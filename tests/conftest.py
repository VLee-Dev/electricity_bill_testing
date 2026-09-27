import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Cho phép import app.* khi chạy test từ root
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

# Import models để SQLAlchemy đăng ký tất cả table với Base.metadata
from app.models import *  # noqa: F401, F403
import app.database as _db_module
from app.database import Base, get_db
from app.main import app


# Dùng SQLite in-memory cho test, dùng StaticPool để mọi connection
# dùng chung 1 database.
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function", autouse=True)
def _override_engine():
    """Override engine trong app.database để trỏ về SQLite in-memory."""
    # Tạo schema ngay trên engine test
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    original_engine = _db_module.engine
    original_sessionlocal = _db_module.SessionLocal
    _db_module.engine = test_engine
    _db_module.SessionLocal = TestingSessionLocal
    try:
        yield
    finally:
        _db_module.engine = original_engine
        _db_module.SessionLocal = original_sessionlocal
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Session dùng engine test (cùng database)."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Test client với dependency override cho DB session."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
