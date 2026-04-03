from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def create_user(self, payload: UserCreate) -> User:
        if self.repo.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        user = User(
            email=payload.email,
            full_name=payload.full_name,
            password_hash=hash_password(payload.password),
            role=payload.role.value,
            is_active=True,
        )
        return self.repo.create(user)

    def list_users(self, skip: int, limit: int) -> List[User]:
        return self.repo.list_users(skip=skip, limit=limit)

    def update_user(self, user_id: int, payload: UserUpdate) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        data = payload.model_dump(exclude_unset=True)
        if "role" in data and data["role"] is not None:
            user.role = data["role"].value
        if "full_name" in data and data["full_name"] is not None:
            user.full_name = data["full_name"]
        if "is_active" in data and data["is_active"] is not None:
            user.is_active = data["is_active"]

        return self.repo.save(user)
