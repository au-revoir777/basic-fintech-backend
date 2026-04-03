from datetime import date, datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field, field_validator

from app.models.enums import RecordType


class RecordBase(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    record_type: RecordType
    category: str = Field(min_length=2, max_length=120)
    record_date: date
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("notes")
    @classmethod
    def sanitize_notes(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.replace("<", "&lt;").replace(">", "&gt;")


class RecordCreate(RecordBase):
    pass


class RecordUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    record_type: RecordType | None = None
    category: str | None = Field(default=None, min_length=2, max_length=120)
    record_date: date | None = None
    notes: str | None = Field(default=None, max_length=1000)


class RecordResponse(RecordBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedRecords(BaseModel):
    total: int
    items: List[RecordResponse]
