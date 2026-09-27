from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def new_id() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Customer(Base):
    """
    Bảng customers - Tài khoản khách hàng
    Liên kết 1-1 với Household
    Đăng nhập bằng customer_code (từ household) + password
    """
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    household_id: Mapped[str] = mapped_column(ForeignKey("households.id"), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    # Relationships
    household: Mapped["Household"] = relationship(back_populates="customer")
