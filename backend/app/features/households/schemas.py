from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class HouseholdCreateIn(BaseModel):
    customer_code: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1, max_length=500)
    phone: str = Field(min_length=10, max_length=20)
    email: EmailStr
    meter_number: str = Field(min_length=1, max_length=50)
    initial_password: str = Field(min_length=6)  # Mật khẩu khởi tạo cho Customer


class HouseholdUpdateIn(BaseModel):
    """Body cho PUT /admin/households/{id}.
    Tất cả field đều optional — chỉ field nào gửi lên mới được cập nhật.
    KHÔNG cho sửa customer_code / meter_number (giữ ổn định FK + UNIQUE).
    """
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = Field(default=None, min_length=1, max_length=500)
    phone: str | None = Field(default=None, min_length=10, max_length=20)
    email: EmailStr | None = None
    status: str | None = Field(default=None, pattern="^(active|inactive)$")


class HouseholdOut(BaseModel):
    id: str
    customer_code: str
    full_name: str
    address: str
    phone: str
    email: str
    meter_number: str
    registered_at: datetime
    status: str

    class Config:
        from_attributes = True


class HouseholdListOut(BaseModel):
    id: str
    customer_code: str
    full_name: str
    address: str
    phone: str
    email: str
    meter_number: str
    status: str

    class Config:
        from_attributes = True
