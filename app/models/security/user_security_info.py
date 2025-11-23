import pytz
from fastapi import HTTPException
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

class UserSecurityInfo(Base):
    __tablename__ = "user_security_info"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    failed_attempts = Column(Integer, default=0)
    last_failed_at = Column(DateTime(timezone=True), nullable=True)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="security_info")

    # -----------------------------
    # Helper para revisar bloqueo
    # -----------------------------
    def check_locked(self):
        now = datetime.now(timezone.utc)

        if self.locked_until:
            # Convertir a timezone-aware si viniera naive
            locked_until_aware = (
                self.locked_until.replace(tzinfo=timezone.utc)
                if self.locked_until.tzinfo is None
                else self.locked_until
            )
            if locked_until_aware > now:
                # Mostrar hora local
                local_time = locked_until_aware.astimezone( pytz.timezone("America/Argentina/Buenos_Aires"))
                raise HTTPException(
                    status_code=403,
                    detail=f"Usuario bloqueado hasta {local_time.isoformat()}"
                )
