import os
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

# For serverless environments (e.g. Vercel), avoid writing sqlite file into read-only project root.
# Use /tmp for local file-based sqlite storage under serverless containers.
database_url = settings.database_url
if database_url.startswith("sqlite"):
    # sqlite:///./finance.db or sqlite:///finance.db etc.
    parsed = urlparse(database_url)
    if parsed.path and not parsed.path.startswith("/"):
        # Relative path: use /tmp
        file_name = os.path.basename(parsed.path)
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
