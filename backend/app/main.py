from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.exceptions import DomainError

# Import all models để SQLAlchemy nhận biết
from app.models import *  # noqa: F403

# Import routers mới
from app.features.admin_auth.router import router as admin_auth_router
from app.features.billing_new.router import router as billing_router
from app.features.customer_auth.router import router as customer_auth_router
from app.features.customer_invoices.router import router as customer_invoices_router
from app.features.households.router import router as households_router
from app.features.meter_readings_new.router import router as meter_readings_router
from app.features.price_tiers.router import router as price_tiers_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Hệ thống tính tiền điện",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount static files (frontend) - MUST be after middleware and before route handlers
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")
app.mount("/admin", StaticFiles(directory="../frontend/static/pages/admin", html=True), name="admin")
app.mount("/customer", StaticFiles(directory="../frontend/static/pages/customer", html=True), name="customer")
app.mount("/auth", StaticFiles(directory="../frontend/static/pages/auth", html=True), name="auth")

@app.exception_handler(DomainError)
async def domain_error_handler(_, exc: DomainError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Dữ liệu gửi lên không hợp lệ.",
            "details": exc.errors()
        }
    )


@app.get("/", include_in_schema=False)
async def root():
    from fastapi.responses import FileResponse
    return FileResponse("../frontend/static/index.html")


# Register routers
app.include_router(admin_auth_router, prefix="/api/v1")
app.include_router(customer_auth_router, prefix="/api/v1")
app.include_router(households_router, prefix="/api/v1")
app.include_router(meter_readings_router, prefix="/api/v1")
app.include_router(billing_router, prefix="/api/v1")
app.include_router(customer_invoices_router, prefix="/api/v1")
app.include_router(price_tiers_router, prefix="/api/v1")
