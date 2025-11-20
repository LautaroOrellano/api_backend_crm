# ingestion/manual_ingestor.py
from models.customer import CustomerCreate
from services.customer_service import CustomerService

def ingest_manual(data: dict):
    """
    Example: data = {
        "full_name": "Lautaro",
        "email": "lautaro@mail.com",
        "phone": "1133445566",
        "source": "manual",
        "notes": "VIP"
    }
    """
    payload = CustomerCreate(**data)
    new_id = CustomerService.create_customer(payload)
    return new_id
