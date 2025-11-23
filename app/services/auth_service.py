from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.core.keys import PRIVATE_KEY, PUBLIC_KEYS, KID_CURRENT
from app.core.security import verify_password
import jwt
from redis import Redis
import logging

from app.config import settings
from app.repositories.token_repository import TokenRepository
from app.models.security.user_tokens import TokenType, UserToken, RevokedToken
from app.models.user import User
from app.models.security.user_security_info import UserSecurityInfo

# Logger central
logger = logging.getLogger("auth_service")
logger.setLevel(logging.INFO)

class TokenError(Exception):
    """Excepción específica para errores de tokens (ACCESO/REFRESH)."""
    pass

class AuthService:
    redis_client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def check_rate(ip: str, username: str, device_id: Optional[str] = None, limit: int = 5, ttl: int = 60):
        """Rate limiting atómico por IP + username + device_id usando Redis Lua script."""
        keys = [f"rate:ip:{ip}", f"rate:user:{username}"]
        if device_id:
            keys.append(f"rate:device:{device_id}")

        # Script Lua atómico: incrementa contador y setea TTL solo si es la primera vez
        RATE_LIMIT_LUA = """
        local current
        current = redis.call('INCR', KEYS[1])
        if current == 1 then
            redis.call('EXPIRE', KEYS[1], ARGV[1])
        end
        if current > tonumber(ARGV[2]) then
            return 0
        end
        return current
        """

        exceeded = False
        for key in keys:
            res = AuthService.redis_client.eval(RATE_LIMIT_LUA, 1, key, ttl, limit)
            if res == 0:
                exceeded = True
                logger.warning(f"[RateLimit] Bloqueado {username} desde IP {ip} device {device_id}")

        if exceeded:
            raise TokenError("Demasiados intentos, inténtalo más tarde")

    @staticmethod
    def _generate_token(user: User, token_type: TokenType, expires_delta: timedelta) -> Dict:
        jti = str(uuid4())
        expires = AuthService._now() + expires_delta
        payload = {
            "sub": str(user.id),
            "jti": jti,
            "type": token_type.name,
            "exp": int(expires.timestamp())
        }
        token_str = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256", headers={"kid": KID_CURRENT})
        logger.info(f"[AuthService] Token {token_type.name} creado para usuario {user.id} (jti={jti})")
        return {
            "jti": jti,
            "token": token_str,
            "expires": expires,
            "type": token_type
        }

    @staticmethod
    def _decode_token(token: str, expected_type: TokenType) -> Optional[dict]:
        try:
            headers = jwt.get_unverified_header(token)
            kid = headers.get("kid")
            if not kid or kid not in PUBLIC_KEYS:
                raise TokenError("Clave pública no encontrada para verificación")

            public_key = PUBLIC_KEYS[kid]
            payload = jwt.decode(token, public_key, algorithms=["RS256"])
            if payload.get("type") != expected_type.name:
                raise TokenError(f"Token no es del tipo {expected_type.name}")
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenError("Token expirado")
        except jwt.InvalidTokenError:
            raise TokenError("Token inválido")
        except KeyError:
            return None

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        return AuthService._decode_token(token, TokenType.ACCESS)

    @staticmethod
    def decode_refresh_token(token: str) -> Optional[dict]:
        return AuthService._decode_token(token, TokenType.REFRESH)

    @staticmethod
    def create_and_persist_tokens(
        db: Session,
        user: User,
        device_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, str]:
        access_data = AuthService._generate_token(
            user,
            TokenType.ACCESS,
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_data = AuthService._generate_token(
            user,
            TokenType.REFRESH,
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        TokenRepository.save_token(
            db, access_data["jti"],
            access_data["type"],
            user.id, device_id,
            user_agent, ip_address,
            access_data["expires"]
        )
        TokenRepository.save_token(
            db, refresh_data["jti"],
            refresh_data["type"],
            user.id,
            device_id,
            user_agent,
            ip_address,
            refresh_data["expires"]
        )

        return {
            "access_token": access_data["token"],
            "refresh_token": refresh_data["token"],
            "access_expires_at": access_data["expires"].isoformat(),
            "refresh_expires_at": refresh_data["expires"].isoformat()
        }

    @staticmethod
    def revoke_token_by_jti(
            db: Session,
            jti: str,
            revoked_by: Optional[int] = None,
            reason: Optional[str] = None
    ):
        token_row: Optional[UserToken] = db.query(UserToken).filter(UserToken.jti == jti).first()
        if token_row and not token_row.is_revoked:
            token_row.is_revoked = True
            token_row.revoked_by = revoked_by
            token_row.revoked_reason = reason
            token_row.revoked_at = AuthService._now()
            db.add(token_row)
            db.add(RevokedToken(**token_row.to_revoked_dict(reason)))
            db.commit()
            logger.info(f"[AuthService] Token revocado (jti={jti})")

    @staticmethod
    def revoke_all_user_tokens(db: Session, user_id: int, reason: Optional[str] = None):
        tokens = db.query(UserToken).filter(UserToken.user_id == user_id,
                                            UserToken.token_type == TokenType.REFRESH,
                                            UserToken.is_revoked == False).all()
        for token in tokens:
            token.is_revoked = True
            token.revoked_by = None
            token.revoked_reason = reason
            token.revoked_at = AuthService._now()
            db.add(token)
            db.add(RevokedToken(**token.to_revoked_dict(reason)))
        db.commit()
        logger.info(f"[AuthService] Todos los refresh tokens revocados para usuario {user_id}")

    @staticmethod
    def rotate_refresh(
            db: Session,
            refresh_token_str: str,
            device_id: Optional[str] = None,
            user_agent: Optional[str] = None,
            ip_address: Optional[str] = None
    ) -> Dict[str, str]:
        # 1️⃣ Validar device_id
        if not device_id:
            raise TokenError("Device ID requerido")
        try:
            uuid_obj = uuid4(device_id)  # asegura que sea UUID válido
        except ValueError:
            raise TokenError("Device ID inválido")

        # 2️⃣ Decodificar refresh token
        payload = AuthService.decode_refresh_token(refresh_token_str)
        if not payload:
            raise TokenError("Refresh token inválido o expirado")

        jti = payload["jti"]
        user_id = int(payload["sub"])

        token_row: Optional[UserToken] = db.query(UserToken).filter(UserToken.jti == jti).first()
        if not token_row:
            raise TokenError("Refresh token no encontrado")

        # 3️⃣ Device binding estricto
        if token_row.device_id != device_id:
            logger.warning(
                f"[DeviceBinding] Mismatch detectado: user={user_id} token_device={token_row.device_id} "
                f"request_device={device_id} ip={ip_address}"
            )
            AuthService.revoke_all_user_tokens(db, user_id, reason="device_mismatch_detected")
            raise TokenError("Device mismatch detected")

        # 4️⃣ Reuse detection
        if token_row.is_revoked:
            logger.warning(f"[TokenReuse] Reuse detectado: user={user_id} jti={jti} ip={ip_address}")
            AuthService.revoke_all_user_tokens(db, user_id, reason="reuse_detected")
            raise TokenError("Refresh token reuse detected")

        # 5️⃣ Revocar el token usado
        AuthService.revoke_token_by_jti(db, jti)

        # 6️⃣ Sanitizar user_agent y ip_address
        user_agent = (user_agent or "")[:512]
        ip_address = (ip_address or "")[:45]

        # 7️⃣ Obtener usuario
        user: Optional[User] = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise TokenError("Usuario no encontrado")

        # 8️⃣ Crear y persistir nuevos tokens
        return AuthService.create_and_persist_tokens(
            db,
            user,
            device_id=device_id,
            user_agent=user_agent,
            ip_address=ip_address
        )

    @staticmethod
    def check_user_lock(db: Session, user: User, password: str, limit: int = 5, block_minutes: int = 15):
        """Verifica intentos fallidos y bloqueo temporal de usuario."""
        security_info = db.query(UserSecurityInfo).filter(UserSecurityInfo.user_id == user.id).first()
        if not security_info:
            security_info = UserSecurityInfo(
                user_id=user.id,
                failed_attempts=0,
                locked_until=None,
                last_failed_at=None
            )
            db.add(security_info)
            db.commit()
            db.refresh(security_info)

        now = datetime.now(timezone.utc)
        if security_info.locked_until and security_info.locked_until > now:
            raise TokenError("Usuario bloqueado temporalmente")

        if not verify_password(password, user.hashed_password):
            security_info.failed_attempts += 1
            security_info.last_failed_at = now
            if security_info.failed_attempts >= limit:
                security_info.locked_until = now + timedelta(minutes=block_minutes)
                security_info.failed_attempts = 0
            db.add(security_info)
            db.commit()
            raise TokenError("Usuario o contraseña incorrectos")

        # Login exitoso: resetear contador
        security_info.failed_attempts = 0
        security_info.locked_until = None
        db.add(security_info)
        db.commit()
