from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin
from app.features.meter_readings_new.schemas import MeterReadingCreateIn, MeterReadingOut, MeterReadingUpdateIn
from app.features.meter_readings_new.service import (
    create_meter_reading,
    delete_meter_reading,
    list_meter_readings,
    update_meter_reading,
)

router = APIRouter(prefix="/admin/meter-readings", tags=["Admin - Meter Readings"])


@router.post("", response_model=MeterReadingOut, status_code=status.HTTP_201_CREATED)
def add_meter_reading(
    data: MeterReadingCreateIn,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """
    FUNC-02: Cập nhật chỉ số điện hàng kỳ
    """
    return create_meter_reading(db, data, admin.id)


@router.get("", response_model=list[MeterReadingOut])
def get_meter_readings(
    household_id: str | None = Query(None),
    period: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """
    Lấy danh sách meter readings
    """
    readings = list_meter_readings(db, household_id, period)
    # Add has_invoice field
    for reading in readings:
        reading.has_invoice = reading.invoice is not None
    return readings


@router.put("/{reading_id}", response_model=MeterReadingOut)
def update_reading(
    reading_id: str,
    data: MeterReadingUpdateIn,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """
    Cập nhật chỉ số điện (chỉ cho phép nếu chưa tính hóa đơn)
    """
    reading = update_meter_reading(db, reading_id, data.new_reading)
    reading.has_invoice = reading.invoice is not None
    return reading


@router.delete("/{reading_id}", status_code=status.HTTP_200_OK)
def soft_delete_reading(
    reading_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin)
):
    """
    Soft delete meter reading: xóa row (KHÔNG có FK nào trỏ về nó trừ Invoice 1-1).
    - Nếu CHƯA có hóa đơn → xóa row bình thường.
    - Nếu ĐÃ có hóa đơn → trả 409 (phải xóa/xử lý hóa đơn trước).
    Meter reading là dữ liệu đầu vào, không có invoice_tier_details/payments/email_logs
    tham chiếu trực tiếp tới nó. Nên xóa row an toàn hơn soft delete.
    """
    return delete_meter_reading(db, reading_id)
