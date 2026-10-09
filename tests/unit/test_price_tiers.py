from datetime import date
from unittest.mock import MagicMock

import pytest

from app.exceptions import NotFoundError
from app.features.price_tiers.service import (
    get_active_price_tiers,
    get_all_price_tiers,
    update_price_tier,
)


def test_get_active_price_tiers():
    db = MagicMock()
    tiers = [MagicMock(tier_no=1), MagicMock(tier_no=2)]
    db.scalars.return_value.all.return_value = tiers

    result = get_active_price_tiers(db)

    assert result == tiers
    db.scalars.assert_called_once()


def test_get_active_price_tiers_empty():
    db = MagicMock()
    db.scalars.return_value.all.return_value = []

    assert get_active_price_tiers(db) == []


def test_get_all_price_tiers():
    db = MagicMock()
    tiers = [MagicMock(tier_no=1), MagicMock(tier_no=2)]
    db.scalars.return_value.all.return_value = tiers

    result = get_all_price_tiers(db)

    assert result == tiers
    db.scalars.assert_called_once()


def test_get_all_price_tiers_empty():
    db = MagicMock()
    db.scalars.return_value.all.return_value = []

    assert get_all_price_tiers(db) == []


def test_update_price_tier_success():
    db = MagicMock()
    tier = MagicMock()
    tier.effective_to = None
    db.get.return_value = tier

    new_date = date(2026, 10, 9)
    result = update_price_tier(db, 1, 2500, new_date)

    assert result is tier
    assert tier.unit_price == 2500
    assert tier.effective_from == new_date
    assert tier.effective_to is None

    db.get.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(tier)


def test_update_price_tier_not_found():
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(NotFoundError):
        update_price_tier(db, 999, 2500, date(2026, 10, 9))

    db.commit.assert_not_called()
    db.refresh.assert_not_called()
