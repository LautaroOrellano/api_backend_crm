# app/service/customer_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone
from app.repositories.customer_filter_repository import CustomerFilterRepository
from app.schemas.customer_schema import CustomerCreate, CustomerRead
from app.schemas.pagination import Page
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.models.user import User

class CustomerService:

    # =========================
    # CREATE
    # =========================
    @staticmethod
    def create_customer(db: Session, payload: CustomerCreate, user: User) -> CustomerRead:
        # Validación de negocio: email único
        if payload.email and CustomerRepository.get_by_email(db, str(payload.email)):
                raise HTTPException(status_code=400, detail="Email already exists")

        entity = Customer(
            **payload.model_dump(),
            created_by=user.id,
            updated_by=user.id
        )

        customer = CustomerRepository.insert_customer(db, entity)

        return CustomerRead.model_validate(customer)

    # =========================
    # LIST + FILTROS + PAGINACIÓN + ORDEN
    # =========================
    @staticmethod
    def list_customers(db: Session, filters, user: User) -> Page[CustomerRead]:

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

        # FILTRO: solo los clientes del usuario actual
        if user.role != "admin":
            query = query.filter(Customer.created_by == user.id)

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
    def get_customer(db: Session, customer_id: int, user: User) -> CustomerRead:
        customer = CustomerRepository.get_customer_by_id(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        if user.role != "admin" and customer.created_by != user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to view this customer")

        return CustomerRead.model_validate(customer)

    # =========================
    # UPDATE
    # =========================
    @staticmethod
    def update_customer(db: Session, customer_id: int, payload: CustomerCreate, user: User) -> CustomerRead:
        customer = CustomerRepository.get_customer_by_id(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(customer, key, value)

        customer.updated_by = user.id

        updated = CustomerRepository.update_customer(db, customer)

        return CustomerRead.model_validate(updated)

    # =========================
    # DELETE
    # =========================
    @staticmethod
    def delete_customer(db: Session, customer_id: int, user: User) -> bool:
        customer = CustomerRepository.get_customer_by_id(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        customer.deleted_by = user.id
        customer.deleted_at = datetime.now(timezone.utc)

        CustomerRepository.soft_delete(db, customer)

        return True

    # =========================
    # REACTIVE
    # =========================
    @staticmethod
    def reactivate_customer(db: Session, customer_id: int, user: User) -> CustomerRead:
        customer = CustomerRepository.get_customer_by_id_for_reactivation(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Only admin can reactivate customers")

        customer = CustomerRepository.reactivate_customer(db, customer)
        return CustomerRead.model_validate(customer)