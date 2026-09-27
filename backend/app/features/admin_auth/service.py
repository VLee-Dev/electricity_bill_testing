from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import UnauthorizedError
from app.models.admin import Admin
from app.security import verify_password


def authenticate_admin(db: Session, username: str, password: str) -> Admin:
    """
    Xác thực Admin bằng username/password
    """
    admin = db.scalar(select(Admin).where(Admin.username == username))
    if not admin or not verify_password(password, admin.password_hash):
        error = UnauthorizedError("Tên đăng nhập hoặc mật khẩu không đúng.")
        error.error_code = "INVALID_CREDENTIALS"
        raise error
    return admin
