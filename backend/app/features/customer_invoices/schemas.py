from datetime import date, datetime

from pydantic import BaseModel


class InvoiceTierDetailOut(BaseModel):
    tier_no: int
    kwh_applied: int
    unit_price: int
    amount: int

    class Config:
        from_attributes = True


class HouseholdBriefOut(BaseModel):
    customer_code: str
    full_name: str

    class Config:
        from_attributes = True


class MeterReadingBriefOut(BaseModel):
    period: str
    consumption: int

    class Config:
        from_attributes = True


class CustomerInvoiceListOut(BaseModel):
    id: str
    subtotal: int
    vat_amount: int
    total_amount: int
    status: str
    issued_at: datetime
    due_date: date
    household: HouseholdBriefOut | None = None
    meter_reading: MeterReadingBriefOut | None = None

    class Config:
        from_attributes = True


class CustomerInvoiceOut(BaseModel):
    id: str
    household_id: str
    meter_reading_id: str
    subtotal: int
    vat_amount: int
    total_amount: int
    status: str
    issued_at: datetime
    due_date: date
    tier_details: list[InvoiceTierDetailOut]
    household: HouseholdBriefOut | None = None
    meter_reading: MeterReadingBriefOut | None = None

    class Config:
        from_attributes = True


class PaymentCreateIn(BaseModel):
    pass  # Không cần input, thanh toán mô phỏng tự động


class PaymentOut(BaseModel):
    id: str
    invoice_id: str
    amount: int
    method: str
    paid_at: datetime

    class Config:
        from_attributes = True
