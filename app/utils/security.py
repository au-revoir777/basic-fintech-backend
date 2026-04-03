from datetime import datetime, timedelta, timezone
from uuid import uuid4
import hashlib

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    # Temporary: use SHA256 for testing
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Temporary: use SHA256 for testing
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


def create_token(subject: str, token_type: str, expires_delta: timedelta, role: str) -> tuple[str, str, datetime]:
    expire = datetime.now(timezone.utc) + expires_delta
    jti = str(uuid4())
    to_encode = {
        "sub": subject,
        "type": token_type,
        "role": role,
        "jti": jti,
        "exp": expire,
    }
    encoded = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded, jti, expire


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
