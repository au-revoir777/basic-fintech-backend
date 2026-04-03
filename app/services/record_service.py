from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.financial_record import FinancialRecord
from app.repositories.record_repository import RecordRepository
from app.schemas.record import RecordCreate, RecordUpdate


class RecordService:
    def __init__(self, db: Session):
        self.repo = RecordRepository(db)

    def create(self, payload: RecordCreate, user_id: int) -> FinancialRecord:
        record = FinancialRecord(
            user_id=user_id,
            amount=payload.amount,
            record_type=payload.record_type.value,
            category=payload.category,
            record_date=payload.record_date,
            notes=payload.notes,
        )
        return self.repo.create(record)

    def list(self, skip: int, limit: int, category: str | None, record_type: str | None, start_date: date | None, end_date: date | None, sort_by: str, sort_order: str):
        return self.repo.list(skip, limit, category, record_type, start_date, end_date, sort_by, sort_order)

    def update(self, record_id: int, payload: RecordUpdate) -> FinancialRecord:
        record = self.repo.get_by_id(record_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            if key == "record_type" and value is not None:
                setattr(record, key, value.value)
            elif value is not None:
                setattr(record, key, value)
        return self.repo.save(record)

    def soft_delete(self, record_id: int) -> None:
        record = self.repo.get_by_id(record_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
        record.is_deleted = True
        self.repo.save(record)
