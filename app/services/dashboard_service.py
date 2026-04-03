from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.record_repository import RecordRepository


class DashboardService:
    def __init__(self, db: Session):
        self.repo = RecordRepository(db)

    def summary(self):
        income, expenses, category_totals = self.repo.summary()
        return {
            "total_income": Decimal(income),
            "total_expenses": Decimal(expenses),
            "net_balance": Decimal(income) - Decimal(expenses),
            "category_totals": category_totals,
        }

    def trends(self, by: str):
        return [{"period": r.period, "income": r.income or 0, "expense": r.expense or 0} for r in self.repo.trends(by)]

    def recent(self, limit: int):
        return self.repo.recent(limit)
