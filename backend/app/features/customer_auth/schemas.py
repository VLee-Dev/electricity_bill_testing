from pydantic import BaseModel, EmailStr, Field


class CustomerLoginIn(BaseModel):
    customer_code: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)


class CustomerChangePasswordIn(BaseModel):
    current_password: str = Field(min_length=6)
    new_password: str = Field(min_length=6)


class CustomerOut(BaseModel):
    id: str
    household_id: str
    must_change_password: bool

    class Config:
        from_attributes = True


class HouseholdOut(BaseModel):
    id: str
    customer_code: str
    full_name: str
    address: str
    phone: str
    email: EmailStr
    meter_number: str
    status: str

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
