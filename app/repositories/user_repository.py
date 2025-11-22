# repositories/user_repository.py
from typing import List, Optional

from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:

    @staticmethod
    def insert_user(db: Session, entity: User) -> User:
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def base_query(db: Session):
        return db.query(User).filter(User.is_deleted == False)

    @staticmethod
    def get_all_user(db: Session) -> List[User]:
        return UserRepository.base_query(db).order_by(User.created_at.desc()).all()

    @staticmethod
    def get_by_email(db: Session, email: str):
        return UserRepository.base_query(db).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return UserRepository.base_query(db).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_id_for_reactivation(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def update_user(db: Session, user: User) -> User:
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def soft_delete(db: Session, user: User) -> None:
        user.is_deleted = True
        db.commit()

    @staticmethod
    def reactivate_user(db: Session, user: User) -> User:
        user.is_deleted = False
        user.deleted_at = None
        user.deleted_by = None
        db.commit()
        db.refresh(user)
        return user