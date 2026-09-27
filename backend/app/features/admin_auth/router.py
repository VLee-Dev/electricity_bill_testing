from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.features.admin_auth.schemas import AdminLoginIn, AdminOut, TokenOut
from app.features.admin_auth.service import authenticate_admin
from app.security import create_access_token

router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])


@router.post("/login", response_model=TokenOut)
def admin_login(data: AdminLoginIn, db: Session = Depends(get_db)):
    """
    Admin đăng nhập bằng username/password
    """
    admin = authenticate_admin(db, data.username, data.password)
    token = create_access_token({"sub": admin.id, "type": "admin"})
    return TokenOut(access_token=token)


# Import dependency ở đầu để tránh lỗi NameError
from app.dependencies import get_current_admin


@router.get("/me", response_model=AdminOut)
def admin_me(admin = Depends(get_current_admin)):
    """
    Lấy thông tin Admin hiện tại
    """
    return admin
