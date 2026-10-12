from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.features.meter_readings_new.router import (
    add_meter_reading,
    get_meter_readings,
    update_reading,
    soft_delete_reading,
)


def test_add_meter_reading():
    db = MagicMock()
    admin = SimpleNamespace(id="admin-1")
    data = SimpleNamespace(new_reading=150)
    expected = object()

    with patch(
        "app.features.meter_readings_new.router.create_meter_reading",
        return_value=expected,
    ) as service:
        result = add_meter_reading(data, db=db, admin=admin)

    assert result is expected
    service.assert_called_once_with(db, data, "admin-1")


def test_get_meter_readings_with_invoice():
    db = MagicMock()
    reading = SimpleNamespace(invoice=object())

    with patch(
        "app.features.meter_readings_new.router.list_meter_readings",
        return_value=[reading],
    ) as service:
        result = get_meter_readings(
            household_id="hh-1",
            period="2026-10",
            db=db,
        )

    assert result == [reading]
    assert reading.has_invoice is True
    service.assert_called_once_with(db, "hh-1", "2026-10")


def test_get_meter_readings_without_invoice():
    db = MagicMock()
    reading = SimpleNamespace(invoice=None)

    with patch(
        "app.features.meter_readings_new.router.list_meter_readings",
        return_value=[reading],
    ):
        result = get_meter_readings(
            household_id=None,
            period=None,
            db=db,
        )

    assert result == [reading]
    assert reading.has_invoice is False


def test_get_meter_readings_empty():
    db = MagicMock()

    with patch(
        "app.features.meter_readings_new.router.list_meter_readings",
        return_value=[],
    ):
        result = get_meter_readings(
            household_id=None,
            period=None,
            db=db,
        )

    assert result == []


def test_update_reading_without_invoice():
    db = MagicMock()
    data = SimpleNamespace(new_reading=250)
    reading = SimpleNamespace(invoice=None)

    with patch(
        "app.features.meter_readings_new.router.update_meter_reading",
        return_value=reading,
    ) as service:
        result = update_reading(
            reading_id="reading-1",
            data=data,
            db=db,
        )

    assert result is reading
    assert reading.has_invoice is False
    service.assert_called_once_with(db, "reading-1", 250)


def test_update_reading_with_invoice():
    db = MagicMock()
    data = SimpleNamespace(new_reading=300)
    reading = SimpleNamespace(invoice=object())

    with patch(
        "app.features.meter_readings_new.router.update_meter_reading",
        return_value=reading,
    ):
        result = update_reading(
            reading_id="reading-2",
            data=data,
            db=db,
        )

    assert result is reading
    assert reading.has_invoice is True


def test_soft_delete_reading():
    db = MagicMock()
    expected = {"message": "Deleted"}

    with patch(
        "app.features.meter_readings_new.router.delete_meter_reading",
        return_value=expected,
    ) as service:
        result = soft_delete_reading(
            reading_id="reading-1",
            db=db,
        )

    assert result == expected
    service.assert_called_once_with(db, "reading-1")
