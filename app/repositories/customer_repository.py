# repositories/customer_repository.py
from datetime import datetime

from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas.customer_schema import CustomerCreate
from app.models.customer import Customer

class CustomerRepository:

    @staticmethod
    def insert_customer(db: Session, payload: CustomerCreate) -> Customer:
        db_customer = Customer(**payload.model_dump())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer

    @staticmethod
    def base_query(db: Session):
        return db.query(Customer).filter(Customer.is_deleted == False)

    @staticmethod
    def get_all_customers(db: Session) -> List[Customer]:
        return CustomerRepository.base_query(db).order_by(Customer.created_at.desc()).all()

    @staticmethod
    def get_by_email(db: Session, email: str):
        return CustomerRepository.base_query(db).filter(Customer.email == email).first()

    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int) -> Optional[Customer]:
        return CustomerRepository.base_query(db).filter(Customer.id == customer_id).first()

    @staticmethod
    def update_customer(
            db: Session,
            customer_id: int,
            payload: CustomerCreate
    ) -> Optional[Customer]:
        db_customer: Optional[Customer] = db.query(Customer).filter(Customer.id == customer_id).first()
        if not db_customer:
            return None

        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(db_customer, key, value)

        db.commit()
        db.refresh(db_customer)

        return db_customer

    @staticmethod
    def soft_delete(db: Session, customer_id: int) -> bool:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return False
        customer.is_deleted = True
        customer.deleted_at = datetime.now()
        db.commit()
        return True

