from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.security.user_tokens import UserToken, RevokedToken, TokenType

class TokenRepository:

    @staticmethod
    def save_token(
        db: Session,
        jti: str,
        token_type: TokenType | str,
        user_id: int,
        device_id: Optional[str],
        user_agent: Optional[str],
        ip_address: Optional[str],
        expires_at: datetime
    ) -> UserToken:
        """Guarda un token en la DB, asegurando que token_type sea Enum."""
        if isinstance(token_type, str):
            token_type = TokenType[token_type.upper()]

        token = UserToken(
            jti=jti,
            token_type=token_type,
            user_id=user_id,
            device_id=device_id,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at,
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        return token

    @staticmethod
    def get_by_jti(db: Session, jti: str) -> Optional[UserToken]:
        return db.query(UserToken).filter(UserToken.jti == jti).first()

    @staticmethod
    def revoke_by_jti(
        db: Session,
        jti: str,
        revoked_by: Optional[int] = None,
        reason: Optional[str] = None
    ) -> bool:
        """Revoca un token específico y crea un registro de auditoría."""
        token = db.query(UserToken).filter(UserToken.jti == jti).first()
        now = datetime.now(timezone.utc)

        revoked = False
        if token and not token.is_revoked:
            token.is_revoked = True
            token.revoked_by = revoked_by
            token.revoked_reason = reason
            token.revoked_at = now
            db.add(token)
            revoked = True

        # siempre registrar auditoría con el valor correcto
        db.add(RevokedToken(jti=jti, revoked_at=now))
        db.commit()
        return revoked

    @staticmethod
    def revoke_all_user_refresh(
        db: Session,
        user_id: int,
        revoked_by: Optional[int] = None,
        reason: Optional[str] = None
    ) -> int:
        """Revoca todos los refresh tokens de un usuario y crea auditorías."""
        tokens = db.query(UserToken).filter(
            UserToken.user_id == user_id,
            UserToken.token_type == TokenType.REFRESH,
            UserToken.is_revoked == False
        ).all()  # type: ignore

        now = datetime.now(timezone.utc)
        for token in tokens:
            token.is_revoked = True
            token.revoked_by = revoked_by
            token.revoked_reason = reason
            token.revoked_at = now
            db.add(token)
            db.add(RevokedToken(jti=token.jti, revoked_at=now))

        db.commit()
        return len(tokens)

    @staticmethod
    def list_user_sessions(db: Session, user_id: int) -> List[UserToken]:
        return db.query(UserToken).filter(UserToken.user_id == user_id)\
                 .order_by(UserToken.created_at.desc()).all()  # type: ignore
