from sqlalchemy.orm import Session
from models.customer import CustomerCreate, CustomerDB
from repositories.customer_repository import CustomerRepository
from fastapi import HTTPException
from typing import List

class CustomerService:

    @staticmethod
    def create_customer(db: Session, payload: CustomerCreate) -> CustomerDB:
        customer = CustomerRepository.insert_customer(db, payload)
        return CustomerDB.model_validate(customer)

    @staticmethod
    def list_customers(db: Session) -> List[CustomerDB]:
        customers = CustomerRepository.get_all_customers(db)
        return [CustomerDB.model_validate(c) for c in customers]

    @staticmethod
    def get_customer(db: Session, customer_id: int) -> CustomerDB:
        customer = CustomerRepository.get_customer_by_id(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return CustomerDB.model_validate(customer)

    @staticmethod
    def update_customer(db: Session, customer_id: int, payload: CustomerCreate) -> CustomerDB:
        customer = CustomerRepository.update_customer(db, customer_id, payload)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return CustomerDB.model_validate(customer)

    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> bool:
        deleted = CustomerRepository.delete_customer(db, customer_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Customer not found")
        return True
