"""
Integration tests for Household Management API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.admin import Admin
from app.models.household import Household
from app.security import create_access_token, hash_password


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


@pytest.fixture
def admin_token(admin: Admin) -> str:
    """Generate admin token"""
    return create_access_token({"sub": admin.id, "type": "admin"})


def test_create_household_success(client: TestClient, admin_token: str):
    """Test creating a new household"""
    response = client.post(
        "/api/v1/admin/households",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "customer_code": "KH001",
            "full_name": "Nguyễn Văn A",
            "address": "123 Test St",
            "phone": "0901234567",
            "email": "test@example.com",
            "meter_number": "MT001",
            "initial_password": "password123"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["customer_code"] == "KH001"
    assert data["full_name"] == "Nguyễn Văn A"
    assert data["status"] == "active"


def test_create_household_duplicate_customer_code(client: TestClient, admin_token: str, db: Session):
    """Test creating household with duplicate customer_code"""
    # Create first household
    household = Household(
        id="h001",
        customer_code="KH001",
        full_name="Test User",
        address="Test Address",
        phone="0901111111",
        email="test1@example.com",
        meter_number="MT001"
    )
    db.add(household)
    db.commit()

    # Try to create duplicate
    response = client.post(
        "/api/v1/admin/households",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "customer_code": "KH001",
            "full_name": "Another User",
            "address": "Another Address",
            "phone": "0902222222",
            "email": "test2@example.com",
            "meter_number": "MT002",
            "initial_password": "password123"
        }
    )

    assert response.status_code == 409
    data = response.json()
    assert data["error_code"] == "CUSTOMER_CODE_EXISTS"


def test_list_households(client: TestClient, admin_token: str, db: Session):
    """Test listing households"""
    # Create test households
    households = [
        Household(
            id=f"h00{i}",
            customer_code=f"KH00{i}",
            full_name=f"User {i}",
            address=f"Address {i}",
            phone=f"090123456{i}",
            email=f"user{i}@example.com",
            meter_number=f"MT00{i}"
        )
        for i in range(1, 4)
    ]
    db.add_all(households)
    db.commit()

    response = client.get(
        "/api/v1/admin/households",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_list_households_with_search(client: TestClient, admin_token: str, db: Session):
    """Test listing households with search"""
    households = [
        Household(
            id="h001",
            customer_code="KH001",
            full_name="Nguyễn Văn A",
            address="Address 1",
            phone="0901234567",
            email="user1@example.com",
            meter_number="MT001"
        ),
        Household(
            id="h002",
            customer_code="KH002",
            full_name="Trần Thị B",
            address="Address 2",
            phone="0909876543",
            email="user2@example.com",
            meter_number="MT002"
        )
    ]
    db.add_all(households)
    db.commit()

    response = client.get(
        "/api/v1/admin/households?search=KH001",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["customer_code"] == "KH001"


# === Tests mới: PUT (sửa) + DELETE (soft) ===

def test_update_household_success(client: TestClient, admin_token: str, db: Session):
    """PUT /admin/households/{id}: cập nhật 1 số field, các field khác giữ nguyên."""
    household = Household(
        id="h-upd-1",
        customer_code="KH001",
        full_name="Old Name",
        address="Old Address",
        phone="0901111111",
        email="upd@example.com",
        meter_number="MT001"
    )
    db.add(household)
    db.commit()

    response = client.put(
        "/api/v1/admin/households/h-upd-1",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"full_name": "New Name", "address": "New Address"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "New Name"
    assert data["address"] == "New Address"
    # các field không gửi lên phải giữ nguyên
    assert data["phone"] == "0901111111"
    assert data["email"] == "upd@example.com"
    assert data["customer_code"] == "KH001"  # không cho sửa


def test_update_household_duplicate_email(client: TestClient, admin_token: str, db: Session):
    """PUT: trùng email với hộ khác → 409."""
    db.add_all([
        Household(id="h-a2", customer_code="KHA2", full_name="A2", address="A",
                  phone="0901111111", email="same@example.com", meter_number="MTA2"),
        Household(id="h-b2", customer_code="KHB2", full_name="B2", address="B",
                  phone="0902222222", email="other@example.com", meter_number="MTB2"),
    ])
    db.commit()

    response = client.put(
        "/api/v1/admin/households/h-b2",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"email": "same@example.com"}
    )
    assert response.status_code == 409
    assert response.json()["error_code"] == "EMAIL_EXISTS"


def test_soft_delete_household_success(client: TestClient, admin_token: str, db: Session):
    """DELETE /admin/households/{id}: không có invoice → chuyển sang inactive."""
    household = Household(
        id="h-del-1",
        customer_code="KHDEL1",
        full_name="Del User",
        address="Test",
        phone="0903333333",
        email="del@example.com",
        meter_number="MTDEL1"
    )
    db.add(household)
    db.commit()

    response = client.delete(
        "/api/v1/admin/households/h-del-1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "inactive"

    # Verify trong DB đã là inactive
    db.expire_all()
    fresh = db.get(Household, "h-del-1")
    assert fresh.status == "inactive"


def test_soft_delete_household_idempotent(client: TestClient, admin_token: str, db: Session):
    """DELETE household đã inactive rồi → trả 200 (idempotent)."""
    household = Household(
        id="h-del-2",
        customer_code="KHDEL2",
        full_name="Already Inactive",
        address="Test",
        phone="0904444444",
        email="del2@example.com",
        meter_number="MTDEL2",
        status="inactive"
    )
    db.add(household)
    db.commit()

    response = client.delete(
        "/api/v1/admin/households/h-del-2",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
