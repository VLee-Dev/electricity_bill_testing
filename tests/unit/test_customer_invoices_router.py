from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.features.customer_invoices.router import (
    list_my_invoices,
    get_my_invoice,
    pay_invoice,
)


def test_list_my_invoices():
    db = MagicMock()
    customer = SimpleNamespace(id="customer-1")
    expected = [object(), object()]

    with patch(
        "app.features.customer_invoices.router.get_customer_invoices",
        return_value=expected,
    ) as service:
        result = list_my_invoices(customer=customer, db=db)

    assert result is expected
    service.assert_called_once_with(db, customer)


def test_list_my_invoices_empty():
    db = MagicMock()
    customer = SimpleNamespace(id="customer-2")

    with patch(
        "app.features.customer_invoices.router.get_customer_invoices",
        return_value=[],
    ) as service:
        result = list_my_invoices(customer=customer, db=db)

    assert result == []
    service.assert_called_once_with(db, customer)


def test_get_my_invoice():
    db = MagicMock()
    customer = SimpleNamespace(id="customer-1")
    invoice = SimpleNamespace(id="invoice-1")
    expected = object()
    db.scalar.return_value = expected

    with patch(
        "app.features.customer_invoices.router.get_customer_invoice",
        return_value=invoice,
    ) as service:
        result = get_my_invoice(
            invoice_id="invoice-1",
            customer=customer,
            db=db,
        )

    service.assert_called_once_with(
        db, "invoice-1", customer
    )
    db.scalar.assert_called_once()
    assert result is expected


def test_get_my_invoice_loads_relations():
    db = MagicMock()
    customer = SimpleNamespace(id="customer-2")

    with patch(
        "app.features.customer_invoices.router.get_customer_invoice",
        return_value=SimpleNamespace(id="invoice-2"),
    ):
        get_my_invoice(
            invoice_id="invoice-2",
            customer=customer,
            db=db,
        )

    db.scalar.assert_called_once()

    query = db.scalar.call_args.args[0]
    query_text = str(query)

    assert "invoices" in query_text.lower()
    assert "invoice-2" in str(
        query.compile(
            compile_kwargs={"literal_binds": True}
        )
    )


def test_pay_invoice_calls_service():
    db = MagicMock()
    customer = SimpleNamespace(id="customer-1")
    data = SimpleNamespace(method="simulated")
    expected = object()

    with patch(
        "app.features.customer_invoices.router.pay_invoice_simulated",
        return_value=expected,
    ) as service:
        result = pay_invoice(
            invoice_id="invoice-1",
            data=data,
            customer=customer,
            db=db,
        )

    service.assert_called_once_with(
        db, "invoice-1", customer
    )
    assert result is expected


def test_pay_invoice_returns_payment():
    db = MagicMock()
    customer = SimpleNamespace(id="customer-2")
    data = SimpleNamespace(method="simulated")
    payment = SimpleNamespace(
        id="payment-1",
        invoice_id="invoice-2",
        status="success",
    )

    with patch(
        "app.features.customer_invoices.router.pay_invoice_simulated",
        return_value=payment,
    ):
        result = pay_invoice(
            invoice_id="invoice-2",
            data=data,
            customer=customer,
            db=db,
        )

    assert result is payment
    assert result.invoice_id == "invoice-2"
    assert result.status == "success"
