# app/dependencies/roles.py
from fastapi import Depends, HTTPException, status
from app.dependencies.auth import get_current_user
from app.models.user import User

def role_required(role: str):
    def decorator(current_user: User = Depends(get_current_user)):
        if getattr(current_user, "role", "user") != role:
            raise HTTPException(status_code=403, detail="Permiso denegado")
        return current_user
    return decorator