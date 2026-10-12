
from datetime import date
from unittest.mock import MagicMock, patch

from app.features.price_tiers.router import (
    get_active_tiers,
    get_all_tiers_admin,
    update_tier_price,
)
from app.features.price_tiers.schemas import PriceTierUpdateIn


# ============================================================
# PRICE TIERS ROUTER TESTS
# ============================================================

def test_get_active_tiers_router():
    """PTR001: Public endpoint returns active price tiers."""
    db = MagicMock()
    expected = [MagicMock(), MagicMock()]

    with patch(
        "app.features.price_tiers.router.get_active_price_tiers",
        return_value=expected,
    ) as mock_service:
        result = get_active_tiers(db=db)

    assert result is expected
    mock_service.assert_called_once_with(db)


def test_get_all_tiers_admin_router():
    """PTR002: Admin endpoint returns all price tiers."""
    db = MagicMock()
    expected = [MagicMock(), MagicMock(), MagicMock()]

    with patch(
        "app.features.price_tiers.router.get_all_price_tiers",
        return_value=expected,
    ) as mock_service:
        result = get_all_tiers_admin(db=db)

    assert result is expected
    mock_service.assert_called_once_with(db)


def test_update_tier_price_router():
    """PTR003: Admin endpoint forwards price update to service."""
    db = MagicMock()

    data = PriceTierUpdateIn(
        unit_price=2500,
        effective_from=date(2026, 10, 12),
    )

    expected = MagicMock()

    with patch(
        "app.features.price_tiers.router.update_price_tier",
        return_value=expected,
    ) as mock_service:
        result = update_tier_price(
            tier_id=1,
            data=data,
            db=db,
        )

    assert result is expected

    mock_service.assert_called_once_with(
        db,
        1,
        data.unit_price,
        data.effective_from,
    )
