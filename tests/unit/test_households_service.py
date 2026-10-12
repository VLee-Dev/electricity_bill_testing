from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import ConflictError, NotFoundError
from app.features.households.service import (
    register_household,
    list_households,
    get_household,
    update_household,
    delete_household,
)


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def registration_data():
    return SimpleNamespace(
        customer_code="KH001",
        full_name="Nguyen Van A",
        address="Ha Noi",
        phone="0901234567",
        email="customer@example.com",
        meter_number="CT001",
        initial_password="Password123",
    )


@pytest.mark.parametrize(
    "results,error_code",
    [
        ([object()], "CUSTOMER_CODE_EXISTS"),
        ([None, object()], "METER_NUMBER_EXISTS"),
        ([None, None, object()], "EMAIL_EXISTS"),
    ],
)
def test_register_household_duplicate(db, registration_data, results, error_code):
    db.scalar.side_effect = results

    with pytest.raises(ConflictError) as exc:
        register_household(db, registration_data)

    assert exc.value.error_code == error_code
    db.commit.assert_not_called()


def test_register_household_success(db, registration_data):
    db.scalar.return_value = None

    with (
        patch(
            "app.features.households.service.hash_password",
            return_value="hashed-password",
        ) as hash_mock,
        patch(
            "app.features.households.service.send_welcome_email",
            return_value=True,
        ) as email_mock,
    ):
        household = register_household(db, registration_data)

    assert household.customer_code == "KH001"
    assert household.status == "active"

    hash_mock.assert_called_once_with("Password123")
    assert db.add.call_count == 2
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(household)

    customer = db.add.call_args_list[1].args[0]
    assert customer.household is household
    assert customer.password_hash == "hashed-password"
    assert customer.must_change_password is True

    email_mock.assert_called_once_with(
        db=db,
        recipient_email="customer@example.com",
        recipient_name="Nguyen Van A",
        customer_code="KH001",
        initial_password="Password123",
    )


def test_list_households_with_filters(db):
    expected = [object()]
    db.scalars.return_value.all.return_value = expected

    result = list_households(db, search="KH001", status="active")

    assert result == expected
    db.scalars.assert_called_once()

    query = db.scalars.call_args.args[0]
    query_text = str(query)

    assert "lower" in query_text.lower()
    assert "status" in query_text.lower()


def test_get_household_not_found(db):
    db.get.return_value = None

    with pytest.raises(NotFoundError):
        get_household(db, "missing-id")


def test_update_household_duplicate_email(db):
    household = SimpleNamespace(
        id="hh-1",
        email="old@example.com",
        phone="0900000000",
    )
    db.get.return_value = household
    db.scalar.return_value = object()

    data = SimpleNamespace(
        email="taken@example.com",
        phone=None,
    )

    with pytest.raises(ConflictError) as exc:
        update_household(db, "hh-1", data)

    assert exc.value.error_code == "EMAIL_EXISTS"
    db.commit.assert_not_called()


def test_update_household_duplicate_phone(db):
    household = SimpleNamespace(
        id="hh-1",
        email="old@example.com",
        phone="0900000000",
    )
    db.get.return_value = household
    db.scalar.return_value = object()

    data = SimpleNamespace(
        email=None,
        phone="0999999999",
    )

    with pytest.raises(ConflictError) as exc:
        update_household(db, "hh-1", data)

    assert exc.value.error_code == "PHONE_EXISTS"
    db.commit.assert_not_called()


def test_update_household_success(db):
    household = SimpleNamespace(
        id="hh-1",
        email="old@example.com",
        phone="0900000000",
        full_name="Old Name",
    )
    db.get.return_value = household
    db.scalar.return_value = None

    data = MagicMock()
    data.email = "new@example.com"
    data.phone = "0999999999"
    data.model_dump.return_value = {
        "email": "new@example.com",
        "phone": "0999999999",
        "full_name": "New Name",
    }

    result = update_household(db, "hh-1", data)

    assert result is household
    assert household.email == "new@example.com"
    assert household.phone == "0999999999"
    assert household.full_name == "New Name"

    data.model_dump.assert_called_once_with(exclude_unset=True)
    assert db.scalar.call_count == 2
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(household)


def test_delete_household_already_inactive(db):
    household = SimpleNamespace(
        id="hh-1",
        status="inactive",
        customer_code="KH001",
    )
    db.get.return_value = household

    result = delete_household(db, "hh-1")

    assert result["status"] == "inactive"
    db.scalar.assert_not_called()
    db.commit.assert_not_called()


def test_delete_household_with_unpaid_invoice(db):
    household = SimpleNamespace(
        id="hh-1",
        status="active",
        customer_code="KH001",
    )
    db.get.return_value = household
    db.scalar.return_value = object()

    with pytest.raises(ConflictError) as exc:
        delete_household(db, "hh-1")

    assert exc.value.error_code == "HOUSEHOLD_HAS_UNPAID_INVOICE"
    assert household.status == "active"
    db.commit.assert_not_called()


def test_delete_household_success(db):
    household = SimpleNamespace(
        id="hh-1",
        status="active",
        customer_code="KH001",
    )
    db.get.return_value = household
    db.scalar.return_value = None

    result = delete_household(db, "hh-1")

    assert result["id"] == "hh-1"
    assert result["status"] == "inactive"
    assert household.status == "inactive"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(household)
