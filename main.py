from fastapi import FastAPI
from app.api.v1.customers import router as customer_router

app = FastAPI(title="Customer Manager API")

# Registrar routers
app.include_router(customer_router, prefix="/customers", tags=["Customers"])

@app.get("/")
def root():
    return {"message": "Customer Manager API running"}
