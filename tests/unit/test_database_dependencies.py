
from unittest.mock import MagicMock, patch

import pytest

from app.database import get_db
from app.dependencies import get_current_admin, get_current_customer
from app.exceptions import ForbiddenError, UnauthorizedError
from app.models.admin import Admin
from app.models.customer import Customer


# ============================================================
# DATABASE TESTS
# ============================================================

def test_get_db_session_lifecycle():
    """DB001: Database session is opened and closed correctly."""
    session = MagicMock()
    context_manager = MagicMock()
    context_manager.__enter__.return_value = session

    with patch(
        "app.database.SessionLocal",
        return_value=context_manager,
    ) as session_factory:
        generator = get_db()

        result = next(generator)

        assert result is session
        session_factory.assert_called_once()
        context_manager.__enter__.assert_called_once()

        with pytest.raises(StopIteration):
            next(generator)

        context_manager.__exit__.assert_called_once()


# ============================================================
# ADMIN DEPENDENCY TESTS
# ============================================================

def test_get_current_admin_without_token():
    """DEP001: Reject requests without an authorization token."""
    db = MagicMock()

    with pytest.raises(UnauthorizedError):
        get_current_admin(authorization=None, db=db)

    db.get.assert_not_called()


def test_get_current_admin_not_found():
    """DEP002: Reject token if admin account does not exist."""
    db = MagicMock()
    db.get.return_value = None

    with patch(
        "app.dependencies.decode_token",
        return_value={"type": "admin", "sub": "admin-missing"},
    ):
        with pytest.raises(UnauthorizedError):
            get_current_admin(
                authorization="Bearer valid-token",
                db=db,
            )

    db.get.assert_called_once_with(Admin, "admin-missing")


def test_get_current_admin_success():
    """DEP003: Return authenticated admin."""
    db = MagicMock()
    admin = MagicMock(spec=Admin)
    db.get.return_value = admin

    with patch(
        "app.dependencies.decode_token",
        return_value={"type": "admin", "sub": "admin-1"},
    ):
        result = get_current_admin(
            authorization="Bearer valid-token",
            db=db,
        )

    assert result is admin
    db.get.assert_called_once_with(Admin, "admin-1")


def test_get_current_admin_wrong_token_type():
    """DEP007: Customer token cannot access admin functions."""
    db = MagicMock()

    with patch(
        "app.dependencies.decode_token",
        return_value={"type": "customer", "sub": "customer-1"},
    ):
        with pytest.raises(ForbiddenError):
            get_current_admin(
                authorization="Bearer customer-token",
                db=db,
            )

    db.get.assert_not_called()


# ============================================================
# CUSTOMER DEPENDENCY TESTS
# ============================================================

def test_get_current_customer_without_token():
    """DEP004: Reject requests without an authorization token."""
    db = MagicMock()

    with pytest.raises(UnauthorizedError):
        get_current_customer(authorization=None, db=db)

    db.get.assert_not_called()


def test_get_current_customer_not_found():
    """DEP005: Reject token if customer account does not exist."""
    db = MagicMock()
    db.get.return_value = None

    with patch(
        "app.dependencies.decode_token",
        return_value={"type": "customer", "sub": "customer-missing"},
    ):
        with pytest.raises(UnauthorizedError):
            get_current_customer(
                authorization="Bearer valid-token",
                db=db,
            )

    db.get.assert_called_once_with(Customer, "customer-missing")


def test_get_current_customer_success():
    """DEP006: Return authenticated customer."""
    db = MagicMock()
    customer = MagicMock(spec=Customer)
    db.get.return_value = customer

    with patch(
        "app.dependencies.decode_token",
        return_value={"type": "customer", "sub": "customer-1"},
    ):
        result = get_current_customer(
            authorization="Bearer valid-token",
            db=db,
        )

    assert result is customer
    db.get.assert_called_once_with(Customer, "customer-1")


def test_get_current_customer_wrong_token_type():
    """DEP008: Admin token cannot access customer functions."""
    db = MagicMock()

    with patch(
        "app.dependencies.decode_token",
        return_value={"type": "admin", "sub": "admin-1"},
    ):
        with pytest.raises(ForbiddenError):
            get_current_customer(
                authorization="Bearer admin-token",
                db=db,
            )

    db.get.assert_not_called()
