# app/service/user_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.user_filter_repository import UserFilterRepository
from app.schemas.pagination import Page
from app.schemas.user_schema import UserCreate, UserRead
from app.core.security import get_password_hash
from datetime import datetime, timezone


class UserService:

    # =========================
    # CREATE
    # =========================
    @staticmethod
    def create_user(db: Session, payload: UserCreate, current_user: User) -> UserRead:
        if payload.email and UserRepository.get_by_email(db, str(payload.email)):
            raise HTTPException(status_code=400, detail="Email already exists")

        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="You do not have permission to create users")

        data = payload.model_dump()
        data["hashed_password"] = get_password_hash(data.pop("password"))

        entity = User(**data, created_by=current_user.id, updated_by=current_user.id)

        user = UserRepository.insert_user(db, entity)

        return UserRead.model_validate(user)

    # =========================
    # LIST + FILTROS + PAGINACIÓN + ORDEN
    # =========================
    @staticmethod
    def list_users(db: Session, filters, current_user: User) -> Page[UserRead]:

        # Validaciones básicas
        if filters.limit < 1 or filters.limit > 200:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 200")
        if filters.offset < 0:
            raise HTTPException(400, "Offset must be >= 0")

        allowed_sort_fields = ["id", "full_name", "created_at", "updated_at"]
        if filters.order_by not in allowed_sort_fields:
            raise HTTPException(400, "Invalid order_by field")
        if filters.order_dir not in ["asc", "desc"]:
            raise HTTPException(400, "Invalid order_dir (asc|desc)")

        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="You do not have permission to view this users")

        # Filtros (repositorio)
        query = UserFilterRepository.filter_users(db, filters)

        # TOTAL ITEMS (sin paginar)
        total_items = query.order_by(None).count()

        # ORDENAMIENTO
        field = getattr(User, filters.order_by)
        field = field.desc() if filters.order_dir == "desc" else field.asc()
        query = query.order_by(field)

        # PAGINACIÓN
        items = query.offset(filters.offset).limit(filters.limit).all()

        # ARMAMOS EL DTO DE RESPUESTA
        total_pages = (total_items + filters.limit - 1) // filters.limit

        return Page[UserRead](
            items=[UserRead.model_validate(c) for c in items],
            total_items=total_items,
            total_pages=total_pages,
            limit=filters.limit,
            offset=filters.offset
        )

    # =========================
    # GET ONE
    # =========================
    @staticmethod
    def get_user(db: Session, user_id: int, current_user: User) -> UserRead:
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="You do not have permission to view this user")

        return UserRead.model_validate(user)

    # =========================
    # UPDATE
    # =========================
    @staticmethod
    def update_user(db: Session, user_id: int, payload: UserCreate, current_user: User) -> UserRead:
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="You do not have permission to update this user")

        data = payload.model_dump(exclude_unset=True)
        if "password" in data:
            user.hashed_password = get_password_hash(data.pop("password"))

        for key, value in data.items():
            setattr(user, key, value)

        user.updated_by = current_user.id

        updated = UserRepository.update_user(db, user)
        return UserRead.model_validate(updated)

    # =========================
    # DELETE
    # =========================
    @staticmethod
    def delete_user(db: Session, user_id: int, current_user: User) -> bool:
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="You do not have permission to delete this user")

        user.deleted_by = current_user.id
        user.deleted_at = datetime.now(timezone.utc)

        UserRepository.soft_delete(db, user)

        return True

    # =========================
    # REACTIVE
    # =========================
    @staticmethod
    def reactivate_user(db: Session, user_id: int, current_user: User) -> UserRead:
        user = UserRepository.get_user_by_id_for_reactivation(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="You do not have permission to update this user")

        user = UserRepository.reactivate_user(db, user)
        return UserRead.model_validate(user)