import re
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
        v = v.strip().title()
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]+", v):
            raise ValueError("Full name must contain only letters and spaces")
        return v

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

    @field_validator("status")
    def validate_status(cls, v):
        allowed_status = [s.value for s in LeadStatus]
        if v.value not in allowed_status:
            raise ValueError(f"Status must be one of {allowed_status}")
        return v

# =========================
# OUTPUT (para devolver al cliente)
# =========================
class CustomerRead(BaseModel):
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

# =========================
# QUERY PARAMS (filtros + paginación)
# =========================
class CustomerQuery(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    q: Optional[str] = None

    # Paginación
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

    # Ordenamiento
    order_by: str = "created_at"
    order_dir: str = "desc"

    # Filtros avanzados
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    updated_from: Optional[datetime] = None
    updated_to: Optional[datetime] = None