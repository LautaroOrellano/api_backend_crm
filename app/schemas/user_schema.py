# app/schemas/user_schema.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
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
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

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
    is_active: bool

    class Config:
        orm_mode = True
