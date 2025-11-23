# app/services/revoked_token_service.py
from sqlalchemy.orm import Session
from app.models.security.user_tokens import RevokedToken

class RevokedTokenService:
    @staticmethod
    def revoke_token(db: Session, jti: str) -> RevokedToken:
        revoked = RevokedToken(jti=jti)
        db.add(revoked)
        db.commit()
        db.refresh(revoked)
        return revoked

    @staticmethod
    def is_token_revoked(db: Session, jti: str) -> bool:
        return db.query(RevokedToken).filter(RevokedToken.jti == jti).first() is not None
