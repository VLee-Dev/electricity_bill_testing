from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.payment import Payment


def get_customer_invoices(db: Session, customer: Customer) -> list[Invoice]:
    """
    FUNC-09: Xem hóa đơn & lịch sử
    Customer chỉ xem được hóa đơn của chính mình
    """
    from sqlalchemy.orm import joinedload
    return db.scalars(
        select(Invoice)
        .options(
            joinedload(Invoice.household),
            joinedload(Invoice.meter_reading),
        )
        .where(Invoice.household_id == customer.household_id)
        .order_by(Invoice.issued_at.desc())
    ).all()


def get_customer_invoice(db: Session, invoice_id: str, customer: Customer) -> Invoice:
    """
    Xem chi tiết 1 hóa đơn
    """
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise NotFoundError("Không tìm thấy hóa đơn.")

    # Kiểm tra quyền: chỉ được xem hóa đơn của chính mình
    if invoice.household_id != customer.household_id:
        raise ForbiddenError("Bạn không có quyền xem hóa đơn này.")

    return invoice


def pay_invoice_simulated(db: Session, invoice_id: str, customer: Customer) -> Payment:
    """
    FUNC-10: Thanh toán nhanh (mô phỏng)
    Customer bấm nút thanh toán → hệ thống xác nhận ngay (không tích hợp cổng thanh toán thật)
    """
    invoice = get_customer_invoice(db, invoice_id, customer)

    # Kiểm tra trạng thái
    if invoice.status == "paid":
        error = ConflictError("Hóa đơn đã được thanh toán.")
        error.error_code = "INVOICE_ALREADY_PAID"
        raise error

    # Tạo payment
    payment = Payment(
        invoice_id=invoice.id,
        amount=invoice.total_amount,
        method="online_simulated",
        confirmed_by=None  # Customer tự thanh toán
    )

    # Cập nhật trạng thái invoice
    invoice.status = "paid"

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
