from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.customer_schema import CustomerCreate, CustomerRead, CustomerQuery
from app.schemas.pagination import Page
from app.services.customer_service import CustomerService
from app.db.session import get_connection
from app.models.user import User
from app.dependencies.roles import role_required
from fastapi import Query

router = APIRouter()

@router.post("/", response_model=CustomerRead)
def create_customer(
        payload: CustomerCreate,
        db: Session = Depends(get_connection),
        current_user: User =  Depends(role_required("admin", "user"))
):
    return CustomerService.create_customer(db, payload, current_user)

@router.get("/count", response_model=int)
def count_customers(
        db: Session = Depends(get_connection),
        current_user: User = Depends(role_required("admin", "user"))
):
    return CustomerService.count_all_customers(db, current_user)

@router.get("/", response_model=Page[CustomerRead])
def list_customers(
    filters: CustomerQuery = Depends(),
    db: Session = Depends(get_connection),
    current_user: User = Depends(role_required("admin", "user"))
):
    return CustomerService.list_customers(db, filters, current_user)

@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(
        customer_id: int,
        db: Session = Depends(get_connection),
        current_user: User = Depends(role_required("admin", "user"))
):
    return CustomerService.get_customer(db, customer_id, current_user)

@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(
        customer_id: int,
        payload: CustomerCreate,
        db: Session = Depends(get_connection),
        current_user: User = Depends(role_required("admin", "user"))
):
    return CustomerService.update_customer(db, customer_id, payload, current_user)

@router.delete("/{customer_id}", response_model=bool)
def delete_customer(
        customer_id: int,
        db: Session = Depends(get_connection),
        current_user: User = Depends(role_required("admin", "user"))
):
    return CustomerService.delete_customer(db, customer_id, current_user)


@router.post("/{customer_id}/reactivate", response_model=CustomerRead)
def reactivate_customer(
        customer_id: int,
        db: Session = Depends(get_connection),
        current_user: User = Depends(role_required("admin", "user"))
):
    return CustomerService.reactivate_customer(db, customer_id, current_user)