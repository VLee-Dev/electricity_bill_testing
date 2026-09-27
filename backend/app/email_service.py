import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.config import settings
from app.models.email_log import EmailLog


def send_welcome_email(
    db: Session,
    recipient_email: str,
    recipient_name: str,
    customer_code: str,
    initial_password: str
) -> bool:
    """
    Gửi email chào mừng khi tạo tài khoản mới cho hộ dân

    Args:
        db: Database session
        recipient_email: Email người nhận
        recipient_name: Tên người nhận
        customer_code: Mã khách hàng (dùng để đăng nhập)
        initial_password: Mật khẩu khởi tạo

    Returns:
        True nếu gửi thành công, False nếu thất bại
    """
    subject = "Chào mừng bạn đến với Hệ thống Quản lý Điện"

    # HTML email body
    html_body = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                .credentials {{ background-color: #fff; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0; }}
                .credentials strong {{ color: #4CAF50; }}
                .footer {{ text-align: center; margin-top: 20px; color: #777; font-size: 12px; }}
                .button {{ display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🏠 Hệ thống Quản lý Điện</h2>
                </div>
                <div class="content">
                    <h3>Xin chào {recipient_name},</h3>
                    <p>Tài khoản của bạn đã được tạo thành công trong hệ thống quản lý hóa đơn tiền điện.</p>

                    <div class="credentials">
                        <h4>Thông tin đăng nhập:</h4>
                        <p><strong>Mã khách hàng:</strong> {customer_code}</p>
                        <p><strong>Mật khẩu khởi tạo:</strong> {initial_password}</p>
                    </div>

                    <p><strong>⚠️ Lưu ý quan trọng:</strong></p>
                    <ul>
                        <li>Vui lòng đổi mật khẩu ngay sau lần đăng nhập đầu tiên</li>
                        <li>Không chia sẻ thông tin đăng nhập với người khác</li>
                        <li>Liên hệ quản trị viên nếu quên mật khẩu</li>
                    </ul>

                    <p style="text-align: center;">
                        <a href="http://localhost:5173/pages/auth/customer_login.html" class="button">Đăng nhập ngay</a>
                    </p>
                </div>
                <div class="footer">
                    <p>Email này được gửi tự động, vui lòng không trả lời.</p>
                    <p>&copy; 2026 Hệ thống Quản lý Điện. All rights reserved.</p>
                </div>
            </div>
        </body>
    </html>
    """

    # Plain text fallback
    text_body = f"""
Xin chào {recipient_name},

Tài khoản của bạn đã được tạo thành công trong hệ thống quản lý hóa đơn tiền điện.

Thông tin đăng nhập:
- Mã khách hàng: {customer_code}
- Mật khẩu khởi tạo: {initial_password}

⚠️ Lưu ý quan trọng:
- Vui lòng đổi mật khẩu ngay sau lần đăng nhập đầu tiên
- Không chia sẻ thông tin đăng nhập với người khác
- Liên hệ quản trị viên nếu quên mật khẩu

Đăng nhập tại: http://localhost:5173/pages/auth/customer_login.html

---
Email này được gửi tự động, vui lòng không trả lời.
© 2026 Hệ thống Quản lý Điện
    """

    try:
        if settings.email_mode == "console":
            # Console mode - chỉ in ra console để test
            print("=" * 80)
            print(f"📧 EMAIL (Console Mode)")
            print(f"To: {recipient_email}")
            print(f"Subject: {subject}")
            print("-" * 80)
            print(text_body)
            print("=" * 80)

            # Log thành công
            email_log = EmailLog(
                invoice_id=None,
                recipient_email=recipient_email,
                subject=subject,
                status="success",
                error_message=None,
                sent_at=datetime.now(timezone.utc)
            )
            db.add(email_log)
            db.commit()
            return True

        elif settings.email_mode == "smtp":
            # SMTP mode - gửi email thật
            if not settings.smtp_username or not settings.smtp_password:
                raise ValueError("SMTP credentials not configured")

            # Tạo email message
            message = MIMEMultipart("alternative")
            message["From"] = f"{settings.sender_name} <{settings.sender_email or settings.smtp_username}>"
            message["To"] = recipient_email
            message["Subject"] = subject

            # Attach text và HTML parts
            part1 = MIMEText(text_body, "plain", "utf-8")
            part2 = MIMEText(html_body, "html", "utf-8")
            message.attach(part1)
            message.attach(part2)

            # Kết nối SMTP và gửi
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(message)

            # Log thành công
            email_log = EmailLog(
                invoice_id=None,
                recipient_email=recipient_email,
                subject=subject,
                status="success",
                error_message=None,
                sent_at=datetime.now(timezone.utc)
            )
            db.add(email_log)
            db.commit()
            return True

        else:
            raise ValueError(f"Invalid email_mode: {settings.email_mode}")

    except Exception as e:
        # Log lỗi
        error_message = str(e)
        print(f"❌ Failed to send email: {error_message}")

        email_log = EmailLog(
            invoice_id=None,
            recipient_email=recipient_email,
            subject=subject,
            status="failed",
            error_message=error_message,
            sent_at=datetime.now(timezone.utc)
        )
        db.add(email_log)
        db.commit()
        return False
