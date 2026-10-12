from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.features.email_service import send_invoice_email


def make_invoice(email="customer@example.com", tiers=None):
    if tiers is None:
        tiers = [
            SimpleNamespace(
                tier_no=1,
                kwh_applied=50,
                unit_price=1800,
                amount=90000,
            )
        ]

    household = SimpleNamespace(
        email=email,
        customer_code="KH001",
        full_name="Nguyen Van A",
        meter_number="CT001",
    )

    reading = SimpleNamespace(
        period="2026-10",
        old_reading=100,
        new_reading=250,
        consumption=150,
    )

    return SimpleNamespace(
        id="invoice-1",
        household=household,
        meter_reading=reading,
        tier_details=tiers,
        subtotal=270000,
        vat_amount=21600,
        total_amount=291600,
        issued_at=datetime(2026, 10, 1),
        due_date=datetime(2026, 10, 20),
    )


def test_send_invoice_email_without_recipient():
    db = MagicMock()
    invoice = make_invoice(email=None)

    result = send_invoice_email(invoice, db)

    assert result is False
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_send_invoice_email_smtp_success():
    db = MagicMock()
    invoice = make_invoice()
    smtp = MagicMock()
    server = smtp.return_value.__enter__.return_value

    with (
        patch(
            "app.features.email_service.settings.email_mode",
            "smtp",
        ),
        patch(
            "app.features.email_service.smtplib.SMTP",
            smtp,
        ),
    ):
        result = send_invoice_email(invoice, db)

    assert result is True
    server.starttls.assert_called_once()
    server.login.assert_called_once()
    server.send_message.assert_called_once()

    db.add.assert_called_once()
    db.commit.assert_called_once()

    email_log = db.add.call_args.args[0]
    assert email_log.status == "success"
    assert email_log.recipient_email == "customer@example.com"
    assert email_log.invoice_id == "invoice-1"


def test_send_invoice_email_smtp_failure():
    db = MagicMock()
    invoice = make_invoice()

    with (
        patch(
            "app.features.email_service.settings.email_mode",
            "smtp",
        ),
        patch(
            "app.features.email_service.smtplib.SMTP",
            side_effect=ConnectionError("SMTP unavailable"),
        ),
    ):
        result = send_invoice_email(invoice, db)

    assert result is False
    db.add.assert_called_once()
    db.commit.assert_called_once()

    email_log = db.add.call_args.args[0]
    assert email_log.status == "failed"
    assert "SMTP unavailable" in email_log.error_message


def test_send_invoice_email_console_mode():
    db = MagicMock()
    invoice = make_invoice()

    with patch(
        "app.features.email_service.settings.email_mode",
        "console",
    ):
        result = send_invoice_email(invoice, db)

    assert result is False
    db.add.assert_called_once()
    db.commit.assert_called_once()

    email_log = db.add.call_args.args[0]
    assert email_log.status == "console"
    assert email_log.error_message is None


def test_send_invoice_email_contains_multiple_tiers():
    db = MagicMock()

    tiers = [
        SimpleNamespace(
            tier_no=1,
            kwh_applied=50,
            unit_price=1800,
            amount=90000,
        ),
        SimpleNamespace(
            tier_no=2,
            kwh_applied=100,
            unit_price=2000,
            amount=200000,
        ),
    ]

    invoice = make_invoice(tiers=tiers)
    smtp = MagicMock()
    server = smtp.return_value.__enter__.return_value

    with (
        patch(
            "app.features.email_service.settings.email_mode",
            "smtp",
        ),
        patch(
            "app.features.email_service.smtplib.SMTP",
            smtp,
        ),
    ):
        result = send_invoice_email(invoice, db)

    assert result is True

    message = server.send_message.call_args.args[0]
    content = message.get_payload()[0].get_payload(decode=True).decode("utf-8")

    assert "Bậc 1" in content
    assert "Bậc 2" in content
    assert "90,000" in content
    assert "200,000" in content
    assert "291,600" in content
