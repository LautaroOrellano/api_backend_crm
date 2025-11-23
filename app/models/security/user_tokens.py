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

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, index=True, nullable=False)
    revoked_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))