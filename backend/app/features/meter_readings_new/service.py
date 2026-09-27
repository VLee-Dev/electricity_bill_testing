from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.household import Household
from app.models.meter_reading import MeterReading


def create_meter_reading(db: Session, data, admin_id: str) -> MeterReading:
    """
    FUNC-02: Cập nhật chỉ số điện hàng kỳ
    Admin nhập chỉ số mới cho household
    """
    # Kiểm tra household tồn tại
    household = db.get(Household, data.household_id)
    if not household:
        raise NotFoundError("Không tìm thấy hộ sử dụng điện.")

    # Kiểm tra trùng period
    existing = db.scalar(
        select(MeterReading).where(
            MeterReading.household_id == data.household_id,
            MeterReading.period == data.period
        )
    )
    if existing:
        error = ConflictError("Hộ này đã có chỉ số cho kỳ này.")
        error.error_code = "DUPLICATE_PERIOD"
        raise error

    # Lấy chỉ số cũ từ kỳ trước
    previous = db.scalar(
        select(MeterReading)
        .where(MeterReading.household_id == data.household_id)
        .order_by(MeterReading.period.desc())
    )
    old_reading = previous.new_reading if previous else 0

    # Validate chỉ số mới >= chỉ số cũ
    if data.new_reading < old_reading:
        raise ValidationError("Chỉ số mới không được nhỏ hơn chỉ số cũ.")

    consumption = data.new_reading - old_reading

    # Tạo meter reading
    reading = MeterReading(
        household_id=data.household_id,
        period=data.period,
        old_reading=old_reading,
        new_reading=data.new_reading,
        consumption=consumption,
        recorded_by=admin_id
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


def list_meter_readings(
    db: Session,
    household_id: str | None = None,
    period: str | None = None
) -> list[MeterReading]:
    """
    Lấy danh sách meter readings
    """
    query = select(MeterReading)

    if household_id:
        query = query.where(MeterReading.household_id == household_id)

    if period:
        query = query.where(MeterReading.period == period)

    query = query.order_by(MeterReading.period.desc())
    return db.scalars(query).all()


def update_meter_reading(db: Session, reading_id: str, new_reading: int) -> MeterReading:
    """
    Cập nhật chỉ số điện (chỉ cho phép nếu chưa có invoice)
    """
    reading = db.get(MeterReading, reading_id)
    if not reading:
        raise NotFoundError("Không tìm thấy chỉ số điện.")

    # Kiểm tra xem đã tính hóa đơn chưa
    if reading.invoice:
        raise ConflictError("Không thể sửa chỉ số đã được tính hóa đơn.")

    # Validate chỉ số mới >= chỉ số cũ
    if new_reading < reading.old_reading:
        raise ValidationError("Chỉ số mới không được nhỏ hơn chỉ số cũ.")

    reading.new_reading = new_reading
    reading.consumption = new_reading - reading.old_reading

    db.commit()
    db.refresh(reading)
    return reading


def delete_meter_reading(db: Session, reading_id: str) -> dict:
    """
    Xóa 1 meter reading (row thật, không soft).
    Điều kiện: CHƯA có invoice tham chiếu tới reading này.
    Meter reading không có bảng nào tham chiếu trực tiếp (chỉ invoices.meter_reading_id,
    nhưng invoices 1-1 nên đã được kiểm tra ở guard phía dưới).
    """
    reading = db.get(MeterReading, reading_id)
    if not reading:
        raise NotFoundError("Không tìm thấy chỉ số điện.")

    # Guard: nếu đã tính hóa đơn thì không cho xóa
    if reading.invoice:
        err = ConflictError(
            "Chỉ số này đã được tính hóa đơn. Vui lòng xóa/xử lý hóa đơn trước."
        )
        err.error_code = "READING_HAS_INVOICE"
        raise err

    period = reading.period
    db.delete(reading)
    db.commit()
    return {
        "id": reading_id,
        "message": f"Đã xóa chỉ số kỳ {period}."
    }
