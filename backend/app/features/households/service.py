from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.customer import Customer
from app.models.household import Household
from app.models.invoice import Invoice
from app.models.meter_reading import MeterReading
from app.security import hash_password
from app.email_service import send_welcome_email


def register_household(db: Session, data) -> Household:
    """
    FUNC-01: Đăng ký hộ sử dụng điện
    Admin tạo household + tự động tạo Customer account với mật khẩu khởi tạo
    """
    # Kiểm tra trùng customer_code
    if db.scalar(select(Household).where(Household.customer_code == data.customer_code)):
        error = ConflictError("Mã khách hàng đã tồn tại.")
        error.error_code = "CUSTOMER_CODE_EXISTS"
        raise error

    # Kiểm tra trùng meter_number
    if db.scalar(select(Household).where(Household.meter_number == data.meter_number)):
        error = ConflictError("Số công tơ đã tồn tại.")
        error.error_code = "METER_NUMBER_EXISTS"
        raise error

    # Kiểm tra trùng email
    if db.scalar(select(Household).where(Household.email == data.email)):
        error = ConflictError("Email đã tồn tại.")
        error.error_code = "EMAIL_EXISTS"
        raise error

    # Tạo household
    household = Household(
        customer_code=data.customer_code,
        full_name=data.full_name,
        address=data.address,
        phone=data.phone,
        email=data.email,
        meter_number=data.meter_number,
        status="active"
    )

    # Tạo customer account liên kết
    customer = Customer(
        household=household,
        password_hash=hash_password(data.initial_password),
        must_change_password=True
    )

    db.add(household)
    db.add(customer)
    db.commit()
    db.refresh(household)

    # Gửi email chào mừng với thông tin đăng nhập
    send_welcome_email(
        db=db,
        recipient_email=household.email,
        recipient_name=household.full_name,
        customer_code=household.customer_code,
        initial_password=data.initial_password
    )

    return household


def list_households(db: Session, search: str | None = None, status: str | None = None) -> list[Household]:
    """
    FUNC-06: Theo dõi danh sách hộ sử dụng điện
    """
    query = select(Household)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Household.customer_code.ilike(search_pattern)) |
            (Household.full_name.ilike(search_pattern)) |
            (Household.phone.ilike(search_pattern))
        )

    if status:
        query = query.where(Household.status == status)

    query = query.order_by(Household.registered_at.desc())
    return db.scalars(query).all()


def get_household(db: Session, household_id: str) -> Household:
    """
    Lấy thông tin chi tiết 1 household
    """
    household = db.get(Household, household_id)
    if not household:
        raise NotFoundError("Không tìm thấy hộ sử dụng điện.")
    return household


def update_household(db: Session, household_id: str, data) -> Household:
    """
    Sửa thông tin hộ dùng điện.
    Chỉ cập nhật các field được gửi lên (optional trong schema).
    KHÔNG cho sửa customer_code, meter_number, registered_at.
    Nếu email thay đổi → validate không trùng email hộ khác.
    """
    household = get_household(db, household_id)

    # Validate email không trùng hộ khác
    if data.email and data.email != household.email:
        existing = db.scalar(
            select(Household).where(
                Household.email == data.email,
                Household.id != household_id
            )
        )
        if existing:
            err = ConflictError("Email đã được sử dụng bởi hộ khác.")
            err.error_code = "EMAIL_EXISTS"
            raise err

    # Validate phone không trùng hộ khác
    if data.phone and data.phone != household.phone:
        existing = db.scalar(
            select(Household).where(
                Household.phone == data.phone,
                Household.id != household_id
            )
        )
        if existing:
            err = ConflictError("Số điện thoại đã được sử dụng bởi hộ khác.")
            err.error_code = "PHONE_EXISTS"
            raise err

    # Áp dụng update (chỉ field nào được gửi)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(household, field, value)

    db.commit()
    db.refresh(household)
    return household


def delete_household(db: Session, household_id: str) -> dict:
    """
    Soft delete household: set status = 'inactive'.
    Không xóa row để giữ FK ổn định với meter_readings, invoices, payments, email_logs.

    Quy tắc nghiệp vụ: nếu hộ còn hóa đơn CHƯA THANH TOÁN → KHÔNG cho xóa (trả 409).
    Hóa đơn đã thanh toán thì OK (dữ liệu lịch sử).
    """
    household = get_household(db, household_id)

    if household.status == "inactive":
        # idempotent — đã inactive rồi vẫn OK
        return {"id": household.id, "status": "inactive", "message": "Hộ đã ở trạng thái ngưng từ trước."}

    # Kiểm tra hóa đơn chưa thanh toán
    unpaid_invoice = db.scalar(
        select(Invoice).where(
            Invoice.household_id == household_id,
            Invoice.status == "unpaid"
        )
    )
    if unpaid_invoice:
        err = ConflictError(
            "Hộ này còn hóa đơn chưa thanh toán. Vui lòng xử lý hóa đơn trước khi ngưng hộ."
        )
        err.error_code = "HOUSEHOLD_HAS_UNPAID_INVOICE"
        raise err

    household.status = "inactive"
    db.commit()
    db.refresh(household)
    return {
        "id": household.id,
        "status": household.status,
        "message": f"Đã chuyển hộ {household.customer_code} sang trạng thái ngưng (inactive)."
    }
