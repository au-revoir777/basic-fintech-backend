from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.enums import Role
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, dependencies=[Depends(require_roles(Role.ADMIN))])
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    return UserService(db).create_user(payload)


@router.get("", response_model=List[UserResponse], dependencies=[Depends(require_roles(Role.ADMIN))])
def list_users(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    return UserService(db).list_users(skip, limit)


@router.patch("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_roles(Role.ADMIN))])
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    return UserService(db).update_user(user_id, payload)
