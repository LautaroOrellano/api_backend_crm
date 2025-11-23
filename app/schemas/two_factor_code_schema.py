from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TwoFactorCodeCreate(BaseModel):
    user_id: int
    code: str
    purpose: str
    expires_at: datetime

class TwoFactorCodeVerify(BaseModel):
    user_id: int
    code: str
    purpose: str

class TwoFactorCodeOut(BaseModel):
    id: int
    user_id: int
    code: str
    purpose: str
    expires_at: datetime
    used: bool
    created_at: datetime

    class Config:
        orm_mode = True
