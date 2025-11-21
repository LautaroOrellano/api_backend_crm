from sqlalchemy.orm import Session
from fastapi import HTTPException

from typing import Optional

from app.repositories.customer_filter_repository import CustomerFilterRepository
from app.schemas.customer_schema import CustomerCreate, CustomerRead, CustomerQuery
from app.schemas.pagination import Page
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository


class CustomerService:

    # =========================
    # CREATE
    # =========================
    @staticmethod
    def create_customer(db: Session, customer: CustomerCreate) -> CustomerRead:
        # Validación de negocio: email único
        if customer.email:
            if CustomerRepository.get_by_email(db, str(customer.email)):
                raise HTTPException(status_code=400, detail="Email already exists")

        entity = Customer(**customer.model_dump())

        db.add(entity)
        db.commit()
        db.refresh(entity)

        return CustomerRead.model_validate(entity)

    # =========================
    # LIST + FILTROS + PAGINACIÓN + ORDEN
    # =========================
    @staticmethod
    @staticmethod
    def list_customers(db: Session, filters) -> Page[CustomerRead]:

        # Validaciones básicas
        if filters.limit < 1 or filters.limit > 200:
            raise HTTPException(400, "Limit must be between 1 and 200")
        if filters.offset < 0:
            raise HTTPException(400, "Offset must be >= 0")

        allowed_sort_fields = ["id", "full_name", "created_at", "updated_at"]
        if filters.order_by not in allowed_sort_fields:
            raise HTTPException(400, "Invalid order_by field")
        if filters.order_dir not in ["asc", "desc"]:
            raise HTTPException(400, "Invalid order_dir (asc|desc)")

        # FILTROS (repositorio)
        query = CustomerFilterRepository.filter_customers(db, filters)

        # TOTAL ITEMS (sin paginar)
        total_items = query.order_by(None).count()

        # ORDENAMIENTO
        field = getattr(Customer, filters.order_by)
        field = field.desc() if filters.order_dir == "desc" else field.asc()
        query = query.order_by(field)

        # PAGINACIÓN
        items = query.offset(filters.offset).limit(filters.limit).all()

        # ARMAMOS EL DTO DE RESPUESTA
        total_pages = (total_items + filters.limit - 1) // filters.limit

        return Page[CustomerRead](
            items=[CustomerRead.model_validate(c) for c in items],
            total_items=total_items,
            total_pages=total_pages,
            limit=filters.limit,
            offset=filters.offset
        )

    # =========================
    # GET ONE
    # =========================
    @staticmethod
    def get_customer(db: Session, customer_id: int) -> CustomerRead:
        customer = CustomerRepository.get_customer_by_id(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return CustomerRead.model_validate(customer)

    # =========================
    # UPDATE
    # =========================
    @staticmethod
    def update_customer(db: Session, customer_id: int, payload: CustomerCreate) -> CustomerRead:
        customer = CustomerRepository.update_customer(db, customer_id, payload)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return CustomerRead.model_validate(customer)

    # =========================
    # DELETE
    # =========================
    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> bool:
        deleted = CustomerRepository.soft_delete(db, customer_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Customer not found")
        return True
