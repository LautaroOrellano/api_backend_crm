from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.enums.lead_status import LeadStatus
from app.enums.lead_source import LeadSource

# =========================
# INPUT (para crear o actualizar)
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
# OUTPUT (para devolver al cliente)
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
