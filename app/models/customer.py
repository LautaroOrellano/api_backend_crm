# app/models/customer.py
from datetime import datetime, timezone
from sqlalchemy import Column, Boolean, Integer, String, DateTime, JSON, Enum as SAEnum, ForeignKey
from app.db.base import Base
from app.enums.lead_status import LeadStatus
from app.enums.lead_source import LeadSource

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    phone = Column(String(30), nullable=True)

    source = Column(SAEnum(LeadSource), nullable=False, default=LeadSource.MANUAL)
    status = Column(SAEnum(LeadStatus), nullable=False, default=LeadStatus.NEW)

    notes = Column(String(255), nullable=True)
    tags = Column(JSON, default=list)

    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Auditoría
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
