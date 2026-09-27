from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.features.customer_auth.schemas import CustomerChangePasswordIn, CustomerLoginIn, CustomerOut, HouseholdOut, TokenOut
from app.features.customer_auth.service import authenticate_customer, change_customer_password
from app.security import create_access_token

router = APIRouter(prefix="/customer/auth", tags=["Customer Auth"])


@router.post("/login", response_model=TokenOut)
def customer_login(data: CustomerLoginIn, db: Session = Depends(get_db)):
    """
    Customer đăng nhập bằng customer_code + password
    """
    customer = authenticate_customer(db, data.customer_code, data.password)
    token = create_access_token({"sub": customer.id, "type": "customer"})
    return TokenOut(access_token=token)


# Import dependency ở đầu để tránh lỗi NameError
from app.dependencies import get_current_customer


@router.get("/me", response_model=CustomerOut)
def customer_me(customer = Depends(get_current_customer)):
    """
    Lấy thông tin Customer hiện tại
    """
    return customer


@router.get("/me/household", response_model=HouseholdOut)
def customer_household(customer = Depends(get_current_customer)):
    """
    Lấy thông tin Household của Customer hiện tại
    """
    return customer.household


@router.post("/change-password", status_code=204)
def customer_change_password(
    data: CustomerChangePasswordIn,
    customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Customer đổi mật khẩu
    """
    change_customer_password(db, customer, data.current_password, data.new_password)
