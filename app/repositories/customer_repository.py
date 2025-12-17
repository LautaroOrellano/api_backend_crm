# repositories/customer_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.customer import Customer
from app.enums.lead_status import LeadStatus

class CustomerRepository:

    @staticmethod
    def insert_customer(db: Session, entity: Customer) -> Customer:
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

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
    def get_customer_by_id_for_reactivation(db: Session, customer_id: int) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.id == customer_id).first()

    @staticmethod
    def update_customer(db: Session, customer: Customer) -> Customer:
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def soft_delete(db: Session, customer: Customer) -> None:
        customer.is_deleted = True
        db.commit()

    @staticmethod
    def reactivate_customer(db: Session, customer: Customer) -> Customer:
        customer.is_deleted = False
        customer.deleted_at = None
        customer.deleted_by = None
        db.commit()
        db.refresh(customer)
        return customer



    @staticmethod
    def count_all_customers(db: Session, user_id: int = None, is_admin: bool = False) -> int:
        query = CustomerRepository.base_query(db)  # ya filtra is_deleted == False

        # Si no es admin, solo los del usuario
        if not is_admin and user_id:
            query = query.filter(Customer.created_by == user_id)

        return query.count()

