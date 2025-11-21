# app/repositories/customer_filter_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from datetime import datetime

from app.models.customer import Customer
from app.schemas.customer_schema import CustomerQuery

class CustomerFilterRepository:

    @staticmethod
    def filter_customers(db: Session, filters: CustomerQuery):
        query = db.query(Customer).filter(Customer.is_deleted == False)

        # Filtros básicos
        if filters.email:
            query = query.filter(Customer.email.ilike(f"%{filters.email}%"))
        if filters.phone:
            query = query.filter(Customer.phone.ilike(f"%{filters.phone}%"))
        if filters.source:
            query = query.filter(Customer.source == filters.source)
        if filters.status:
            query = query.filter(Customer.status == filters.status)

        # Búsqueda general
        if filters.q:
            q_like = f"%{filters.q}%"
            query = query.filter(
                or_(
                    Customer.full_name.ilike(q_like),
                    Customer.email.ilike(q_like),
                    Customer.phone.ilike(q_like)
                )
            )

        # Filtros avanzados (ejemplos)
        if getattr(filters, "created_from", None):
            query = query.filter(Customer.created_at >= filters.created_from)
        if getattr(filters, "created_to", None):
            query = query.filter(Customer.created_at <= filters.created_to)

        return query