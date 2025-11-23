from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.db.session import get_connection
from app.models.user import User
from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token
)
from app.core.security import verify_password
from app.dependencies.auth import get_current_user, oauth2_scheme
from app.schemas.user_schema import UserMe, Token
from app.services.revoked_token_service import RevokedTokenService

router = APIRouter()

@router.post("/login", response_model=Token)
def login(username: str = Form(...), password: str = Form(...),
          db: Session = Depends(get_connection)):

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    # Crear tokens
    access_token = create_access_token({
        "sub": user.username,
        "role": user.role
    })

    refresh_token = create_refresh_token({
        "sub": user.username
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_connection)):

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    jti = payload["jti"]
    RevokedTokenService.revoke_token(db, jti)

    return {"msg": "Logged out successfully"}

@router.post("/refresh")
def refresh_token(refresh_token: str = Form(...), db: Session = Depends(get_connection)):

    payload = decode_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    jti = payload["jti"]

    # 1. Revisar si fue revocado
    if RevokedTokenService.is_token_revoked(db, jti):
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    username = payload["sub"]

    # 2. Revocar el refresh usado
    RevokedTokenService.revoke_token(db, jti)

    # 3. Generar nuevo refresh y access
    new_access = create_access_token({"sub": username})
    new_refresh = create_refresh_token({"sub": username})

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserMe)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user
