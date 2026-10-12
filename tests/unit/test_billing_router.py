from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.features.billing_new.router import (
    create_invoice,
    get_invoices,
    get_invoice_detail,
)


def test_create_invoice_calls_calculation():
    db = MagicMock()
    data = SimpleNamespace(meter_reading_id="reading-1")
    invoice = SimpleNamespace(id="invoice-1")
    expected = object()
    db.scalar.return_value = expected

    with patch(
        "app.features.billing_new.router.calculate_invoice",
        return_value=invoice,
    ) as service:
        result = create_invoice(data, db=db)

    service.assert_called_once_with(db, "reading-1")
    db.refresh.assert_called_once_with(invoice)
    assert result is expected


def test_create_invoice_loads_tier_details():
    db = MagicMock()
    data = SimpleNamespace(meter_reading_id="reading-2")
    invoice = SimpleNamespace(id="invoice-2")

    with patch(
        "app.features.billing_new.router.calculate_invoice",
        return_value=invoice,
    ):
        create_invoice(data, db=db)

    db.query.assert_called_once()
    db.query.return_value.options.assert_called_once()
    db.query.return_value.options.return_value.where.assert_called_once()
    db.scalar.assert_called_once()


def test_get_invoices_with_filters():
    db = MagicMock()
    expected = [object(), object()]

    with patch(
        "app.features.billing_new.router.list_invoices",
        return_value=expected,
    ) as service:
        result = get_invoices(
            household_id="household-1",
            status="unpaid",
            db=db,
        )

    assert result is expected
    service.assert_called_once_with(
        db, "household-1", "unpaid"
    )


def test_get_invoices_empty():
    db = MagicMock()

    with patch(
        "app.features.billing_new.router.list_invoices",
        return_value=[],
    ):
        result = get_invoices(
            household_id=None,
            status=None,
            db=db,
        )

    assert result == []


def test_get_invoice_detail():
    db = MagicMock()
    invoice = SimpleNamespace(id="invoice-1")
    expected = object()
    db.scalar.return_value = expected

    with patch(
        "app.features.billing_new.router.get_invoice",
        return_value=invoice,
    ) as service:
        result = get_invoice_detail(
            invoice_id="invoice-1",
            db=db,
        )

    service.assert_called_once_with(db, "invoice-1")
    assert result is expected


def test_get_invoice_detail_loads_tier_details():
    db = MagicMock()

    with patch(
        "app.features.billing_new.router.get_invoice",
        return_value=SimpleNamespace(id="invoice-2"),
    ):
        get_invoice_detail(
            invoice_id="invoice-2",
            db=db,
        )

    db.query.assert_called_once()
    db.query.return_value.options.assert_called_once()
    db.query.return_value.options.return_value.where.assert_called_once()
    db.scalar.assert_called_once()
