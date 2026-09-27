from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def new_id() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Household(Base):
    """
    Bảng households - Hộ sử dụng điện
    """
    __tablename__ = "households"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    customer_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String(500))
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(255))
    meter_number: Mapped[str] = mapped_column(String(50), unique=True)
    registered_at: Mapped[datetime] = mapped_column(default=utcnow)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active/inactive

    # Relationships
    customer: Mapped["Customer | None"] = relationship(back_populates="household", uselist=False)
    meter_readings: Mapped[list["MeterReading"]] = relationship(back_populates="household")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="household")
