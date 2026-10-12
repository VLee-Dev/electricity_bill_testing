
from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import ValidationError
from app.features.customer_auth.router import customer_household
from app.features.customer_auth.service import change_customer_password


# ============================================================
# CUSTOMER AUTH ROUTER
# ============================================================

def test_customer_household_returns_associated_household():
    """
    CAR001: Customer can retrieve their associated household.
    Covers customer_auth/router.py line 39.
    """
    customer = MagicMock()
    household = MagicMock()
    customer.household = household

    result = customer_household(customer=customer)

    assert result is household


# ============================================================
# CUSTOMER AUTH SERVICE
# ============================================================

def test_change_password_rejects_short_new_password():
    """
    CAS001: New password shorter than 6 characters is rejected.
    Covers customer_auth/service.py line 39.
    """
    db = MagicMock()
    customer = MagicMock()
    customer.password_hash = "existing-password-hash"

    with patch(
        "app.features.customer_auth.service.verify_password",
        return_value=True,
    ) as mock_verify:
        with pytest.raises(ValidationError):
            change_customer_password(
                db=db,
                customer=customer,
                current_password="old-password",
                new_password="12345",
            )

    mock_verify.assert_called_once_with(
        "old-password",
        "existing-password-hash",
    )

    db.commit.assert_not_called()
