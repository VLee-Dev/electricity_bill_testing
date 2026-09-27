from datetime import date
from pydantic import BaseModel, Field


class PriceTierOut(BaseModel):
    """Schema output cho price tier"""
    id: int
    tier_no: int
    kwh_from: int
    kwh_to: int | None
    unit_price: int
    effective_from: date
    effective_to: date | None

    class Config:
        from_attributes = True


class PriceTierUpdateIn(BaseModel):
    """Schema input để cập nhật giá điện"""
    unit_price: int = Field(gt=0, description="Đơn giá (đồng/kWh)")
    effective_from: date = Field(description="Ngày hiệu lực")
