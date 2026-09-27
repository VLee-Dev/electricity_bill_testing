"""Hash mật khẩu bằng bcrypt (trực tiếp, không qua passlib để tránh xung đột version).
JWT helpers.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import settings
from app.exceptions import UnauthorizedError


def hash_password(password: str) -> str:
    """Hash mật khẩu bằng bcrypt"""
    # bcrypt chỉ chấp nhận tối đa 72 bytes
    pwd = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu với hash"""
    pwd = plain_password.encode("utf-8")[:72]
    try:
        return bcrypt.checkpw(pwd, hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict) -> str:
    """
    Tạo JWT access token
    data phải chứa: {"sub": user_id, "type": "admin" hoặc "customer"}
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm="HS256")


def decode_token(token: str) -> dict:
    """Giải mã JWT token"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        raise UnauthorizedError("Token không hợp lệ hoặc đã hết hạn.")
