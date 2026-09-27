"""
Integration tests for Admin Auth API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.admin import Admin
from app.security import hash_password


@pytest.fixture
def admin(db: Session) -> Admin:
    """Create test admin"""
    admin = Admin(
        id="test-admin-001",
        username="testadmin",
        password_hash=hash_password("password123"),
        full_name="Test Admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def test_admin_login_success(client: TestClient, admin: Admin):
    """Test admin login with valid credentials"""
    response = client.post(
        "/api/v1/admin/auth/login",
        json={"username": "testadmin", "password": "password123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_admin_login_invalid_credentials(client: TestClient, admin: Admin):
    """Test admin login with invalid credentials"""
    response = client.post(
        "/api/v1/admin/auth/login",
        json={"username": "testadmin", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    data = response.json()
    assert data["error_code"] == "INVALID_CREDENTIALS"


def test_admin_login_nonexistent_user(client: TestClient):
    """Test admin login with non-existent user"""
    response = client.post(
        "/api/v1/admin/auth/login",
        json={"username": "nonexistent", "password": "password123"}
    )

    assert response.status_code == 401


def test_admin_me(client: TestClient, admin: Admin):
    """Test getting admin info"""
    # Login first
    login_response = client.post(
        "/api/v1/admin/auth/login",
        json={"username": "testadmin", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    # Get admin info
    response = client.get(
        "/api/v1/admin/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testadmin"
    assert data["full_name"] == "Test Admin"


def test_admin_me_unauthorized(client: TestClient):
    """Test getting admin info without token"""
    response = client.get("/api/v1/admin/auth/me")

    assert response.status_code == 401
