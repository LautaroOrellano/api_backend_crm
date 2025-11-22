from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserRead, UserQuery
from app.schemas.pagination import Page
from app.services.user_service import UserService
from app.db.session import get_connection
from app.models.user import User
from app.dependencies.roles import role_required

router = APIRouter()

@router.post("/", response_model=UserRead)
def create_user(
        payload: UserCreate,
        db: Session = Depends(get_connection),
        current_user: User =  Depends(role_required("admin"))
):
    return UserService.create_user(db, payload, current_user)

@router.get("/", response_model=Page[UserRead])
def list_user(
    filters: UserQuery = Depends(),
    db: Session = Depends(get_connection),
    current_user: User = Depends(role_required("admin"))
):
    return UserService.list_users(db, filters, current_user)

@router.get("/{user_id}", response_model=UserRead)
def get_user(
        user_id: int,
        db: Session = Depends(get_connection),
        current_user: User = Depends(role_required("admin"))
):
    return UserService.get_user(db, user_id, current_user)

@router.put("/{user_id}", response_model=UserRead)
def update_user(
        user_id: int,
        payload: UserCreate,
        db: Session = Depends(get_connection),
        current_user: User = Depends(role_required("admin"))
):
    return UserService.update_user(db, user_id, payload, current_user)

@router.delete("/{user_id}", response_model=bool)
def delete_user(
        user_id: int,
        db: Session = Depends(get_connection),
        current_user: User = Depends(role_required("admin"))
):
    return UserService.delete_user(db, user_id, current_user)

@router.post("/{user_id}/reactivate", response_model=UserRead)
def reactivate_user(
       user_id: int,
        db: Session = Depends(get_connection),
        current_user: User = Depends(role_required("admin"))
):
    return UserService.reactivate_user(db, user_id, current_user)