# app/schemas/user_schema.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, ClassVar
from datetime import datetime

# -----------------------------
# User base (campos comunes)
# -----------------------------
class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr
    full_name: Optional[str] = None

# -----------------------------
# User para creación (input)
# -----------------------------
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

# -----------------------------
# User para lectura (output)
# -----------------------------
class UserRead(UserBase):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str]
    role: str
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[dict] = {"from_attributes": True}

# -----------------------------
# User para login
# -----------------------------
class UserLogin(BaseModel):
    username: str
    password: str

# -----------------------------
# User para swagger
# -----------------------------
class UserMe(BaseModel):
    username: str
    email: str
    full_name: str | None
    is_deleted: bool
    role: str

    class Config:
        orm_mode = True

# -----------------------------
# Token
# -----------------------------
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

# =========================
# QUERY PARAMS (filtros + paginación)
# =========================
class UserQuery(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_deleted: Optional[bool] = None
    q: Optional[str] = None

    # Paginación
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

    # Ordenamiento
    order_by: str = "created_at"  # columnas como created_at, username, email
    order_dir: str = "desc"

    # Filtros por fechas
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    updated_from: Optional[datetime] = None
    updated_to: Optional[datetime] = None