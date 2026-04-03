from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.enums import Role
from app.schemas.dashboard import DashboardSummary, TrendPoint
from app.schemas.record import RecordResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(require_roles(Role.VIEWER, Role.ANALYST, Role.ADMIN))])


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db)):
    return DashboardService(db).summary()


@router.get("/trends", response_model=List[TrendPoint])
def trends(by: str = Query("monthly", pattern="^(monthly|weekly)$"), db: Session = Depends(get_db)):
    return DashboardService(db).trends(by)


@router.get("/recent", response_model=List[RecordResponse])
def recent(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    return DashboardService(db).recent(limit)
