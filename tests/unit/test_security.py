"""
Unit tests for security module
"""

import base64
import json
from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.config import settings
from app.exceptions import UnauthorizedError


# ============================================================
# EXISTING SECURITY TEST CASES (SEC001 - SEC005)
# ============================================================

def test_hash_password():
    """SEC001: Test password hashing."""
    password = "test123"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 0


def test_verify_password():
    """SEC002: Test password verification."""
    password = "test123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_create_access_token():
    """SEC003: Test JWT token creation."""
    data = {"sub": "user123", "type": "admin"}
    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=["HS256"],
    )

    assert payload["sub"] == "user123"
    assert payload["type"] == "admin"
    assert "exp" in payload


def test_decode_token_valid():
    """SEC004: Test decoding valid token."""
    data = {"sub": "user123", "type": "customer"}
    token = create_access_token(data)

    payload = decode_token(token)

    assert payload["sub"] == "user123"
    assert payload["type"] == "customer"


def test_decode_token_invalid():
    """SEC005: Test decoding invalid token."""
    with pytest.raises(UnauthorizedError) as exc_info:
        decode_token("invalid.token.here")

    assert "không hợp lệ" in str(exc_info.value.message)


# ============================================================
# NEW SECURITY TEST CASES (SEC006 - SEC010)
# ============================================================

def test_decode_token_expired():
    """SEC006: Expired JWT token must be rejected."""
    payload = {
        "sub": "user123",
        "type": "admin",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm="HS256",
    )

    with pytest.raises(UnauthorizedError) as exc_info:
        decode_token(token)

    assert "hết hạn" in str(exc_info.value.message)


def test_decode_token_wrong_signature():
    """SEC007: JWT signed with wrong secret must be rejected."""
    payload = {
        "sub": "user123",
        "type": "admin",
    }

    token = jwt.encode(
        payload,
        "different-secret-key",
        algorithm="HS256",
    )

    with pytest.raises(UnauthorizedError):
        decode_token(token)


def test_decode_token_tampered():
    """SEC008: Modified JWT payload must be rejected."""
    token = create_access_token({
        "sub": "user123",
        "type": "customer",
    })

    header, payload, signature = token.split(".")

    padded_payload = payload + "=" * (-len(payload) % 4)
    decoded_payload = json.loads(
        base64.urlsafe_b64decode(padded_payload)
    )

    # Attempt to change customer role to admin
    decoded_payload["type"] = "admin"

    modified_payload = json.dumps(
        decoded_payload,
        separators=(",", ":"),
    ).encode("utf-8")

    encoded_payload = (
        base64.urlsafe_b64encode(modified_payload)
        .rstrip(b"=")
        .decode("utf-8")
    )

    tampered_token = f"{header}.{encoded_payload}.{signature}"

    with pytest.raises(UnauthorizedError):
        decode_token(tampered_token)


def test_verify_password_invalid_hash():
    """SEC009: Invalid password hash must return False."""
    result = verify_password(
        "test123",
        "invalid-hash",
    )

    assert result is False


def test_create_access_token_expiration():
    """SEC010: JWT expiration time must be correct."""
    before = datetime.now(timezone.utc)

    token = create_access_token({
        "sub": "user123",
        "type": "admin",
    })

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=["HS256"],
    )

    expiration = datetime.fromtimestamp(
        payload["exp"],
        tz=timezone.utc,
    )

    expected_expiration = before + timedelta(
        minutes=settings.jwt_expire_minutes
    )

    difference = abs(
        (expiration - expected_expiration).total_seconds()
    )

    assert difference <= 5