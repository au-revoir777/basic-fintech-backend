import os
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

# For serverless environments (e.g. Vercel), avoid writing sqlite file into read-only project root.
# Use /tmp for local file-based sqlite storage under serverless containers.
database_url = settings.database_url
if database_url.startswith("sqlite") and not database_url.startswith("sqlite:////") and ":memory:" not in database_url:
    # Not an absolute path and not in-memory: use /tmp
    parsed = urlparse(database_url)
    file_name = os.path.basename(parsed.path) or "finance.db"
    tmp_path = f"/tmp/{file_name}"
    os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
    database_url = f"sqlite:///{tmp_path}"

connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

engine = create_engine(database_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
