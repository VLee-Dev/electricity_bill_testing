from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def new_id() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Invoice(Base):
    """
    Bảng invoices - Hóa đơn
    """
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    household_id: Mapped[str] = mapped_column(ForeignKey("households.id"), index=True)
    meter_reading_id: Mapped[str] = mapped_column(ForeignKey("meter_readings.id"), unique=True)
    subtotal: Mapped[int] = mapped_column(BigInteger)
    vat_amount: Mapped[int] = mapped_column(BigInteger)
    total_amount: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(20), default="unpaid")  # unpaid/paid
    issued_at: Mapped[datetime] = mapped_column(default=utcnow)
    due_date: Mapped[date] = mapped_column(Date)

    # Relationships
    household: Mapped["Household"] = relationship(back_populates="invoices")
    meter_reading: Mapped["MeterReading"] = relationship(back_populates="invoice")
    tier_details: Mapped[list["InvoiceTierDetail"]] = relationship(back_populates="invoice", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship(back_populates="invoice")


class InvoiceTierDetail(Base):
    """
    Bảng invoice_tier_details - Chi tiết tính theo từng bậc
    """
    __tablename__ = "invoice_tier_details"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invoice_id: Mapped[str] = mapped_column(ForeignKey("invoices.id"), index=True)
    tier_no: Mapped[int] = mapped_column(Integer)
    kwh_applied: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[int] = mapped_column(Integer)
    amount: Mapped[int] = mapped_column(BigInteger)

    # Relationships
    invoice: Mapped["Invoice"] = relationship(back_populates="tier_details")
