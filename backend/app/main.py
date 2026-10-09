from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base
import app.database as database
from app.exceptions import DomainError

from app.models import *  # noqa: F401, F403

# Import routers
from app.features.admin_auth.router import router as admin_auth_router
from app.features.billing_new.router import router as billing_router
from app.features.customer_auth.router import router as customer_auth_router
from app.features.customer_invoices.router import router as customer_invoices_router
from app.features.households.router import router as households_router
from app.features.meter_readings_new.router import router as meter_readings_router
from app.features.price_tiers.router import router as price_tiers_router


BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend" / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Sử dụng engine hiện tại, hỗ trợ SQLite khi chạy pytest
    Base.metadata.create_all(bind=database.engine)
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

app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static"
)

app.mount(
    "/admin",
    StaticFiles(
        directory=str(FRONTEND_DIR / "pages" / "admin"),
        html=True
    ),
    name="admin"
)

app.mount(
    "/customer",
    StaticFiles(
        directory=str(FRONTEND_DIR / "pages" / "customer"),
        html=True
    ),
    name="customer"
)

app.mount(
    "/auth",
    StaticFiles(
        directory=str(FRONTEND_DIR / "pages" / "auth"),
        html=True
    ),
    name="auth"
)


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
    return FileResponse(str(FRONTEND_DIR / "index.html"))


app.include_router(admin_auth_router, prefix="/api/v1")
app.include_router(customer_auth_router, prefix="/api/v1")
app.include_router(households_router, prefix="/api/v1")
app.include_router(meter_readings_router, prefix="/api/v1")
app.include_router(billing_router, prefix="/api/v1")
app.include_router(customer_invoices_router, prefix="/api/v1")
app.include_router(price_tiers_router, prefix="/api/v1")