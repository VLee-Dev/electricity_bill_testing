"""
Unit tests for security module
"""
import pytest
from jose import jwt

from app.security import create_access_token, decode_token, hash_password, verify_password
from app.config import settings
from app.exceptions import UnauthorizedError


def test_hash_password():
    """Test password hashing"""
    password = "test123"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 0


def test_verify_password():
    """Test password verification"""
    password = "test123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_create_access_token():
    """Test JWT token creation"""
    data = {"sub": "user123", "type": "admin"}
    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0

    # Decode without verification to check payload
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
    assert payload["sub"] == "user123"
    assert payload["type"] == "admin"
    assert "exp" in payload


def test_decode_token_valid():
    """Test decoding valid token"""
    data = {"sub": "user123", "type": "customer"}
    token = create_access_token(data)

    payload = decode_token(token)
    assert payload["sub"] == "user123"
    assert payload["type"] == "customer"


def test_decode_token_invalid():
    """Test decoding invalid token"""
    with pytest.raises(UnauthorizedError) as exc_info:
        decode_token("invalid.token.here")

    assert "không hợp lệ" in str(exc_info.value.message)
