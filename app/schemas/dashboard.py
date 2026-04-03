from decimal import Decimal
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    category_totals: dict[str, Decimal]


class TrendPoint(BaseModel):
    period: str
    income: Decimal
    expense: Decimal
