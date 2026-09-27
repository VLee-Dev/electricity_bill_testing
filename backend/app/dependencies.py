from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import ForbiddenError, UnauthorizedError
from app.models.admin import Admin
from app.models.customer import Customer
from app.security import decode_token


def get_current_admin(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
) -> Admin:
    """
    Dependency để lấy Admin hiện tại từ JWT token
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Cần đăng nhập để sử dụng chức năng này.")

    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)

    if payload.get("type") != "admin":
        raise ForbiddenError("Chức năng này chỉ dành cho Admin.")

    admin = db.get(Admin, payload.get("sub"))
    if not admin:
        raise UnauthorizedError("Tài khoản không tồn tại.")

    return admin


def get_current_customer(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
) -> Customer:
    """
    Dependency để lấy Customer hiện tại từ JWT token
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Cần đăng nhập để sử dụng chức năng này.")

    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)

    if payload.get("type") != "customer":
        raise ForbiddenError("Chức năng này chỉ dành cho Customer.")

    customer = db.get(Customer, payload.get("sub"))
    if not customer:
        raise UnauthorizedError("Tài khoản không tồn tại.")

    return customer
