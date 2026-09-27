from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.price_tier import PriceTier
from app.exceptions import NotFoundError


def get_active_price_tiers(db: Session) -> list[PriceTier]:
    """
    Lấy bảng giá điện hiện hành (đang active)
    """
    today = date.today()
    query = select(PriceTier).where(
        PriceTier.effective_from <= today,
        (PriceTier.effective_to == None) | (PriceTier.effective_to >= today)
    ).order_by(PriceTier.tier_no)

    return db.scalars(query).all()


def get_all_price_tiers(db: Session) -> list[PriceTier]:
    """
    Lấy bảng giá điện mới nhất (cho admin).
    Trả về phiên bản mới nhất của mỗi bậc (bản ghi có effective_to IS NULL).
    Trả về đầy đủ 6 bậc (mỗi tier_no 1 record) để admin thấy đúng giá hiện hành
    và ngày cập nhật mới nhất.
    """
    query = (
        select(PriceTier)
        .where(PriceTier.effective_to.is_(None))
        .order_by(PriceTier.tier_no)
    )
    return db.scalars(query).all()


def update_price_tier(db: Session, tier_id: int, unit_price: int, effective_from: date) -> PriceTier:
    """
    Cập nhật giá điện cho 1 bậc (UPDATE trực tiếp, không tạo bản ghi mới).
    - Cập nhật unit_price và effective_from của chính bản ghi đó.
    - effective_to giữ nguyên (None nếu đang active).
    """
    # Lấy bậc giá hiện tại
    tier = db.get(PriceTier, tier_id)
    if not tier:
        raise NotFoundError("Không tìm thấy bậc giá.")

    # Cập nhật trực tiếp - không tạo bản ghi mới
    tier.unit_price = unit_price
    tier.effective_from = effective_from
    # effective_to giữ nguyên giá trị cũ (None nếu active)

    db.commit()
    db.refresh(tier)

    return tier
