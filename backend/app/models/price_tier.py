from datetime import date

from sqlalchemy import Date, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PriceTier(Base):
    """
    Bảng price_tiers - Bậc giá điện
    Hỗ trợ thay đổi biểu giá theo thời gian với effective_from/effective_to
    """
    __tablename__ = "price_tiers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tier_no: Mapped[int] = mapped_column(Integer)
    kwh_from: Mapped[int] = mapped_column(Integer)  # Ngưỡng bắt đầu (VD: 0, 51, 101...)
    kwh_to: Mapped[int | None] = mapped_column(Integer, nullable=True)  # NULL = không giới hạn
    unit_price: Mapped[int] = mapped_column(Integer)  # VNĐ/kWh
    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)  # NULL = đang áp dụng
