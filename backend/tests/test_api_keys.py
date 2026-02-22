"""Tests for API Key management"""

import pytest
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.models.user_tenant_role import UserTenantRole
from app.models.api_key import APIKey
from app.auth import get_password_hash, create_access_token


def _make_user_with_token(db_session, role=UserRole.SALES_ENGINEER):
    """Helper: create a user with tenant role and return (user, auth_header)."""
    tenant = Tenant(name="Test Tenant", slug="test-tenant")
    db_session.add(tenant)
    db_session.flush()

    user = User(
        email=f"{role.value}@test.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpass123"),
        role=role,
        is_active=True,
        tenant_id=tenant.id,
    )
    db_session.add(user)
    db_session.flush()

    utr = UserTenantRole(
        user_id=user.id,
        tenant_id=tenant.id,
        role=role,
        is_default=True,
        is_active=True,
    )
    db_session.add(utr)
    db_session.commit()

    token = create_access_token(data={"sub": user.email}, tenant_id=tenant.id)
    header = {"Authorization": f"Bearer {token}"}
    return user, header


# ─── LIST ────────────────────────────────────────────────────────────────────


def test_list_api_keys_empty(client, db_session):
    """No keys initially."""
    _, header = _make_user_with_token(db_session)
    resp = client.get("/api-keys/", headers=header)
    assert resp.status_code == 200
    assert resp.json() == []


# ─── CREATE ──────────────────────────────────────────────────────────────────


def test_create_api_key(client, db_session):
    """Create a key and get the raw key back."""
    _, header = _make_user_with_token(db_session)
    resp = client.post(
        "/api-keys/",
        json={"name": "CI Key", "expiration": "1_year"},
        headers=header,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "CI Key"
    assert body["api_key"].startswith("pocm_")
    assert body["key_prefix"] == body["api_key"][:8]
    assert "message" in body  # vault warning


def test_create_api_key_limit(client, db_session):
    """Cannot exceed 3 active keys."""
    _, header = _make_user_with_token(db_session)
    for i in range(3):
        resp = client.post(
            "/api-keys/",
            json={"name": f"Key {i}", "expiration": "6_months"},
            headers=header,
        )
        assert resp.status_code == 201

    # 4th should fail
    resp = client.post(
        "/api-keys/",
        json={"name": "Key 4", "expiration": "6_months"},
        headers=header,
    )
    assert resp.status_code == 400
    assert "Maximum" in resp.json()["detail"]


def test_create_key_customer_allowed(client, db_session):
    """Customers should be able to create keys."""
    _, header = _make_user_with_token(db_session, role=UserRole.CUSTOMER)
    resp = client.post(
        "/api-keys/",
        json={"name": "Customer Key", "expiration": "6_months"},
        headers=header,
    )
    assert resp.status_code == 201


# ─── DELETE ──────────────────────────────────────────────────────────────────


def test_delete_api_key(client, db_session):
    """Delete an existing key."""
    _, header = _make_user_with_token(db_session)
    create_resp = client.post(
        "/api-keys/",
        json={"name": "Temp", "expiration": "6_months"},
        headers=header,
    )
    key_id = create_resp.json()["id"]

    del_resp = client.delete(f"/api-keys/{key_id}", headers=header)
    assert del_resp.status_code == 204

    # Should no longer appear in list
    list_resp = client.get("/api-keys/", headers=header)
    assert all(k["id"] != key_id for k in list_resp.json())


def test_delete_nonexistent_key(client, db_session):
    """404 when key doesn't exist or belongs to another user."""
    _, header = _make_user_with_token(db_session)
    resp = client.delete("/api-keys/99999", headers=header)
    assert resp.status_code == 404


# ─── EXTEND ──────────────────────────────────────────────────────────────────


def test_extend_api_key(client, db_session):
    """Extend shifts the expiry date forward."""
    _, header = _make_user_with_token(db_session)
    create_resp = client.post(
        "/api-keys/",
        json={"name": "Extend Me", "expiration": "6_months"},
        headers=header,
    )
    key_id = create_resp.json()["id"]
    original_expires = create_resp.json()["expires_at"]

    ext_resp = client.post(
        f"/api-keys/{key_id}/extend",
        json={"expiration": "1_year"},
        headers=header,
    )
    assert ext_resp.status_code == 200
    assert ext_resp.json()["expires_at"] > original_expires


# ─── AUTH WITH API KEY ───────────────────────────────────────────────────────


def test_authenticate_with_api_key(client, db_session):
    """Use an API key instead of JWT to call a protected endpoint."""
    _, header = _make_user_with_token(db_session)
    create_resp = client.post(
        "/api-keys/",
        json={"name": "Auth Key", "expiration": "1_year"},
        headers=header,
    )
    raw_key = create_resp.json()["api_key"]

    # Use the raw API key as Bearer token to list keys
    api_header = {"Authorization": f"Bearer {raw_key}"}
    resp = client.get("/api-keys/", headers=api_header)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
