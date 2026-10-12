
import asyncio
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import UUID

from fastapi.responses import FileResponse

from app.features.households.router import (
    get_households,
    get_household_detail,
)
from app.main import root
from app.models import admin, email_log, meter_reading, payment


# ============================================================
# HOUSEHOLDS ROUTER
# ============================================================

def test_get_households_router():
    """FC001: Router forwards filters to household service."""
    db = MagicMock()
    expected = [MagicMock(), MagicMock()]

    with patch(
        "app.features.households.router.list_households",
        return_value=expected,
    ) as mock_service:
        result = get_households(
            search="KH001",
            status="active",
            db=db,
        )

    assert result is expected
    mock_service.assert_called_once_with(
        db, "KH001", "active"
    )


def test_get_household_detail_router():
    """FC008: Router returns household details from service."""
    db = MagicMock()
    household_id = "HH001"
    expected = MagicMock()

    with patch(
        "app.features.households.router.get_household",
        return_value=expected,
    ) as mock_service:
        result = get_household_detail(
            household_id=household_id,
            db=db,
        )

    assert result is expected
    mock_service.assert_called_once_with(db, household_id)


# ============================================================
# MAIN APPLICATION
# ============================================================

def test_root_returns_frontend_index():
    """FC002: Root route returns frontend index.html."""
    response = asyncio.run(root())

    assert isinstance(response, FileResponse)
    assert response.path.endswith("index.html")


# ============================================================
# ADMIN MODEL
# ============================================================

def test_admin_new_id():
    """FC003: Admin ID generator returns valid UUID."""
    generated_id = admin.new_id()

    assert isinstance(generated_id, str)
    assert str(UUID(generated_id)) == generated_id


# ============================================================
# EMAIL LOG MODEL
# ============================================================

def test_email_log_utcnow():
    """FC004: EmailLog timestamp uses UTC."""
    result = email_log.utcnow()

    assert isinstance(result, datetime)
    assert result.tzinfo == timezone.utc


# ============================================================
# METER READING MODEL
# ============================================================

def test_meter_reading_new_id():
    """FC005: MeterReading ID generator returns valid UUID."""
    generated_id = meter_reading.new_id()

    assert isinstance(generated_id, str)
    assert str(UUID(generated_id)) == generated_id


# ============================================================
# PAYMENT MODEL
# ============================================================

def test_payment_new_id():
    """FC006: Payment ID generator returns valid UUID."""
    generated_id = payment.new_id()

    assert isinstance(generated_id, str)
    assert str(UUID(generated_id)) == generated_id


def test_payment_utcnow():
    """FC007: Payment timestamp uses UTC."""
    result = payment.utcnow()

    assert isinstance(result, datetime)
    assert result.tzinfo == timezone.utc
