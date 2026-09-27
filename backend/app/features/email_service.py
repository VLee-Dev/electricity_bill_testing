"""
Email service for sending notifications
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import settings
from app.models.email_log import EmailLog
from app.models.invoice import Invoice


def send_invoice_email(invoice: Invoice, db: Session) -> bool:
    """
    Gửi email thông báo hóa đơn cho khách hàng

    Args:
        invoice: Invoice object
        db: Database session

    Returns:
        bool: True nếu gửi thành công, False nếu thất bại
    """
    household = invoice.household
    to_email = household.email

    if not to_email:
        print(f"[WARNING] Household {household.customer_code} không có email")
        return False

    # Tạo email content
    subject = f"Hóa đơn tiền điện kỳ {invoice.meter_reading.period}"

    body = f"""
Kính gửi quý khách {household.full_name},

Hệ thống xin thông báo hóa đơn tiền điện kỳ {invoice.meter_reading.period}:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THÔNG TIN HÓA ĐƠN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mã khách hàng: {household.customer_code}
Số đồng hồ: {household.meter_number}
Kỳ hóa đơn: {invoice.meter_reading.period}

Chỉ số cũ: {invoice.meter_reading.old_reading} kWh
Chỉ số mới: {invoice.meter_reading.new_reading} kWh
Tiêu thụ: {invoice.meter_reading.consumption} kWh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHI TIẾT TÍNH TIỀN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    # Thêm chi tiết từng bậc
    for tier in invoice.tier_details:
        body += f"\nBậc {tier.tier_no}: {tier.kwh_applied} kWh × {tier.unit_price:,} đ = {tier.amount:,} đ"

    body += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tổng tiền điện: {invoice.subtotal:,} đ
VAT (8%): {invoice.vat_amount:,} đ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TỔNG CỘNG: {invoice.total_amount:,} đ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ngày phát hành: {invoice.issued_at.strftime('%d/%m/%Y')}
Hạn thanh toán: {invoice.due_date.strftime('%d/%m/%Y')}

Vui lòng đăng nhập vào hệ thống để xem chi tiết và thanh toán trực tuyến.

Trân trọng,
{settings.sender_name}
"""

    status = "failed"
    error_message = None

    try:
        if settings.email_mode == "smtp":
            # Gửi email qua SMTP
            message = MIMEMultipart()
            message["From"] = f"{settings.sender_name} <{settings.sender_email}>"
            message["To"] = to_email
            message["Subject"] = subject

            message.attach(MIMEText(body, "plain", "utf-8"))

            # Kết nối SMTP server
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()  # Bật TLS
                server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(message)

            status = "success"
            print(f"[EMAIL] ✓ Đã gửi email đến {to_email}")

        else:
            # Console mode (development)
            print(f"\n{'='*60}")
            print(f"[EMAIL - CONSOLE MODE]")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"{'='*60}")
            print(body)
            print(f"{'='*60}\n")
            status = "console"

    except Exception as e:
        status = "failed"
        error_message = str(e)
        print(f"[EMAIL ERROR] Không gửi được email đến {to_email}: {e}")

    # Log vào database
    email_log = EmailLog(
        invoice_id=invoice.id,
        recipient_email=to_email,
        subject=subject,
        sent_at=datetime.now(timezone.utc),
        status=status,
        error_message=error_message,
    )
    db.add(email_log)
    db.commit()

    return status == "success"
