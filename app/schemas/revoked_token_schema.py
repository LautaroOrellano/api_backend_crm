from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RevokedTokenSchema(BaseModel):
    jti: str
    user_id: Optional[int]
    revoked_by: Optional[int]
    revoked_reason: Optional[str]
    device_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    revoked_at: datetime
