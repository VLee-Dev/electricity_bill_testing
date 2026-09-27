from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.exceptions import UnauthorizedError, ValidationError
from app.models.customer import Customer
from app.models.household import Household
from app.security import hash_password, verify_password


def authenticate_customer(db: Session, customer_code: str, password: str) -> Customer:
    """
    Xác thực Customer bằng customer_code (từ household) + password
    """
    household = db.scalar(select(Household).where(Household.customer_code == customer_code))
    if not household or not household.customer:
        error = UnauthorizedError("Mã khách hàng hoặc mật khẩu không đúng.")
        error.error_code = "INVALID_CREDENTIALS"
        raise error

    customer = household.customer
    if not verify_password(password, customer.password_hash):
        error = UnauthorizedError("Mã khách hàng hoặc mật khẩu không đúng.")
        error.error_code = "INVALID_CREDENTIALS"
        raise error

    return customer


def change_customer_password(db: Session, customer: Customer, current_password: str, new_password: str):
    """
    Đổi mật khẩu Customer
    """
    if not verify_password(current_password, customer.password_hash):
        error = UnauthorizedError("Mật khẩu hiện tại không đúng.")
        error.error_code = "INVALID_CREDENTIALS"
        raise error

    if len(new_password) < 6:
        raise ValidationError("Mật khẩu mới phải có ít nhất 6 ký tự.")

    customer.password_hash = hash_password(new_password)
    customer.must_change_password = False
    db.commit()
