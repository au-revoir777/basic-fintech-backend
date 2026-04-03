from enum import StrEnum


class Role(StrEnum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"


class RecordType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"
