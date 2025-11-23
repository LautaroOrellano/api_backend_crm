from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Optional, Dict
import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.repositories.token_repository import TokenRepository
from app.models.security.user_tokens import TokenType, UserToken
from app.models.user import User


class TokenError(Exception):
    """Excepción específica para errores de tokens (ACCESO/REFRESH)."""
    pass


class AuthService:

    @staticmethod
    def _now() -> datetime:
        """Devuelve la hora actual en UTC."""
        return datetime.now(timezone.utc)

    @staticmethod
    def _generate_token(user: User, token_type: TokenType, expires_delta: timedelta) -> Dict:
        """Genera un token JWT y devuelve un dict con jti, token, expiración y tipo Enum."""
        jti = str(uuid4())
        expires = AuthService._now() + expires_delta
        payload = {
            "sub": str(user.id),
            "jti": jti,
            "type": token_type.name,  # ACCESS / REFRESH
            "exp": int(expires.timestamp())
        }
        token_str = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        # Log de creación de token
        print(f"[AuthService] Token {token_type.name} creado para usuario {user.id} (jti={jti})")

        return {
            "jti": jti,
            "token": token_str,
            "expires": expires,
            "type": token_type
        }

    @staticmethod
    def create_and_persist_tokens(
        db: Session,
        user: User,
        device_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, str]:
        """Genera y guarda tokens ACCESS y REFRESH en la base de datos."""
        access_data = AuthService._generate_token(
            user=user,
            token_type=TokenType.ACCESS,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_data = AuthService._generate_token(
            user=user,
            token_type=TokenType.REFRESH,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        # Guardar en DB
        TokenRepository.save_token(
            db=db,
            jti=access_data["jti"],
            token_type=access_data["type"],
            user_id=user.id,
            device_id=device_id,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=access_data["expires"]
        )
        TokenRepository.save_token(
            db=db,
            jti=refresh_data["jti"],
            token_type=refresh_data["type"],
            user_id=user.id,
            device_id=device_id,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=refresh_data["expires"]
        )

        return {
            "access_token": access_data["token"],
            "refresh_token": refresh_data["token"],
            "access_expires_at": access_data["expires"],
            "refresh_expires_at": refresh_data["expires"]
        }

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """Decodifica un token ACCESS y retorna el payload si es válido."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != TokenType.ACCESS.name:
                return None
            return payload
        except jwt.PyJWTError:
            return None

    @staticmethod
    def decode_refresh_token(token: str) -> Optional[dict]:
        """Decodifica un token REFRESH y retorna el payload si es válido."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != TokenType.REFRESH.name:
                return None
            return payload
        except jwt.PyJWTError:
            return None

    @staticmethod
    def revoke_token_by_jti(db: Session, jti: str, revoked_by: Optional[int] = None, reason: Optional[str] = None):
        """Revoca cualquier token por su JTI."""
        TokenRepository.revoke_by_jti(db, jti, revoked_by=revoked_by, reason=reason)
        print(f"[AuthService] Token revocado (jti={jti})")

    @staticmethod
    def revoke_all_user_tokens(db: Session, user_id: int, reason: Optional[str] = None):
        """Revoca todos los refresh tokens de un usuario."""
        TokenRepository.revoke_all_user_refresh(db, user_id, reason=reason)
        print(f"[AuthService] Todos los refresh tokens revocados para usuario {user_id}")

    @staticmethod
    def rotate_refresh(
            db: Session,
            refresh_token_str: str,
            device_id: Optional[str] = None,
            user_agent: Optional[str] = None,
            ip_address: Optional[str] = None
    ) -> Dict[str, str]:
        """Valida un refresh token, lo revoca y crea nuevos tokens ACCESS y REFRESH."""
        payload = AuthService.decode_refresh_token(refresh_token_str)
        if not payload:
            raise TokenError("Refresh token inválido o expirado")

        jti = payload["jti"]
        user_id = int(payload["sub"])

        # Buscar el token en DB
        token_row: Optional[UserToken] = db.query(UserToken).filter(UserToken.jti == jti).first()
        if not token_row:
            raise TokenError("Refresh token no encontrado")

        # -------------------------------
        # Device Binding: validamos que coincida el device_id
        # -------------------------------
        # Device Binding: obligamos device_id
        if not device_id or token_row.device_id != device_id:
            AuthService.revoke_all_user_tokens(db, user_id, reason="device_mismatch_detected")
            raise TokenError("Device mismatch detected")

        # -------------------------------
        # Reuse detection (si ya estaba revocado)
        # -------------------------------
        if token_row.is_revoked:
            AuthService.revoke_all_user_tokens(db, user_id, reason="reuse_detected")
            raise TokenError("Refresh token reuse detected")

        # Revocamos el refresh token usado
        AuthService.revoke_token_by_jti(db, jti)

        # Obtener usuario
        user: Optional[User] = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise TokenError("Usuario no encontrado")

        # Crear nuevos tokens
        return AuthService.create_and_persist_tokens(
            db, user, device_id=device_id, user_agent=user_agent, ip_address=ip_address
        )
