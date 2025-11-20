# repositories/customer_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.customer_schema import CustomerCreate
from app.models.customer import Customer

class CustomerRepository:

    @staticmethod
    def insert_customer(db: Session, payload: CustomerCreate) -> Customer:
        db_customer = Customer(**payload.dict())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer

    @staticmethod
    def get_all_customers(db: Session) -> List[Customer]:
        return db.query(Customer).order_by(Customer.created_at.desc()).all()

    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.id == customer_id).first()

    @staticmethod
    def update_customer(db: Session, customer_id: int, payload: CustomerCreate) -> Optional[Customer]:
        db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not db_customer:
            return None
        for key, value in payload.dict(exclude_unset=True).items():
            setattr(db_customer, key, value)
        db.commit()
        db.refresh(db_customer)
        return db_customer

    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> bool:
        db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not db_customer:
            return False
        db.delete(db_customer)
        db.commit()
        return True
