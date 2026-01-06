from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.customers import router as customer_router
from app.api.v1.users import router as user_router
from app.api.v1.auth import router as authorization_router

app = FastAPI(title="Customer Manager API")

# -----------------------------
# 🚀 CORS CONFIG (SOLUCIÓN AL 405)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# 🔗 Rutas
# -----------------------------
app.include_router(customer_router, prefix="/customers", tags=["Customers"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(authorization_router, prefix="/auth", tags=["auth"])

@app.get("/")
def root():
    return {"message": "Customer Manager API running"}
