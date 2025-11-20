from sqlalchemy.orm import Session
from app.schemas.customer_schema import CustomerCreate, CustomerRead
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from fastapi import HTTPException
from typing import List

class CustomerService:
    @staticmethod
    def create_customer(db: Session, customer: CustomerCreate) -> CustomerRead:
        # Validación de negocio: email único
        if customer.email:
            existing = db.query(Customer).filter(Customer.email == customer.email).first()
            if existing:
                raise ValueError("Customer with this email already exists")

        customer_db = Customer(**customer.model_dump())
        db.add(customer_db)
        db.commit()
        db.refresh(customer_db)
        return customer_db

    @staticmethod
    def list_customers(db: Session) -> List[CustomerRead]:
        customers = CustomerRepository.get_all_customers(db)
        return [CustomerRead.model_validate(c) for c in customers]

    @staticmethod
    def get_customer(db: Session, customer_id: int) -> CustomerRead:
        customer = CustomerRepository.get_customer_by_id(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return CustomerRead.model_validate(customer)

    @staticmethod
    def update_customer(db: Session, customer_id: int, payload: CustomerCreate) -> CustomerRead:
        customer = CustomerRepository.update_customer(db, customer_id, payload)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return CustomerRead.model_validate(customer)

    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> bool:
        deleted = CustomerRepository.delete_customer(db, customer_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Customer not found")
        return True
