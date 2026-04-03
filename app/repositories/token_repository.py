from datetime import datetime, timezone
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.token_blocklist import TokenBlocklist


class TokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def revoke(self, jti: str, token_type: str, expires_at: datetime) -> None:
        self.db.add(TokenBlocklist(jti=jti, token_type=token_type, expires_at=expires_at))
        self.db.commit()

    def is_revoked(self, jti: str) -> bool:
        row = self.db.scalar(select(TokenBlocklist).where(TokenBlocklist.jti == jti))
        return row is not None

    def cleanup_expired(self) -> None:
        self.db.execute(delete(TokenBlocklist).where(TokenBlocklist.expires_at < datetime.now(timezone.utc)))
        self.db.commit()
