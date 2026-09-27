from pydantic import BaseModel, Field


class AdminLoginIn(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6)


class AdminOut(BaseModel):
    id: str
    username: str
    full_name: str

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
