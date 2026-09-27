"""
Integration tests cho Meter Readings API: DELETE
(không có invoice thì OK; có invoice thì 409)
"""
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.admin import Admin
from app.models.household import Household
from app.models.invoice import Invoice
from app.models.meter_reading import MeterReading
from app.security import create_access_token, hash_password


@pytest.fixture
def admin(db: Session) -> Admin:
    admin = Admin(
        id="test-admin",
        username="testadmin",
        password_hash=hash_password("password123"),
        full_name="Test Admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def admin_token(admin: Admin) -> str:
    return create_access_token({"sub": admin.id, "type": "admin"})


@pytest.fixture
def household(db: Session) -> Household:
    h = Household(
        id="hh-1",
        customer_code="KHX",
        full_name="Test User",
        address="Test",
        phone="0901234567",
        email="hh1@example.com",
        meter_number="MTX"
    )
    db.add(h)
    db.commit()
    return h


def test_delete_meter_reading_success(client: TestClient, admin_token: str, db: Session, household: Household):
    """DELETE meter reading chưa có invoice → 200, row bị xóa."""
    reading = MeterReading(
        id="r-del-1",
        household_id=household.id,
        period="2026-09",
        old_reading=0,
        new_reading=100,
        consumption=100
    )
    db.add(reading)
    db.commit()

    response = client.delete(
        "/api/v1/admin/meter-readings/r-del-1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "Đã xóa" in response.json()["message"]

    db.expire_all()
    assert db.get(MeterReading, "r-del-1") is None


def test_delete_meter_reading_with_invoice_blocked(
    client: TestClient, admin_token: str, db: Session, household: Household
):
    """DELETE meter reading đã có invoice → 409 READING_HAS_INVOICE."""
    reading = MeterReading(
        id="r-del-2",
        household_id=household.id,
        period="2026-10",
        old_reading=100,
        new_reading=200,
        consumption=100
    )
    db.add(reading)
    db.flush()

    invoice = Invoice(
        id="inv-del-1",
        household_id=household.id,
        meter_reading_id="r-del-2",
        subtotal=100000,
        vat_amount=8000,
        total_amount=108000,
        status="paid",
        issued_at=datetime(2026, 10, 15),
        due_date=date(2026, 10, 30)
    )
    db.add(invoice)
    db.commit()

    response = client.delete(
        "/api/v1/admin/meter-readings/r-del-2",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 409
    assert response.json()["error_code"] == "READING_HAS_INVOICE"

    # Reading vẫn còn trong DB
    db.expire_all()
    assert db.get(MeterReading, "r-del-2") is not None


def test_delete_meter_reading_not_found(client: TestClient, admin_token: str):
    """DELETE không tồn tại → 404."""
    response = client.delete(
        "/api/v1/admin/meter-readings/not-exist-id",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
