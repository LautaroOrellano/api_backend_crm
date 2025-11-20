from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum as SAEnum

from app.enums.lead_status import LeadStatus
from app.enums.lead_source import LeadSource
from app.db.base import Base



# =========================
# MODELO ORM
# =========================

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

# =========================
# Pydantic INPUT
# =========================

class CustomerCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    source: Optional[LeadSource] = LeadSource.MANUAL
    status: LeadStatus = LeadStatus.NEW
    notes: Optional[str] = None
    tags: List[str] = []

    @field_validator("full_name")
    def validate_name(cls, v):
        return v.strip().title()

    @field_validator("phone")
    def validate_phone(cls, v):
        if v is None:
            return v
        digits = ''.join(filter(str.isdigit, v))
        if len(digits) < 8:
            raise ValueError("Phone number too short")
        return digits

    @field_validator("tags", mode="before")
    def normalize_tags(cls, v):
        if not v:
            return []
        return [t.strip().lower() for t in v]

# =========================
# Pydantic OUTPUT
# =========================

class CustomerDB(BaseModel):
    id: int
    full_name: str
    email: Optional[EmailStr]
    phone: Optional[str]
    source: LeadSource
    status: LeadStatus
    notes: Optional[str]
    tags: List[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}
