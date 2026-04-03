from datetime import date
from typing import List
from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.financial_record import FinancialRecord
from app.models.enums import RecordType


class RecordRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, record: FinancialRecord) -> FinancialRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_id(self, record_id: int) -> FinancialRecord | None:
        return self.db.scalar(
            select(FinancialRecord).where(FinancialRecord.id == record_id, FinancialRecord.is_deleted.is_(False))
        )

    def list(
        self,
        skip: int,
        limit: int,
        category: str | None,
        record_type: str | None,
        start_date: date | None,
        end_date: date | None,
        sort_by: str,
        sort_order: str,
    ) -> tuple[int, List[FinancialRecord]]:
        conditions = [FinancialRecord.is_deleted.is_(False)]
        if category:
            conditions.append(FinancialRecord.category == category)
        if record_type:
            conditions.append(FinancialRecord.record_type == record_type)
        if start_date:
            conditions.append(FinancialRecord.record_date >= start_date)
        if end_date:
            conditions.append(FinancialRecord.record_date <= end_date)

        stmt = select(FinancialRecord).where(and_(*conditions))
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

        sort_col = FinancialRecord.record_date if sort_by == "date" else FinancialRecord.amount
        stmt = stmt.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc()).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return total, items

    def save(self, record: FinancialRecord) -> FinancialRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def summary(self) -> tuple:
        income = self.db.scalar(
            select(func.coalesce(func.sum(FinancialRecord.amount), 0)).where(
                FinancialRecord.is_deleted.is_(False), FinancialRecord.record_type == RecordType.INCOME.value
            )
        )
        expense = self.db.scalar(
            select(func.coalesce(func.sum(FinancialRecord.amount), 0)).where(
                FinancialRecord.is_deleted.is_(False), FinancialRecord.record_type == RecordType.EXPENSE.value
            )
        )
        category_rows = self.db.execute(
            select(FinancialRecord.category, func.coalesce(func.sum(FinancialRecord.amount), 0))
            .where(FinancialRecord.is_deleted.is_(False))
            .group_by(FinancialRecord.category)
        ).all()
        return income, expense, {category: total for category, total in category_rows}

    def trends(self, by: str):
    # PostgreSQL-compatible format
    fmt = "YYYY-IW" if by == "weekly" else "YYYY-MM"

    rows = self.db.execute(
        select(
            func.to_char(FinancialRecord.record_date, fmt).label("period"),
            func.sum(
                case(
                    (FinancialRecord.record_type == RecordType.INCOME.value, FinancialRecord.amount),
                    else_=0,
                )
            ).label("income"),
            func.sum(
                case(
                    (FinancialRecord.record_type == RecordType.EXPENSE.value, FinancialRecord.amount),
                    else_=0,
                )
            ).label("expense"),
        )
        .where(FinancialRecord.is_deleted.is_(False))
        .group_by("period")
        .order_by("period")
    ).all()

    return rows

    def recent(self, limit: int = 10) -> List[FinancialRecord]:
        return list(
            self.db.scalars(
                select(FinancialRecord)
                .where(FinancialRecord.is_deleted.is_(False))
                .order_by(FinancialRecord.created_at.desc())
                .limit(limit)
            ).all()
        )
