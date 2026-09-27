from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def new_id() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MeterReading(Base):
    """
    Bảng meter_readings - Chỉ số điện theo kỳ
    """
    __tablename__ = "meter_readings"
    __table_args__ = (
        UniqueConstraint("household_id", "period", name="uq_household_period"),
        CheckConstraint("new_reading >= old_reading", name="ck_reading_valid"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    household_id: Mapped[str] = mapped_column(ForeignKey("households.id"), index=True)
    period: Mapped[str] = mapped_column(String(7))  # YYYY-MM
    old_reading: Mapped[int] = mapped_column(Integer)
    new_reading: Mapped[int] = mapped_column(Integer)
    consumption: Mapped[int] = mapped_column(Integer)  # computed = new - old
    recorded_at: Mapped[datetime] = mapped_column(default=utcnow)
    recorded_by: Mapped[str | None] = mapped_column(ForeignKey("admins.id"), nullable=True)

    # Relationships
    household: Mapped["Household"] = relationship(back_populates="meter_readings")
    invoice: Mapped["Invoice | None"] = relationship(back_populates="meter_reading", uselist=False)
