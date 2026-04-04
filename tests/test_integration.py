import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.utils.security import hash_password

client = TestClient(app)


# -------------------------
# Helpers 
# -------------------------

def create_user(role: str):
    db = SessionLocal()

    email = f"{role}_{uuid.uuid4()}@test.com"

    user = User(
        email=email,
        full_name="Test User",
        password_hash=hash_password("test123"),
        role=role,
        is_active=True,
        failed_login_attempts=0,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    return email


def login(role: str):
    email = create_user(role)

    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "test123"
    })

    assert res.status_code == 200
    return res.json()


def headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def record_payload():
    return {
        "amount": 1000.0,
        "category": "Salary",
        "record_type": "income",
        "record_date": "2024-01-01",
        "notes": "Integration test"
    }


# -------------------------
# Full Flow
# -------------------------

def test_full_record_lifecycle():
    tokens = login("analyst")
    h = headers(tokens["access_token"])

    # CREATE
    res = client.post("/api/v1/records", json=record_payload(), headers=h)
    assert res.status_code in (200, 201)

    record_id = res.json()["id"]

    # LIST
    res = client.get("/api/v1/records", headers=h)
    assert res.status_code == 200
    assert res.json()["total"] >= 1

    # UPDATE
    res = client.patch(f"/api/v1/records/{record_id}", json={
        "amount": 2000.0
    }, headers=h)

    assert res.status_code == 200
    assert res.json()["amount"] == 2000.0

    # DELETE (analyst should fail)
    res = client.delete(f"/api/v1/records/{record_id}", headers=h)
    assert res.status_code == 403


# -------------------------
# Admin Flow
# -------------------------

def test_admin_can_delete():
    tokens = login("admin")
    h = headers(tokens["access_token"])

    res = client.post("/api/v1/records", json=record_payload(), headers=h)
    record_id = res.json()["id"]

    res = client.delete(f"/api/v1/records/{record_id}", headers=h)
    assert res.status_code == 204


# -------------------------
# Refresh Flow
# -------------------------

def test_refresh_token_flow():
    tokens = login("viewer")

    # Only test if refresh_token exists
    assert "refresh_token" in tokens

    res = client.post("/api/v1/auth/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })

    assert res.status_code == 200
    assert "access_token" in res.json()


# -------------------------
# Permission Check
# -------------------------

def test_access_without_permission():
    tokens = login("viewer")
    h = headers(tokens["access_token"])

    res = client.post("/api/v1/records", json=record_payload(), headers=h)
    assert res.status_code == 403