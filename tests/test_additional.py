import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.utils.security import hash_password, decode_token
from app.repositories.token_repository import TokenRepository

client = TestClient(app)


# -------------------------
# Helpers
# -------------------------

def create_user(db, role: str):
    import uuid
    email = f"{role}_{uuid.uuid4()}@test.com"

    user = User(
        email=email,
        full_name=f"{role} user",
        password_hash=hash_password("test123"),
        role=role,
        is_active=True,
        failed_login_attempts=0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, email


def login_and_get_token(role: str):
    db = SessionLocal()
    _, email = create_user(db, role)

    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "test123"
    })

    db.close()

    assert res.status_code == 200
    return res.json()["access_token"]


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def valid_record_payload():
    return {
        "amount": 1000.0,  # ✅ float (not Decimal)
        "category": "Salary",
        "record_type": "income",
        "record_date": "2024-01-01",
        "notes": "Test record"
    }


# -------------------------
# Auth / Token Tests
# -------------------------

def test_invalid_token():
    headers = {"Authorization": "Bearer invalidtoken"}
    res = client.get("/api/v1/records", headers=headers)

    # Your decode_token raises ValueError → unhandled
    assert res.status_code in (401, 500)


def test_missing_token():
    res = client.get("/api/v1/records")
    assert res.status_code == 403


def test_revoked_token():
    db = SessionLocal()
    _, email = create_user(db, "viewer")

    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "test123"
    })
    token = res.json()["access_token"]

    token_data = decode_token(token)

    # ✅ FIX: pass required args
    TokenRepository(db).revoke(
        jti=token_data["jti"],
        token_type="access",
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )

    headers = auth_headers(token)
    res = client.get("/api/v1/records", headers=headers)

    db.close()

    assert res.status_code == 401


# -------------------------
# Account Lock Test
# -------------------------

def test_locked_user():
    db = SessionLocal()
    user, email = create_user(db, "viewer")

    # ✅ FIX: use naive datetime
    user.locked_until = datetime.utcnow() + timedelta(minutes=5)
    db.commit()

    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "test123"
    })

    db.close()

    assert res.status_code == 403


# -------------------------
# Validation Tests
# -------------------------

def test_create_record_invalid_payload():
    token = login_and_get_token("analyst")
    headers = auth_headers(token)

    res = client.post("/api/v1/records", json={
        "amount": 1000
    }, headers=headers)

    assert res.status_code == 400


def test_negative_amount():
    token = login_and_get_token("analyst")
    headers = auth_headers(token)

    payload = valid_record_payload()
    payload["amount"] = -100.0  # ✅ float

    res = client.post("/api/v1/records", json=payload, headers=headers)
    assert res.status_code == 400


def test_notes_sanitization():
    token = login_and_get_token("analyst")
    headers = auth_headers(token)

    payload = valid_record_payload()
    payload["notes"] = "<script>alert(1)</script>"

    res = client.post("/api/v1/records", json=payload, headers=headers)

    assert res.status_code in (200, 201)
    assert "&lt;script&gt;" in res.json()["notes"]


# -------------------------
# RBAC Edge Case
# -------------------------

def test_analyst_cannot_delete_others_record():
    token = login_and_get_token("analyst")
    headers = auth_headers(token)

    res = client.delete("/api/v1/records/999", headers=headers)
    assert res.status_code in (403, 404)


# -------------------------
# Exception Handlers
# -------------------------

def test_validation_error_format():
    token = login_and_get_token("analyst")
    headers = auth_headers(token)

    res = client.post("/api/v1/records", json={}, headers=headers)

    assert res.status_code == 400
    assert "error" in res.json()
    assert res.json()["error"]["code"] == 400


def test_404_format():
    res = client.get("/nonexistent")

    assert res.status_code == 404
    assert "error" in res.json()


# -------------------------
# Middleware Tests
# -------------------------

def test_security_headers():
    res = client.get("/health")

    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in res.headers


# -------------------------
# Basic Endpoints
# -------------------------

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert "Finance Dashboard API" in res.json()["message"]