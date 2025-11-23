# app/models/security/user_tokens.by
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class TokenType(str, enum.Enum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"


class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True, index=True)

    # Identificador único del token (JTI)
    jti = Column(String(255), nullable=False, unique=True, index=True)

    # access / refresh
    token_type = Column(Enum(TokenType), nullable=False)

    # A quién pertenece esta sesión/token
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", foreign_keys=[user_id])

    # Metadata de sesión
    device_id = Column(String(255), nullable=True)
    user_agent = Column(String(1024), nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Estado de revocación
    is_revoked = Column(Boolean, default=False, nullable=False)
    revoked_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    revoked_by_user = relationship("User", foreign_keys=[revoked_by])
    revoked_reason = Column(String(255), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True, default=datetime.now(timezone.utc))

    # Auditoría
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
    )

    # Expiración real del token
    expires_at = Column(DateTime(timezone=True), nullable=False)

    def is_expired(self) -> bool:
        """Devuelve True si el token ya expiró."""
        return datetime.now(timezone.utc) >= self.expires_at

    def to_revoked_dict(self, reason: str | None = None) -> dict:
        """Devuelve un dict listo para usar en RevokedToken, con valores seguros para MyPy."""
        now = datetime.now(timezone.utc)
        return {
            "jti": str(self.jti),
            "user_id": int(self.user_id) if self.user_id is not None else None,
            "revoked_by": int(self.revoked_by) if self.revoked_by is not None else None,
            "revoked_reason": reason or self.revoked_reason,
            "device_id": self.device_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "revoked_at": now
        }

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=False, index=True, nullable=False)
    user_id = Column(Integer, nullable=True)
    revoked_by = Column(Integer, nullable=True)
    revoked_reason = Column(String, nullable=True)
    device_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    revoked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))