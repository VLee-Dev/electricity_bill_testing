
"""
Integration tests for Customer Authentication API.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.household import Household
from app.security import hash_password


@pytest.fixture
def customer(db: Session) -> Customer:
    household = Household(
        customer_code="KH_TEST_001",
        full_name="Nguyen Van Test",
        address="Ha Noi",
        phone="0912345678",
        email="customer_test@example.com",
        meter_number="METER_TEST_001",
        status="active",
    )
    db.add(household)
    db.flush()

    customer = Customer(
        household_id=household.id,
        password_hash=hash_password("password123"),
        must_change_password=True,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def login(client: TestClient, password="password123"):
    return client.post(
        "/api/v1/customer/auth/login",
        json={
            "customer_code": "KH_TEST_001",
            "password": password,
        },
    )


def auth_headers(client: TestClient):
    response = login(client)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_customer_login_success(client: TestClient, customer: Customer):
    response = login(client)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_customer_login_wrong_password(client: TestClient, customer: Customer):
    response = login(client, "wrongpassword")

    assert response.status_code == 401
    assert response.json()["error_code"] == "INVALID_CREDENTIALS"


def test_customer_login_nonexistent(client: TestClient):
    response = client.post(
        "/api/v1/customer/auth/login",
        json={
            "customer_code": "KH_UNKNOWN",
            "password": "password123",
        },
    )

    assert response.status_code == 401
    assert response.json()["error_code"] == "INVALID_CREDENTIALS"


def test_customer_me_success(client: TestClient, customer: Customer):
    response = client.get(
        "/api/v1/customer/auth/me",
        headers=auth_headers(client),
    )

    assert response.status_code == 200
    assert response.json()["id"] == customer.id
    assert response.json()["household_id"] == customer.household_id


def test_customer_me_unauthorized(client: TestClient):
    response = client.get("/api/v1/customer/auth/me")

    assert response.status_code == 401


def test_customer_change_password_success(
    client: TestClient,
    customer: Customer,
):
    response = client.post(
        "/api/v1/customer/auth/change-password",
        headers=auth_headers(client),
        json={
            "current_password": "password123",
            "new_password": "newpassword456",
        },
    )

    assert response.status_code == 204

    old_login = login(client, "password123")
    assert old_login.status_code == 401

    new_login = login(client, "newpassword456")
    assert new_login.status_code == 200


def test_customer_change_password_wrong_current(
    client: TestClient,
    customer: Customer,
):
    response = client.post(
        "/api/v1/customer/auth/change-password",
        headers=auth_headers(client),
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword456",
        },
    )

    assert response.status_code == 401
    assert response.json()["error_code"] == "INVALID_CREDENTIALS"


def test_customer_change_password_too_short(
    client: TestClient,
    customer: Customer,
):
    response = client.post(
        "/api/v1/customer/auth/change-password",
        headers=auth_headers(client),
        json={
            "current_password": "password123",
            "new_password": "123",
        },
    )

    assert response.status_code == 422
