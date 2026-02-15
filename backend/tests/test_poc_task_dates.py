"""Tests for POC task start_date and due_date"""

import pytest
from datetime import date
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.models.poc import POC, POCStatus
from app.models.user_tenant_role import UserTenantRole
from app.auth import get_password_hash


@pytest.fixture
def sales_engineer_with_poc(db_session):
    """Create a sales engineer with a tenant and a POC"""
    tenant = Tenant(name="Test Company", slug="test-company-tasks")
    db_session.add(tenant)
    db_session.flush()

    user = User(
        email="se_tasks@test.com",
        full_name="Sales Engineer",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.SALES_ENGINEER,
        tenant_id=tenant.id,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    # Multi-tenant auth requires a UserTenantRole record
    utr = UserTenantRole(
        user_id=user.id,
        tenant_id=tenant.id,
        role=UserRole.SALES_ENGINEER,
        is_default=True,
        is_active=True,
    )
    db_session.add(utr)
    db_session.flush()

    poc = POC(
        title="Task Date Test POC",
        customer_company_name="Customer Corp",
        tenant_id=tenant.id,
        created_by=user.id,
        status=POCStatus.ACTIVE,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 3, 31),
    )
    db_session.add(poc)
    db_session.commit()
    return user, tenant, poc


def _login(client, tenant_id):
    """Login via select-tenant endpoint to get an access token"""
    resp = client.post(
        "/auth/select-tenant",
        json={
            "email": "se_tasks@test.com",
            "password": "testpass123",
            "tenant_id": tenant_id,
        },
    )
    return resp.json()["access_token"]


def test_add_task_defaults_due_date_to_poc_end(
    client, sales_engineer_with_poc, db_session
):
    """When no due_date is provided, it should default to the POC end_date"""
    user, tenant, poc = sales_engineer_with_poc
    token = _login(client, tenant.id)

    response = client.post(
        f"/tasks/pocs/{poc.id}/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Task without dates"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["due_date"] == "2026-03-31"
    assert data["start_date"] is None


def test_add_task_with_explicit_dates(
    client, sales_engineer_with_poc, db_session
):
    """Explicit start and due dates within POC range should work"""
    user, tenant, poc = sales_engineer_with_poc
    token = _login(client, tenant.id)

    response = client.post(
        f"/tasks/pocs/{poc.id}/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Dated task",
            "start_date": "2026-01-15",
            "due_date": "2026-02-28",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["start_date"] == "2026-01-15"
    assert data["due_date"] == "2026-02-28"


def test_add_task_due_date_after_poc_end_fails(
    client, sales_engineer_with_poc, db_session
):
    """due_date after POC end_date should be rejected"""
    user, tenant, poc = sales_engineer_with_poc
    token = _login(client, tenant.id)

    response = client.post(
        f"/tasks/pocs/{poc.id}/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Late task",
            "due_date": "2026-05-01",
        },
    )

    assert response.status_code == 400
    assert "after the POC end date" in response.json()["detail"]


def test_add_task_due_date_before_poc_start_fails(
    client, sales_engineer_with_poc, db_session
):
    """due_date before POC start_date should be rejected"""
    user, tenant, poc = sales_engineer_with_poc
    token = _login(client, tenant.id)

    response = client.post(
        f"/tasks/pocs/{poc.id}/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Early task",
            "due_date": "2025-12-01",
        },
    )

    assert response.status_code == 400
    assert "before the POC start date" in response.json()["detail"]


def test_add_task_start_after_due_fails(
    client, sales_engineer_with_poc, db_session
):
    """start_date after due_date should be rejected"""
    user, tenant, poc = sales_engineer_with_poc
    token = _login(client, tenant.id)

    response = client.post(
        f"/tasks/pocs/{poc.id}/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Backwards task",
            "start_date": "2026-03-01",
            "due_date": "2026-02-01",
        },
    )

    assert response.status_code == 400
    assert "after the task due date" in response.json()["detail"]


def test_update_task_dates(client, sales_engineer_with_poc, db_session):
    """Updating task dates within POC range should work"""
    user, tenant, poc = sales_engineer_with_poc
    token = _login(client, tenant.id)

    # Create task first
    create_resp = client.post(
        f"/tasks/pocs/{poc.id}/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Update me"},
    )
    task_id = create_resp.json()["id"]

    # Update dates
    update_resp = client.put(
        f"/tasks/pocs/{poc.id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "start_date": "2026-02-01",
            "due_date": "2026-03-15",
        },
    )

    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["start_date"] == "2026-02-01"
    assert data["due_date"] == "2026-03-15"


def test_update_task_due_date_outside_poc_fails(
    client, sales_engineer_with_poc, db_session
):
    """Updating due_date beyond POC end should fail"""
    user, tenant, poc = sales_engineer_with_poc
    token = _login(client, tenant.id)

    # Create task
    create_resp = client.post(
        f"/tasks/pocs/{poc.id}/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Bounded task"},
    )
    task_id = create_resp.json()["id"]

    # Try to update due_date beyond POC end
    update_resp = client.put(
        f"/tasks/pocs/{poc.id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"due_date": "2026-06-01"},
    )

    assert update_resp.status_code == 400
    assert "after the POC end date" in update_resp.json()["detail"]
