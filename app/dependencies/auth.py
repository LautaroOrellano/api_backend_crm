from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_connection
from app.models.user import User
from app.services.revoked_token_service import RevokedTokenService
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_connection)) -> User:
    payload = AuthService.decode_access_token(token)

    print("Payload del token:", payload)  # movemos esto arriba para debug

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    jti = payload.get("jti")
    if RevokedTokenService.is_token_revoked(db, jti):
        raise HTTPException(status_code=401, detail="Token revoked")

    user_id: int = int(payload.get("sub"))  # ⚡ usar ID
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()  # ⚡ filtrar por ID
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

