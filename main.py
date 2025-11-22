from fastapi import FastAPI
from app.api.v1.customers import router as customer_router
from app.api.v1.users import router as user_router
from app.api.v1.auth import router as authorization_router
app = FastAPI(title="Customer Manager API")

# Registrar routers
app.include_router(customer_router, prefix="/customers", tags=["Customers"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(authorization_router, prefix="/auth", tags=["auth"])


@app.get("/")
def root():
    return {"message": "Customer Manager API running"}
