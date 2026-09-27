from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def new_id() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Payment(Base):
    """
    Bảng payments - Thanh toán
    """
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    invoice_id: Mapped[str] = mapped_column(ForeignKey("invoices.id"), index=True)
    amount: Mapped[int] = mapped_column(BigInteger)
    method: Mapped[str] = mapped_column(String(50))  # cash/bank_transfer/online_simulated
    paid_at: Mapped[datetime] = mapped_column(default=utcnow)
    confirmed_by: Mapped[str | None] = mapped_column(ForeignKey("admins.id"), nullable=True)  # NULL nếu customer tự thanh toán

    # Relationships
    invoice: Mapped["Invoice"] = relationship(back_populates="payments")
