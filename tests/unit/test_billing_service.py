from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import ConflictError, NotFoundError
from app.features.billing_new.service import (
    calculate_invoice,
    get_invoice,
    list_invoices,
)
from app.models.invoice import Invoice
from app.models.meter_reading import MeterReading


def make_reading(consumption=80):
    return SimpleNamespace(
        id="reading-1",
        household_id="household-1",
        old_reading=100,
        new_reading=100 + consumption,
        consumption=consumption,
    )


def make_tier(number, start, end, price):
    return SimpleNamespace(
        tier_no=number,
        kwh_from=start,
        kwh_to=end,
        unit_price=price,
    )


def make_db(consumption=80, tiers=None, vat=None, due_days=None):
    db = MagicMock()
    db.get.return_value = make_reading(consumption)

    if tiers is None:
        tiers = [
            make_tier(1, 0, 50, 2000),
            make_tier(2, 51, 100, 2500),
            make_tier(3, 101, None, 3000),
        ]

    db.scalars.return_value.all.return_value = tiers
    db.scalar.side_effect = [
        None,
        SimpleNamespace(value=vat) if vat is not None else None,
        SimpleNamespace(value=due_days) if due_days is not None else None,
    ]
    return db


def test_calculate_invoice_success():
    db = make_db(consumption=80)

    with patch(
        "app.features.billing_new.service.send_invoice_email"
    ) as send_email:
        invoice = calculate_invoice(db, "reading-1")

    assert isinstance(invoice, Invoice)
    assert invoice.subtotal == 200000
    assert invoice.vat_amount == 16000
    assert invoice.total_amount == 216000
    assert invoice.status == "unpaid"
    assert invoice.due_date == date.today() + timedelta(days=15)

    assert len(invoice.tier_details) == 1
    assert invoice.tier_details[0].tier_no == 2
    assert invoice.tier_details[0].kwh_applied == 80

    db.add.assert_called_once_with(invoice)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(invoice)
    send_email.assert_called_once_with(invoice, db)


def test_calculate_invoice_reading_not_found():
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(NotFoundError):
        calculate_invoice(db, "missing")

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_calculate_invoice_already_exists():
    db = MagicMock()
    db.get.return_value = make_reading()
    db.scalar.return_value = MagicMock(spec=Invoice)

    with pytest.raises(ConflictError) as exc:
        calculate_invoice(db, "reading-1")

    assert exc.value.error_code == "INVOICE_EXISTS"
    db.commit.assert_not_called()


def test_calculate_invoice_no_price_tiers():
    db = make_db(tiers=[])

    with pytest.raises(NotFoundError):
        calculate_invoice(db, "reading-1")

    db.commit.assert_not_called()


def test_calculate_invoice_no_matching_tier():
    db = make_db(
        consumption=500,
        tiers=[make_tier(1, 0, 50, 2000)],
    )

    with pytest.raises(NotFoundError):
        calculate_invoice(db, "reading-1")

    db.commit.assert_not_called()


def test_calculate_invoice_last_tier():
    db = make_db(consumption=500)

    with patch("app.features.billing_new.service.send_invoice_email"):
        invoice = calculate_invoice(db, "reading-1")

    assert invoice.tier_details[0].tier_no == 3
    assert invoice.subtotal == 1500000
    assert invoice.total_amount == 1620000


def test_calculate_invoice_custom_vat_and_due_days():
    db = make_db(consumption=50, vat="0.10", due_days="30")

    with patch("app.features.billing_new.service.send_invoice_email"):
        invoice = calculate_invoice(db, "reading-1")

    assert invoice.subtotal == 100000
    assert invoice.vat_amount == 10000
    assert invoice.total_amount == 110000
    assert invoice.due_date == date.today() + timedelta(days=30)


def test_calculate_invoice_email_failure_does_not_rollback():
    db = make_db()

    with patch(
        "app.features.billing_new.service.send_invoice_email",
        side_effect=RuntimeError("SMTP unavailable"),
    ):
        invoice = calculate_invoice(db, "reading-1")

    assert isinstance(invoice, Invoice)
    db.commit.assert_called_once()


def test_calculate_invoice_zero_consumption():
    db = make_db(consumption=0)

    with patch("app.features.billing_new.service.send_invoice_email"):
        invoice = calculate_invoice(db, "reading-1")

    assert invoice.subtotal == 0
    assert invoice.vat_amount == 0
    assert invoice.total_amount == 0
    assert invoice.tier_details[0].tier_no == 1


def test_get_invoice_success():
    db = MagicMock()
    invoice = MagicMock(spec=Invoice)
    db.get.return_value = invoice

    assert get_invoice(db, "invoice-1") is invoice
    db.get.assert_called_once_with(Invoice, "invoice-1")


def test_get_invoice_not_found():
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(NotFoundError):
        get_invoice(db, "missing")


def test_list_invoices_without_filters():
    db = MagicMock()
    invoices = [MagicMock(), MagicMock()]
    db.scalars.return_value.all.return_value = invoices

    assert list_invoices(db) == invoices
    db.scalars.assert_called_once()


def test_list_invoices_household_filter():
    db = MagicMock()
    db.scalars.return_value.all.return_value = []

    assert list_invoices(db, household_id="household-1") == []
    db.scalars.assert_called_once()


def test_list_invoices_status_filter():
    db = MagicMock()
    db.scalars.return_value.all.return_value = []

    assert list_invoices(db, status="unpaid") == []
    db.scalars.assert_called_once()


def test_list_invoices_both_filters():
    db = MagicMock()
    db.scalars.return_value.all.return_value = []

    assert list_invoices(
        db,
        household_id="household-1",
        status="paid",
    ) == []
    db.scalars.assert_called_once()
