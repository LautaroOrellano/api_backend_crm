from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.security.two_factor_codes import TwoFactorCode

class TwoFactorCodeRepository:

    @staticmethod
    def create_code(db: Session, user_id: int, code: str, purpose: str, expires_at: datetime):
        db_code = TwoFactorCode(
            user_id=user_id,
            code=code,
            purpose=purpose,
            expires_at=expires_at,
            used=False
        )
        db.add(db_code)
        db.commit()
        db.refresh(db_code)
        return db_code

    @staticmethod
    def get_active_code(db: Session, user_id: int, code: str, purpose: str):
        now = datetime.now(timezone.utc)
        return db.query(TwoFactorCode).filter(
            TwoFactorCode.user_id == user_id,
            TwoFactorCode.code == code,
            TwoFactorCode.purpose == purpose,
            TwoFactorCode.used == False,
            TwoFactorCode.expires_at > now
        ).first()

    @staticmethod
    def mark_as_used(db: Session, code_id: int):
        code = db.query(TwoFactorCode).filter(TwoFactorCode.id == code_id).first()
        if code:
            code.used = True
            db.add(code)
            db.commit()
        return code