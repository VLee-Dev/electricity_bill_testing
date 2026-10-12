from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MeterReadingCreateIn(BaseModel):
    household_id: str
    period: str = Field(pattern=r"^\d{4}-\d{2}$", description="Kỳ tính tiền (YYYY-MM)")
    new_reading: int = Field(ge=0)


class MeterReadingUpdateIn(BaseModel):
    new_reading: int = Field(ge=0)


class MeterReadingOut(BaseModel):
    id: str
    household_id: str
    period: str
    old_reading: int
    new_reading: int
    consumption: int
    recorded_at: datetime
    has_invoice: bool = False

    model_config = ConfigDict(from_attributes=True)

