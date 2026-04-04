from datetime import date

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import analyst_or_admin, get_current_user, require_roles
from app.core.rate_limit import enforce_rate_limit
from app.db.session import get_db
from app.models.enums import Role, RecordType
from app.models.user import User
from app.schemas.record import PaginatedRecords, RecordCreate, RecordResponse, RecordUpdate
from app.services.record_service import RecordService

router = APIRouter(prefix="/records", tags=["records"])


@router.post("", response_model=RecordResponse)
def create_record(
    payload: RecordCreate,
    request: Request,
    user: User = Depends(analyst_or_admin),
    db: Session = Depends(get_db),
):
    enforce_rate_limit(request)
    record = RecordService(db).create(payload, user.id)
    return RecordResponse.model_validate(record)


@router.get("", response_model=PaginatedRecords, dependencies=[Depends(require_roles(Role.VIEWER, Role.ANALYST, Role.ADMIN))])
def list_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: str | None = None,
    record_type: RecordType | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    sort_by: str = Query("date", pattern="^(date|amount)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    total, items = RecordService(db).list(skip, limit, category, record_type.value if record_type else None, start_date, end_date, sort_by, sort_order)
    return {
    "total": total,
    "items": [RecordResponse.model_validate(item) for item in items]
}

@router.patch("/{record_id}", response_model=RecordResponse)
def update_record(record_id: int, payload: RecordUpdate, user: User = Depends(analyst_or_admin), db: Session = Depends(get_db)):
    _ = user
    record = RecordService(db).update(record_id, payload)
    return RecordResponse.model_validate(record)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles(Role.ADMIN))])
def delete_record(record_id: int, db: Session = Depends(get_db)):
    RecordService(db).soft_delete(record_id)
