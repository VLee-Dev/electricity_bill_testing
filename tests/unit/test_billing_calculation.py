"""
Unit tests for billing calculation (tính gộp - consumption được nhân với đơn giá của bậc nó thuộc về).
"""
import pytest
from datetime import date
from decimal import Decimal

from app.features.billing_new.service import calculate_invoice
from app.models.household import Household
from app.models.meter_reading import MeterReading
from app.models.price_tier import PriceTier
from app.models.system_config import SystemConfig


@pytest.fixture
def setup_price_tiers(db):
    """Setup price tiers"""
    # Bảng giá mẫu EVN: 6 bậc
    # Tier 1: 0-50 kWh, 1678 đ/kWh
    # Tier 2: 51-100 kWh, 1734 đ/kWh
    # Tier 3: 101-200 kWh, 2014 đ/kWh
    # Tier 4: 201-300 kWh, 2536 đ/kWh
    # Tier 5: 301-400 kWh, 2834 đ/kWh
    # Tier 6: >=401 kWh, 2927 đ/kWh
    tiers = [
        PriceTier(tier_no=1, kwh_from=0, kwh_to=50, unit_price=1678, effective_from=date(2024, 1, 1)),
        PriceTier(tier_no=2, kwh_from=51, kwh_to=100, unit_price=1734, effective_from=date(2024, 1, 1)),
        PriceTier(tier_no=3, kwh_from=101, kwh_to=200, unit_price=2014, effective_from=date(2024, 1, 1)),
        PriceTier(tier_no=4, kwh_from=201, kwh_to=300, unit_price=2536, effective_from=date(2024, 1, 1)),
        PriceTier(tier_no=5, kwh_from=301, kwh_to=400, unit_price=2834, effective_from=date(2024, 1, 1)),
        PriceTier(tier_no=6, kwh_from=401, kwh_to=None, unit_price=2927, effective_from=date(2024, 1, 1)),
    ]
    for tier in tiers:
        db.add(tier)

    # Setup system config
    db.add(SystemConfig(key="vat_rate", value="0.08", description="VAT 8%"))
    db.add(SystemConfig(key="invoice_due_days", value="15", description="Due in 15 days"))
    db.commit()


def _make_invoice_setup(db, consumption):
    """Helper: tạo household + meter reading với mức tiêu thụ cho trước"""
    household = Household(
        id="h001",
        customer_code="KH001",
        full_name="Test User",
        address="Test Address",
        phone="0901234567",
        email="test@example.com",
        meter_number="MT001",
    )
    db.add(household)
    reading = MeterReading(
        id="r001",
        household_id=household.id,
        period="2026-09",
        old_reading=0,
        new_reading=consumption,
        consumption=consumption,
    )
    db.add(reading)
    db.commit()
    return reading


def test_calculate_invoice_tier_1_only(db, setup_price_tiers):
    """Tiêu thụ 30 kWh thuộc bậc 1 → 30 × 1678 = 50,340"""
    reading = _make_invoice_setup(db, 30)
    invoice = calculate_invoice(db, reading.id)

    expected_subtotal = 30 * 1678  # 50,340
    expected_vat = int((Decimal(expected_subtotal) * Decimal("0.08")).quantize(Decimal("1")))
    expected_total = expected_subtotal + expected_vat

    assert invoice.subtotal == expected_subtotal
    assert invoice.vat_amount == expected_vat
    assert invoice.total_amount == expected_total
    assert len(invoice.tier_details) == 1
    assert invoice.tier_details[0].tier_no == 1
    assert invoice.tier_details[0].kwh_applied == 30


def test_calculate_invoice_tier_2(db, setup_price_tiers):
    """Tiêu thụ 80 kWh thuộc bậc 2 (51-100) → 80 × 1734 = 138,720"""
    reading = _make_invoice_setup(db, 80)
    invoice = calculate_invoice(db, reading.id)

    assert invoice.subtotal == 80 * 1734
    assert len(invoice.tier_details) == 1
    assert invoice.tier_details[0].tier_no == 2
    assert invoice.tier_details[0].kwh_applied == 80


def test_calculate_invoice_tier_3(db, setup_price_tiers):
    """Tiêu thụ 150 kWh thuộc bậc 3 (101-200) → 150 × 2014 = 302,100"""
    reading = _make_invoice_setup(db, 150)
    invoice = calculate_invoice(db, reading.id)

    assert invoice.subtotal == 150 * 2014
    assert len(invoice.tier_details) == 1
    assert invoice.tier_details[0].tier_no == 3
    assert invoice.tier_details[0].kwh_applied == 150


def test_calculate_invoice_tier_4(db, setup_price_tiers):
    """Tiêu thụ 300 kWh thuộc bậc 4 (201-300) → 300 × 2536 = 760,800"""
    reading = _make_invoice_setup(db, 300)
    invoice = calculate_invoice(db, reading.id)

    assert invoice.subtotal == 300 * 2536
    assert len(invoice.tier_details) == 1
    assert invoice.tier_details[0].tier_no == 4
    assert invoice.tier_details[0].kwh_applied == 300


def test_calculate_invoice_tier_6(db, setup_price_tiers):
    """Tiêu thụ 500 kWh thuộc bậc 6 (>=401) → 500 × 2927 = 1,463,500"""
    reading = _make_invoice_setup(db, 500)
    invoice = calculate_invoice(db, reading.id)

    assert invoice.subtotal == 500 * 2927
    assert len(invoice.tier_details) == 1
    assert invoice.tier_details[0].tier_no == 6
    assert invoice.tier_details[0].kwh_applied == 500
