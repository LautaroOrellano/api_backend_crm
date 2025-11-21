from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.customer_schema import CustomerCreate, CustomerRead, CustomerQuery
from app.schemas.pagination import Page
from app.services.customer_service import CustomerService
from app.db.session import get_connection

router = APIRouter()

@router.post("/", response_model=CustomerRead)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_connection)):
    return CustomerService.create_customer(db, payload)

@router.get("/", response_model=Page[CustomerRead])
def list_customers(
    filters: CustomerQuery = Depends(),
    db: Session = Depends(get_connection)
):
    return CustomerService.list_customers(db, filters)

@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, db: Session = Depends(get_connection)):
    customer = CustomerService.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(customer_id: int, payload: CustomerCreate, db: Session = Depends(get_connection)):
    updated_customer = CustomerService.update_customer(db, customer_id, payload)
    if not updated_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated_customer

@router.delete("/{customer_id}", response_model=bool)
def delete_customer(customer_id: int, db: Session = Depends(get_connection)):
    deleted = CustomerService.delete_customer(db, customer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")
    return deleted
