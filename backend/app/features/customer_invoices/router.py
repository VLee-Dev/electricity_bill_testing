from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_customer
from app.features.customer_invoices.schemas import (
    CustomerInvoiceListOut,
    CustomerInvoiceOut,
    PaymentCreateIn,
    PaymentOut,
)
from app.features.customer_invoices.service import (
    get_customer_invoice,
    get_customer_invoices,
    pay_invoice_simulated,
)
from app.models.invoice import Invoice

router = APIRouter(prefix="/customer/invoices", tags=["Customer - Invoices"])


@router.get("", response_model=list[CustomerInvoiceListOut])
def list_my_invoices(
    customer=Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    FUNC-09: Xem danh sách hóa đơn & lịch sử của mình
    """
    return get_customer_invoices(db, customer)


@router.get("/{invoice_id}", response_model=CustomerInvoiceOut)
def get_my_invoice(
    invoice_id: str,
    customer=Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    FUNC-09: Xem chi tiết 1 hóa đơn
    """
    invoice = get_customer_invoice(db, invoice_id, customer)
    # Eager load household, meter_reading và tier_details
    return db.scalar(
        select(Invoice)
        .options(
            joinedload(Invoice.tier_details),
            joinedload(Invoice.household),
            joinedload(Invoice.meter_reading),
        )
        .where(Invoice.id == invoice_id)
    )


@router.post("/{invoice_id}/pay", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def pay_invoice(
    invoice_id: str,
    data: PaymentCreateIn,
    customer=Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    FUNC-10: Thanh toán nhanh (mô phỏng - không tích hợp cổng thanh toán thật)
    """
    return pay_invoice_simulated(db, invoice_id, customer)
