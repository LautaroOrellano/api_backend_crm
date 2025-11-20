from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from models.customer import CustomerCreate, CustomerDB
from services.customer_service import CustomerService
from db.connection import get_connection

app = FastAPI(title="CustomerManager API")

@app.post("/customers", response_model=CustomerDB)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_connection)):
    return CustomerService.create_customer(db, payload)

@app.get("/customers", response_model=list[CustomerDB])
def list_customers(db: Session = Depends(get_connection)):
    return CustomerService.list_customers(db)

@app.get("/customers/{customer_id}", response_model=CustomerDB)
def get_customer(customer_id: int, db: Session = Depends(get_connection)):
    customer = CustomerService.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.put("/customers/{customer_id}", response_model=CustomerDB)
def update_customer(customer_id: int, payload: CustomerCreate, db: Session = Depends(get_connection)):
    updated_customer = CustomerService.update_customer(db, customer_id, payload)
    if not updated_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated_customer

@app.delete("/customers/{customer_id}", response_model=bool)
def delete_customer(customer_id: int, db: Session = Depends(get_connection)):
    deleted = CustomerService.delete_customer(db, customer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")
    return deleted
