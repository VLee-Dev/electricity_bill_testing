import pytest
from unittest.mock import MagicMock, patch

from app.email_service import send_welcome_email


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def email_data():
    return {
        "recipient_email": "customer@example.com",
        "recipient_name": "Nguyen Van A",
        "customer_code": "KH001",
        "initial_password": "Password123",
    }


def test_console_mode_success(db, email_data, capsys):
    with patch("app.email_service.settings") as settings:
        settings.email_mode = "console"

        result = send_welcome_email(db, **email_data)

    assert result is True
    db.add.assert_called_once()
    db.commit.assert_called_once()

    email_log = db.add.call_args.args[0]
    assert email_log.status == "success"
    assert email_log.recipient_email == "customer@example.com"

    output = capsys.readouterr().out
    assert "KH001" in output
    assert "Password123" in output


def test_smtp_mode_success(db, email_data):
    with (
        patch("app.email_service.settings") as settings,
        patch("app.email_service.smtplib.SMTP") as smtp,
    ):
        settings.email_mode = "smtp"
        settings.smtp_username = "sender@example.com"
        settings.smtp_password = "secret"
        settings.smtp_host = "smtp.example.com"
        settings.smtp_port = 587
        settings.sender_name = "Electricity"
        settings.sender_email = "sender@example.com"

        result = send_welcome_email(db, **email_data)

    assert result is True
    smtp.assert_called_once_with("smtp.example.com", 587)

    server = smtp.return_value.__enter__.return_value
    server.starttls.assert_called_once()
    server.login.assert_called_once_with("sender@example.com", "secret")
    server.send_message.assert_called_once()

    message = server.send_message.call_args.args[0]
    assert message["To"] == "customer@example.com"
    assert len(message.get_payload()) == 2

    assert db.add.call_args.args[0].status == "success"
    db.commit.assert_called_once()


@pytest.mark.parametrize(
    "username,password",
    [
        ("", "secret"),
        ("sender@example.com", ""),
    ],
)
def test_smtp_missing_credentials(db, email_data, username, password):
    with (
        patch("app.email_service.settings") as settings,
        patch("app.email_service.smtplib.SMTP") as smtp,
    ):
        settings.email_mode = "smtp"
        settings.smtp_username = username
        settings.smtp_password = password

        result = send_welcome_email(db, **email_data)

    assert result is False
    smtp.assert_not_called()

    email_log = db.add.call_args.args[0]
    assert email_log.status == "failed"
    assert "SMTP credentials" in email_log.error_message
    db.commit.assert_called_once()


def test_smtp_connection_failure(db, email_data):
    with (
        patch("app.email_service.settings") as settings,
        patch("app.email_service.smtplib.SMTP") as smtp,
    ):
        settings.email_mode = "smtp"
        settings.smtp_username = "sender@example.com"
        settings.smtp_password = "secret"
        settings.smtp_host = "smtp.example.com"
        settings.smtp_port = 587
        settings.sender_name = "Electricity"
        settings.sender_email = "sender@example.com"

        smtp.return_value.__enter__.side_effect = OSError(
            "SMTP connection failed"
        )

        result = send_welcome_email(db, **email_data)

    assert result is False
    email_log = db.add.call_args.args[0]
    assert email_log.status == "failed"
    assert "SMTP connection failed" in email_log.error_message
    db.commit.assert_called_once()


def test_invalid_email_mode(db, email_data):
    with patch("app.email_service.settings") as settings:
        settings.email_mode = "invalid"

        result = send_welcome_email(db, **email_data)

    assert result is False
    email_log = db.add.call_args.args[0]
    assert email_log.status == "failed"
    assert "Invalid email_mode" in email_log.error_message


def test_smtp_message_contains_customer_information(db, email_data):
    with (
        patch("app.email_service.settings") as settings,
        patch("app.email_service.smtplib.SMTP") as smtp,
    ):
        settings.email_mode = "smtp"
        settings.smtp_username = "sender@example.com"
        settings.smtp_password = "secret"
        settings.smtp_host = "smtp.example.com"
        settings.smtp_port = 587
        settings.sender_name = "Electricity"
        settings.sender_email = ""

        result = send_welcome_email(db, **email_data)

    assert result is True

    server = smtp.return_value.__enter__.return_value
    message = server.send_message.call_args.args[0]

    assert "sender@example.com" in message["From"]

    parts = message.get_payload()
    plain_text = parts[0].get_payload(decode=True).decode("utf-8")
    html_text = parts[1].get_payload(decode=True).decode("utf-8")

    for content in (plain_text, html_text):
        assert "Nguyen Van A" in content
        assert "KH001" in content
        assert "Password123" in content


def test_database_log_failure(db, email_data):
    db.commit.side_effect = RuntimeError("Database unavailable")

    with patch("app.email_service.settings") as settings:
        settings.email_mode = "console"

        with pytest.raises(RuntimeError, match="Database unavailable"):
            send_welcome_email(db, **email_data)

    assert db.commit.call_count == 2
