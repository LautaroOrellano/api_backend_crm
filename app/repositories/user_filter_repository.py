# app/repositories/user_filter_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User
from app.schemas.user_schema import UserQuery

class UserFilterRepository:

    @staticmethod
    def filter_users(db: Session, filters: UserQuery):
        query = db.query(User).filter(User.is_deleted == False)

        # Filtros básicos
        if filters.username:
            query = query.filter(User.username.ilike(f"%{filters.username}%"))
        if filters.email:
            query = query.filter(User.email.ilike(f"%{filters.email}%"))
        if filters.full_name:
            query = query.filter(User.full_name.ilike(f"%{filters.full_name}%"))
        if filters.role:
            query = query.filter(User.role == filters.role)

        # Búsqueda general
        if filters.q:
            q_like = f"%{filters.q}%"
            query = query.filter(
                or_(
                    User.full_name.ilike(q_like),
                    User.email.ilike(q_like),
                    User.phone.ilike(q_like)
                )
            )

        # Filtros avanzados (ejemplos)
        if getattr(filters, "created_from", None):
            query = query.filter(User.created_at >= filters.created_from)
        if getattr(filters, "created_to", None):
            query = query.filter(User.created_at <= filters.created_to)

        return query