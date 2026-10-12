from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.features.customer_invoices.service import (
    get_customer_invoices,
    get_customer_invoice,
    pay_invoice_simulated,
)
from app.models.invoice import Invoice
from app.models.payment import Payment


# ============================================================
# TEST HELPERS
# ============================================================

def make_customer():
    return SimpleNamespace(household_id="household-1")


def make_invoice(status="unpaid", household_id="household-1"):
    return SimpleNamespace(
        id="invoice-1",
        household_id=household_id,
        status=status,
        total_amount=216000,
    )


# ============================================================
# EXISTING TEST CASES (CI001 - CI008)
# ============================================================

def test_get_customer_invoices_success():
    db = MagicMock()
    customer = make_customer()
    invoices = [make_invoice(), make_invoice()]
    db.scalars.return_value.all.return_value = invoices

    result = get_customer_invoices(db, customer)

    assert result == invoices
    db.scalars.assert_called_once()


def test_get_customer_invoices_empty():
    db = MagicMock()
    db.scalars.return_value.all.return_value = []

    result = get_customer_invoices(db, make_customer())

    assert result == []


def test_get_customer_invoice_success():
    db = MagicMock()
    invoice = make_invoice()
    db.get.return_value = invoice

    result = get_customer_invoice(db, "invoice-1", make_customer())

    assert result is invoice
    db.get.assert_called_once_with(Invoice, "invoice-1")


def test_get_customer_invoice_not_found():
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(NotFoundError):
        get_customer_invoice(db, "missing", make_customer())


def test_get_customer_invoice_forbidden():
    db = MagicMock()
    db.get.return_value = make_invoice(household_id="household-2")

    with pytest.raises(ForbiddenError):
        get_customer_invoice(db, "invoice-1", make_customer())


def test_pay_invoice_simulated_success():
    db = MagicMock()
    invoice = make_invoice()
    db.get.return_value = invoice

    result = pay_invoice_simulated(db, "invoice-1", make_customer())

    assert isinstance(result, Payment)
    assert result.invoice_id == "invoice-1"
    assert result.amount == 216000
    assert result.method == "online_simulated"
    assert result.confirmed_by is None
    assert invoice.status == "paid"

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_pay_invoice_simulated_already_paid():
    db = MagicMock()
    db.get.return_value = make_invoice(status="paid")

    with pytest.raises(ConflictError) as exc:
        pay_invoice_simulated(db, "invoice-1", make_customer())

    assert exc.value.error_code == "INVOICE_ALREADY_PAID"
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_pay_invoice_simulated_forbidden():
    db = MagicMock()
    db.get.return_value = make_invoice(household_id="household-2")

    with pytest.raises(ForbiddenError):
        pay_invoice_simulated(db, "invoice-1", make_customer())

    db.add.assert_not_called()
    db.commit.assert_not_called()


# ============================================================
# NEW TEST CASES (CI009 - CI011)
# ============================================================

def test_pay_invoice_simulated_not_found():
    """CI009: Cannot pay an invoice that does not exist."""
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(NotFoundError):
        pay_invoice_simulated(db, "missing", make_customer())

    db.get.assert_called_once_with(Invoice, "missing")
    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_pay_invoice_simulated_zero_amount():
    """CI010: Verify current behavior for a zero-amount invoice."""
    db = MagicMock()

    invoice = make_invoice(status="unpaid")
    invoice.total_amount = 0

    db.get.return_value = invoice

    result = pay_invoice_simulated(
        db,
        "invoice-1",
        make_customer(),
    )

    assert isinstance(result, Payment)
    assert result.invoice_id == "invoice-1"
    assert result.amount == 0
    assert result.method == "online_simulated"
    assert result.confirmed_by is None
    assert invoice.status == "paid"

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_get_customer_invoices_query_filters_household():
    """CI011: Query must filter invoices by the customer's household."""
    db = MagicMock()
    customer = make_customer()

    db.scalars.return_value.all.return_value = []

    result = get_customer_invoices(db, customer)

    assert result == []
    db.scalars.assert_called_once()

    query = db.scalars.call_args.args[0]
    query_text = str(query).lower()

    assert "household_id" in query_text
    assert "where" in query_text
    assert "order by" in query_text

    compiled = query.compile()
    assert customer.household_id in compiled.params.values()