from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin
from app.features.households.schemas import (
    HouseholdCreateIn,
    HouseholdListOut,
    HouseholdOut,
    HouseholdUpdateIn,
)
from app.features.households.service import (
    delete_household,
    get_household,
    list_households,
    register_household,
    update_household,
)

router = APIRouter(prefix="/admin/households", tags=["Admin - Households"])


@router.post("", response_model=HouseholdOut, status_code=status.HTTP_201_CREATED)
def create_household(
    data: HouseholdCreateIn,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """
    FUNC-01: Đăng ký hộ sử dụng điện
    Admin tạo household mới + tự động tạo tài khoản Customer
    """
    return register_household(db, data)


@router.get("", response_model=list[HouseholdListOut])
def get_households(
    search: str | None = Query(None, description="Tìm kiếm theo mã KH, tên, SĐT"),
    status: str | None = Query(None, description="Lọc theo trạng thái: active/inactive"),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """
    FUNC-06: Theo dõi danh sách hộ sử dụng điện
    """
    return list_households(db, search, status)


@router.get("/{household_id}", response_model=HouseholdOut)
def get_household_detail(
    household_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """
    Lấy thông tin chi tiết 1 household
    """
    return get_household(db, household_id)


@router.put("/{household_id}", response_model=HouseholdOut)
def edit_household(
    household_id: str,
    data: HouseholdUpdateIn,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """
    Sửa thông tin hộ dùng điện (tên, địa chỉ, SĐT, email, trạng thái).
    KHÔNG cho sửa customer_code và meter_number (để tránh đứt liên kết FK).
    """
    return update_household(db, household_id, data)


@router.delete("/{household_id}", status_code=status.HTTP_200_OK)
def soft_delete_household(
    household_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """
    Soft delete: set status = 'inactive'.
    KHÔNG xóa row để giữ toàn vẹn FK với meter_readings, invoices, payments, email_logs.
    Nếu hộ có hóa đơn chưa thanh toán → trả 409.
    """
    return delete_household(db, household_id)
