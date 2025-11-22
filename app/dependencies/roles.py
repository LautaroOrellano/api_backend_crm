# app/dependencies/roles.py
from fastapi import Depends, HTTPException
from app.dependencies.auth import get_current_user
from app.models.user import User

def role_required(*roles: str):
    """
    Permite que el endpoint sea accedido por uno o más roles.
    Uso: Depends(role_required("admin", "user"))
    """
    def wrapper(current_user: User = Depends(get_current_user)):
        if getattr(current_user, "role", "user") not in roles:
            raise HTTPException(status_code=403, detail="Permiso denegado")
        return current_user
    return wrapper