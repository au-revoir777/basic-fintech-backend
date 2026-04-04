# tests/test_rbac.py

import pytest
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

def create_user(db, role: str):
    unique_email = f"{role}_{uuid.uuid4()}@test.com"

    user = User(
        email=unique_email,
        full_name=f"{role} user",
        password_hash=hash_password("test123"),
        role=role,
        is_active=True,
        failed_login_attempts=0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, unique_email


def login_and_get_token(role: str):
    db = SessionLocal()
    user, email = create_user(db, role)

    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "test123"
    })
    db.close()

    assert res.status_code == 200
    return res.json()["access_token"]


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


# -------------------------
# Common payload
# -------------------------

def valid_record_payload():
    return {
        "amount": 1000,
        "category": "Salary",
        "record_type": "income",        # must match your enum
        "record_date": "2026-06-01",    # ISO format
        "notes": "test record"
    }


# -------------------------
# RBAC Tests
# -------------------------

def test_viewer_permissions():
    token = login_and_get_token("viewer")
    headers = auth_headers(token)

    # Viewer CAN read
    res = client.get("/api/v1/records", headers=headers)
    assert res.status_code == 200

    # Viewer CANNOT create
    res = client.post("/api/v1/records", json=valid_record_payload(), headers=headers)
    assert res.status_code == 403

    # Viewer CANNOT delete
    res = client.delete("/api/v1/records/1", headers=headers)
    assert res.status_code == 403


def test_analyst_permissions():
    token = login_and_get_token("analyst")
    headers = auth_headers(token)

    # Analyst CAN create
    res = client.post("/api/v1/records", json=valid_record_payload(), headers=headers)
    assert res.status_code in (200, 201)

    # Analyst CAN read
    res = client.get("/api/v1/records", headers=headers)
    assert res.status_code == 200

    # Analyst CANNOT delete
    res = client.delete("/api/v1/records/1", headers=headers)
    assert res.status_code == 403


def test_admin_permissions():
    token = login_and_get_token("admin")
    headers = auth_headers(token)

    # Admin CAN create
    res = client.post("/api/v1/records", json=valid_record_payload(), headers=headers)
    assert res.status_code in (200, 201)

    record_id = res.json().get("id", 1)

    # Admin CAN delete
    res = client.delete(f"/api/v1/records/{record_id}", headers=headers)
    assert res.status_code in (200, 204)


# -------------------------
# Parametrized test
# -------------------------

@pytest.mark.parametrize("role,can_delete", [
    ("viewer", False),
    ("analyst", False),
    ("admin", True),
])
def test_delete_rbac(role, can_delete):
    token = login_and_get_token(role)
    headers = auth_headers(token)

    # Step 1: Create a record (as admin always)
    admin_token = login_and_get_token("admin")
    admin_headers = auth_headers(admin_token)

    create_res = client.post(
        "/api/v1/records",
        json=valid_record_payload(),
        headers=admin_headers
    )
    assert create_res.status_code in (200, 201)

    record_id = create_res.json()["id"]

    # Step 2: Try deleting with current role
    res = client.delete(f"/api/v1/records/{record_id}", headers=headers)

    # Step 3: Assert RBAC behavior
    if can_delete:
        assert res.status_code in (200, 204)
    else:
        assert res.status_code == 403