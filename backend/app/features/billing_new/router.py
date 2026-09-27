from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_admin
from app.features.billing_new.schemas import InvoiceCreateIn, InvoiceListOut, InvoiceOut
from app.features.billing_new.service import calculate_invoice, get_invoice, list_invoices
from app.models.invoice import Invoice

router = APIRouter(prefix="/admin/invoices", tags=["Admin - Billing"])


@router.post("/calculate", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
def create_invoice(
    data: InvoiceCreateIn,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """
    FUNC-03: Tính tiền điện từ meter_reading → tạo invoice
    """
    invoice = calculate_invoice(db, data.meter_reading_id)
    # Eager load tier_details
    db.refresh(invoice)
    return db.scalar(
        db.query(Invoice)
        .options(joinedload(Invoice.tier_details))
        .where(Invoice.id == invoice.id)
    )


@router.get("", response_model=list[InvoiceListOut])
def get_invoices(
    household_id: str | None = Query(None),
    status: str | None = Query(None, pattern="^(paid|unpaid)$"),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """
    Danh sách hóa đơn
    """
    return list_invoices(db, household_id, status)


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice_detail(
    invoice_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """
    Chi tiết hóa đơn
    """
    invoice = get_invoice(db, invoice_id)
    # Eager load tier_details
    return db.scalar(
        db.query(Invoice)
        .options(joinedload(Invoice.tier_details))
        .where(Invoice.id == invoice_id)
    )
