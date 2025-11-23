# app/routers/auth_router.py
import pytz
from fastapi import APIRouter, Depends, HTTPException, Form, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta, timezone

from app.db.session import get_connection
from app.models.user import User
from app.models.security.user_security_info import UserSecurityInfo
from app.schemas.user_schema import UserMe, Token
from app.services.auth_service import AuthService, TokenError
from app.dependencies.auth import get_current_user, oauth2_scheme
from app.core.security import verify_password
from app.services.two_factor_service import TwoFactorService

router = APIRouter()

# -----------------------------
# Helper para estandarizar la respuesta de tokens
# -----------------------------
def token_response(tokens: dict) -> dict:
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer"
    }

# -----------------------------
# LOGIN
# -----------------------------
@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_connection)
):
    # Buscar usuario
    user: Optional[User] = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    # Obtener o crear security_info
    if not user.security_info:
        user.security_info = UserSecurityInfo(user_id=user.id)
        db.add(user.security_info)
        db.commit()
        db.refresh(user.security_info)
    sec = user.security_info

    # Chequear bloqueo usando el helper del modelo
    sec.check_locked()

    # Validar contraseña
    now = datetime.now(timezone.utc)
    if not verify_password(password, user.hashed_password):
        sec.failed_attempts += 1
        sec.last_failed_at = now

        if sec.failed_attempts >= 5:
            sec.locked_until = now + timedelta(minutes=15)
            sec.failed_attempts = 0

        db.add(sec)
        db.commit()
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    # Resetear intentos fallidos en login exitoso
    sec.failed_attempts = 0
    sec.locked_until = None
    db.add(sec)
    db.commit()

    # Obtener headers y sanitizar
    user_agent = (request.headers.get("user-agent") or "")[:512]
    ip_address = request.client.host[:45]
    device_id = request.headers.get("X-Device-Id")
    if not device_id:
        raise HTTPException(status_code=400, detail="Device ID requerido")

    # Rate limiting
    AuthService.check_rate(ip_address, user.username, device_id=device_id)

    # 2FA (si aplica)
    if getattr(user, "two_factor_enabled", False):
        temp_2fa = TwoFactorService.generate_2fa_code(db, user.id)
        return {
            "2fa_required": True,
            "temp_token": temp_2fa["temp_token"],
            "expires_at": temp_2fa["expires_at"]
        }

    # Crear y persistir tokens
    tokens = AuthService.create_and_persist_tokens(
        db,
        user,
        device_id=device_id,
        user_agent=user_agent,
        ip_address=ip_address
    )

    return token_response(tokens)

# -----------------------------
# LOGOUT
# -----------------------------
@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_connection)
):
    payload = AuthService.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    AuthService.revoke_token_by_jti(db, payload["jti"])
    return {"msg": "Logout exitoso"}

# -----------------------------
# LOGOUT ALL
# -----------------------------
@router.post("/logout-all")
def logout_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_connection)
):
    AuthService.revoke_all_user_tokens(db, current_user.id)
    return {"msg": "Todos los tokens revocados"}

# -----------------------------
# REFRESH TOKEN
# -----------------------------
@router.post("/refresh", response_model=Token)
@router.post("/refresh", response_model=Token)
def refresh_token(
        request: Request,
        refresh_token_str: str = Form(...),
        db: Session = Depends(get_connection),
):
    # 1️⃣ Decodificar refresh token
    payload = AuthService.decode_refresh_token(refresh_token_str)
    if not payload:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 2️⃣ Obtener headers y sanitizar
    device_id = request.headers.get("X-Device-Id")
    if not device_id:
        raise HTTPException(status_code=400, detail="Device ID requerido")

    user_agent = (request.headers.get("user-agent") or "")[:512]
    ip_address = request.client.host[:45]

    # 3️⃣ Rate limiting atómico
    AuthService.check_rate(ip_address, user.username, device_id=device_id)

    # 4️⃣ Rotar refresh token con device binding + reuse detection
    try:
        tokens = AuthService.rotate_refresh(
            db,
            refresh_token_str,
            device_id=device_id,
            user_agent=user_agent,
            ip_address=ip_address
        )
    except TokenError as e:
        raise HTTPException(status_code=401, detail=str(e))

    # 5️⃣ Devolver tokens
    return token_response(tokens)

# -----------------------------
# GET CURRENT USER
# -----------------------------
@router.get("/me", response_model=UserMe)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user
