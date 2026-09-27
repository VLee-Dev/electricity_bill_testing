from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin, get_current_customer
from app.features.price_tiers.schemas import PriceTierOut, PriceTierUpdateIn
from app.features.price_tiers.service import get_active_price_tiers, get_all_price_tiers, update_price_tier

router = APIRouter(prefix="/price-tiers", tags=["Price Tiers"])


@router.get("/active", response_model=list[PriceTierOut])
def get_active_tiers(db: Session = Depends(get_db)):
    """
    Lấy bảng giá điện hiện hành (public - customer có thể xem)
    """
    return get_active_price_tiers(db)


@router.get("/admin/all", response_model=list[PriceTierOut])
def get_all_tiers_admin(
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """
    Admin: Xem toàn bộ lịch sử bảng giá
    """
    return get_all_price_tiers(db)


@router.put("/admin/{tier_id}", response_model=PriceTierOut)
def update_tier_price(
    tier_id: int,
    data: PriceTierUpdateIn,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """
    Admin: Cập nhật giá điện cho 1 bậc
    - Đóng bậc giá cũ
    - Tạo bậc giá mới với giá mới
    """
    return update_price_tier(db, tier_id, data.unit_price, data.effective_from)
