from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError
from app.models.invoice import Invoice, InvoiceTierDetail
from app.models.meter_reading import MeterReading
from app.models.price_tier import PriceTier
from app.models.system_config import SystemConfig
from app.features.email_service import send_invoice_email


def calculate_invoice(db: Session, meter_reading_id: str) -> Invoice:
    """
    FUNC-03: Tính tiền điện theo biểu giá bậc thang
    Từ 1 meter_reading → tạo invoice với chi tiết từng bậc
    """
    # Lấy meter reading
    reading = db.get(MeterReading, meter_reading_id)
    if not reading:
        raise NotFoundError("Không tìm thấy chỉ số điện.")

    # Kiểm tra đã có invoice chưa
    existing = db.scalar(select(Invoice).where(Invoice.meter_reading_id == meter_reading_id))
    if existing:
        error = ConflictError("Chỉ số này đã có hóa đơn.")
        error.error_code = "INVOICE_EXISTS"
        raise error

    # Lấy biểu giá hiện tại (effective_to = NULL)
    tiers = db.scalars(
        select(PriceTier)
        .where(PriceTier.effective_to.is_(None))
        .order_by(PriceTier.tier_no)
    ).all()

    # Lấy mức tiêu thụ của kỳ này
    consumption = reading.consumption or (reading.new_reading - reading.old_reading)

    # Xác định bậc mà consumption thuộc về (tính gộp - toàn bộ consumption được nhân
    # với đơn giá của bậc đó).
    # Quy ước ngưỡng (theo bảng giá EVN):
    #   Bậc 1: 0   - 50   kWh
    #   Bậc 2: 51  - 100  kWh
    #   Bậc 3: 101 - 200  kWh
    #   Bậc 4: 201 - 300  kWh
    #   Bậc 5: 301 - 400  kWh
    #   Bậc 6: >= 401 kWh
    if not tiers:
        raise NotFoundError("Chưa cấu hình biểu giá điện.")

    # Tìm bậc phù hợp với consumption
    matched_tier = None
    for tier in tiers:
        kwh_from = tier.kwh_from or 0
        kwh_to = tier.kwh_to if tier.kwh_to is not None else float("inf")
        # Nếu kwh_from = 0 thì bậc đó bao gồm cả 0 (VD: tier 1: 0 ≤ x ≤ 50)
        # Các tier khác: kwh_from ≤ x ≤ kwh_to (VD: tier 2: 51 ≤ x ≤ 100)
        if kwh_from == 0:
            in_tier = consumption <= kwh_to
        else:
            in_tier = kwh_from <= consumption <= kwh_to
        if in_tier:
            matched_tier = tier
            break

    # Nếu consumption > tất cả các bậc có kwh_to → rơi vào bậc cuối (kwh_to IS NULL)
    if matched_tier is None:
        for tier in tiers:
            if tier.kwh_to is None:
                matched_tier = tier
                break

    if matched_tier is None:
        raise NotFoundError("Không tìm được bậc giá phù hợp với mức tiêu thụ.")

    # Tính tiền - toàn bộ consumption nhân với đơn giá bậc đó
    kwh_applied = consumption
    amount = kwh_applied * matched_tier.unit_price
    subtotal = amount

    tier_details = [
        InvoiceTierDetail(
            tier_no=matched_tier.tier_no,
            kwh_applied=kwh_applied,
            unit_price=matched_tier.unit_price,
            amount=amount,
        )
    ]

    # Lấy VAT rate từ system_config (mặc định 8%)
    vat_rate_config = db.scalar(select(SystemConfig).where(SystemConfig.key == "vat_rate"))
    vat_rate = Decimal(vat_rate_config.value if vat_rate_config else "0.08")

    # Tính VAT (làm tròn đến đồng)
    vat_amount = int((Decimal(subtotal) * vat_rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    total_amount = subtotal + vat_amount

    # Lấy số ngày đến hạn thanh toán từ config (mặc định 15 ngày)
    due_days_config = db.scalar(select(SystemConfig).where(SystemConfig.key == "invoice_due_days"))
    due_days = int(due_days_config.value if due_days_config else "15")
    due_date = date.today() + timedelta(days=due_days)

    # Tạo invoice
    invoice = Invoice(
        household_id=reading.household_id,
        meter_reading_id=reading.id,
        subtotal=subtotal,
        vat_amount=vat_amount,
        total_amount=total_amount,
        status="unpaid",
        due_date=due_date,
        tier_details=tier_details
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    # Gửi email thông báo
    try:
        send_invoice_email(invoice, db)
    except Exception as e:
        # Log lỗi nhưng không fail transaction
        print(f"[WARNING] Không gửi được email cho invoice {invoice.id}: {e}")

    return invoice


def get_invoice(db: Session, invoice_id: str) -> Invoice:
    """
    Lấy chi tiết invoice
    """
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise NotFoundError("Không tìm thấy hóa đơn.")
    return invoice


def list_invoices(
    db: Session,
    household_id: str | None = None,
    status: str | None = None
) -> list[Invoice]:
    """
    Danh sách invoices
    """
    from sqlalchemy.orm import joinedload

    query = select(Invoice).options(
        joinedload(Invoice.household),
        joinedload(Invoice.meter_reading)
    )

    if household_id:
        query = query.where(Invoice.household_id == household_id)

    if status:
        query = query.where(Invoice.status == status)

    query = query.order_by(Invoice.issued_at.desc())
    return db.scalars(query).all()
