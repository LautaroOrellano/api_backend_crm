# app/core/jwt.py
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError, ExpiredSignatureError
from app.config import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str):
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "access":
            return None
        return payload
    except (ExpiredSignatureError, JWTError):
        return None


def decode_refresh_token(token: str):
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "refresh":
            return None
        return payload
    except (ExpiredSignatureError, JWTError):
        return None

def get_jti_from_token(token: Optional[str]) -> Optional[str]:
    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload.get("jti")
    except (ExpiredSignatureError, JWTError):
        return None
