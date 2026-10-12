from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.exceptions import ConflictError, NotFoundError, ValidationError
from app.features.meter_readings_new.service import (
    create_meter_reading,
    list_meter_readings,
    update_meter_reading,
    delete_meter_reading,
)
from app.models.household import Household
from app.models.meter_reading import MeterReading


# ============================================================
# TEST HELPERS
# ============================================================

def make_data(new_reading=150):
    return SimpleNamespace(
        household_id="household-1",
        period="2026-10",
        new_reading=new_reading,
    )


# ============================================================
# EXISTING TEST CASES (MR001 - MR013)
# ============================================================

def test_create_meter_reading_success():
    db = MagicMock()
    db.get.return_value = MagicMock(spec=Household)
    db.scalar.side_effect = [None, SimpleNamespace(new_reading=100)]

    result = create_meter_reading(db, make_data(150), "admin-1")

    assert isinstance(result, MeterReading)
    assert result.old_reading == 100
    assert result.new_reading == 150
    assert result.consumption == 50
    assert result.recorded_by == "admin-1"
    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_create_meter_reading_household_not_found():
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(NotFoundError):
        create_meter_reading(db, make_data(), "admin-1")

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_create_meter_reading_duplicate_period():
    db = MagicMock()
    db.get.return_value = MagicMock(spec=Household)
    db.scalar.return_value = MagicMock(spec=MeterReading)

    with pytest.raises(ConflictError) as exc:
        create_meter_reading(db, make_data(), "admin-1")

    assert exc.value.error_code == "DUPLICATE_PERIOD"
    db.commit.assert_not_called()


def test_create_meter_reading_invalid_value():
    db = MagicMock()
    db.get.return_value = MagicMock(spec=Household)
    db.scalar.side_effect = [None, SimpleNamespace(new_reading=200)]

    with pytest.raises(ValidationError):
        create_meter_reading(db, make_data(150), "admin-1")

    db.commit.assert_not_called()


def test_list_meter_readings_without_filters():
    db = MagicMock()
    readings = [MagicMock(), MagicMock()]
    db.scalars.return_value.all.return_value = readings

    result = list_meter_readings(db)

    assert result == readings
    db.scalars.assert_called_once()


def test_list_meter_readings_with_filters():
    db = MagicMock()
    db.scalars.return_value.all.return_value = []

    result = list_meter_readings(
        db,
        household_id="household-1",
        period="2026-10",
    )

    assert result == []
    db.scalars.assert_called_once()


def test_update_meter_reading_success():
    db = MagicMock()
    reading = SimpleNamespace(
        old_reading=100,
        new_reading=120,
        consumption=20,
        invoice=None,
    )
    db.get.return_value = reading

    result = update_meter_reading(db, "reading-1", 180)

    assert result is reading
    assert reading.new_reading == 180
    assert reading.consumption == 80
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(reading)


def test_update_meter_reading_not_found():
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(NotFoundError):
        update_meter_reading(db, "missing", 180)

    db.commit.assert_not_called()


def test_update_meter_reading_has_invoice():
    db = MagicMock()
    db.get.return_value = SimpleNamespace(
        old_reading=100,
        invoice=object(),
    )

    with pytest.raises(ConflictError):
        update_meter_reading(db, "reading-1", 180)

    db.commit.assert_not_called()


def test_update_meter_reading_invalid_value():
    db = MagicMock()
    db.get.return_value = SimpleNamespace(
        old_reading=200,
        invoice=None,
    )

    with pytest.raises(ValidationError):
        update_meter_reading(db, "reading-1", 150)

    db.commit.assert_not_called()


def test_delete_meter_reading_success():
    db = MagicMock()
    reading = SimpleNamespace(
        period="2026-10",
        invoice=None,
    )
    db.get.return_value = reading

    result = delete_meter_reading(db, "reading-1")

    assert result["id"] == "reading-1"
    assert "2026-10" in result["message"]
    db.delete.assert_called_once_with(reading)
    db.commit.assert_called_once()


def test_delete_meter_reading_not_found():
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(NotFoundError):
        delete_meter_reading(db, "missing")

    db.delete.assert_not_called()
    db.commit.assert_not_called()


def test_delete_meter_reading_has_invoice():
    db = MagicMock()
    db.get.return_value = SimpleNamespace(
        period="2026-10",
        invoice=object(),
    )

    with pytest.raises(ConflictError) as exc:
        delete_meter_reading(db, "reading-1")

    assert exc.value.error_code == "READING_HAS_INVOICE"
    db.delete.assert_not_called()
    db.commit.assert_not_called()

def test_create_meter_reading_first_period():
    """MR014: First period starts with old reading equal to zero."""
    db = MagicMock()
    db.get.return_value = MagicMock(spec=Household)
    db.scalar.side_effect = [None, None]

    result = create_meter_reading(
        db,
        make_data(new_reading=150),
        "admin-1",
    )

    assert isinstance(result, MeterReading)
    assert result.old_reading == 0
    assert result.new_reading == 150
    assert result.consumption == 150
    assert result.recorded_by == "admin-1"

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_create_meter_reading_equal_previous():
    """MR015: Equal readings result in zero consumption."""
    db = MagicMock()
    db.get.return_value = MagicMock(spec=Household)
    db.scalar.side_effect = [
        None,
        SimpleNamespace(new_reading=150),
    ]

    result = create_meter_reading(
        db,
        make_data(new_reading=150),
        "admin-1",
    )

    assert isinstance(result, MeterReading)
    assert result.old_reading == 150
    assert result.new_reading == 150
    assert result.consumption == 0

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()


def test_update_meter_reading_equal_old():
    """MR016: Updating reading to old value is allowed."""
    db = MagicMock()

    reading = SimpleNamespace(
        old_reading=100,
        new_reading=180,
        consumption=80,
        invoice=None,
    )

    db.get.return_value = reading

    result = update_meter_reading(
        db,
        "reading-1",
        100,
    )

    assert result is reading
    assert reading.new_reading == 100
    assert reading.consumption == 0

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(reading)


def test_list_meter_readings_period_only():
    """MR017: List meter readings filtered by period only."""
    db = MagicMock()

    readings = [
        SimpleNamespace(
            household_id="household-1",
            period="2026-10",
        ),
        SimpleNamespace(
            household_id="household-2",
            period="2026-10",
        ),
    ]

    db.scalars.return_value.all.return_value = readings

    result = list_meter_readings(
        db,
        period="2026-10",
    )

    assert result == readings
    assert all(reading.period == "2026-10" for reading in result)
    db.scalars.assert_called_once()