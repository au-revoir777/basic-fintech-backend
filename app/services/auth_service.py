from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.user import User
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.utils.security import create_token, decode_token, verify_password

settings = get_settings()


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)

    def login(self, email: str, password: str) -> TokenResponse:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        now = datetime.now(timezone.utc)

        if user.locked_until:
            locked_until = self._to_utc(user.locked_until)
            if locked_until and locked_until > now:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account locked. Try again later."
                )

        if not verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.login_max_attempts:
                user.locked_until = now + timedelta(minutes=settings.login_lockout_minutes)
                user.failed_login_attempts = 0
            self.user_repo.save(user)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account inactive")

        user.failed_login_attempts = 0
        user.locked_until = None
        self.user_repo.save(user)

        access_token, _, _ = create_token(
            subject=str(user.id),
            token_type="access",
            role=user.role,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )
        refresh_token, _, _ = create_token(
            subject=str(user.id),
            token_type="refresh",
            role=user.role,
            expires_delta=timedelta(days=settings.refresh_token_expire_days),
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        jti = payload.get("jti", "")
        if self.token_repo.is_revoked(jti):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

        user = self.user_repo.get_by_id(int(payload["sub"]))
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

        self.token_repo.revoke(jti=jti, token_type="refresh", expires_at=datetime.fromtimestamp(payload["exp"], timezone.utc))

        access_token, _, _ = create_token(
            subject=str(user.id),
            token_type="access",
            role=user.role,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )
        new_refresh, _, _ = create_token(
            subject=str(user.id),
            token_type="refresh",
            role=user.role,
            expires_delta=timedelta(days=settings.refresh_token_expire_days),
        )
        return TokenResponse(access_token=access_token, refresh_token=new_refresh)

    def logout(self, token: str) -> None:
        payload = decode_token(token)
        exp = datetime.fromtimestamp(payload["exp"], timezone.utc)
        self.token_repo.revoke(jti=payload.get("jti", ""), token_type=payload.get("type", "unknown"), expires_at=exp)

    @staticmethod
    def _to_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)