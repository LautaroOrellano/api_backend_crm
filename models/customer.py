# models/customer.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# =========================
# Modelo ORM para la DB
# =========================
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    phone = Column(String(30), nullable=True)
    source = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# =========================
# Modelos Pydantic
# =========================

# Para creación o update (input)
class CustomerCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    source: Optional[str] = None

# Para salida (respuesta)
class CustomerDB(BaseModel):
    id: int
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
