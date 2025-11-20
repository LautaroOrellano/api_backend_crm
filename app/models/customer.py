# app/models/customer.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum as SAEnum
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

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)