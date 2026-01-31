"""Tests for POC management"""
import pytest
from datetime import date
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.models.poc import POC, POCStatus
from app.auth import get_password_hash


@pytest.fixture
def sales_engineer_with_tenant(db_session):
    """Create a sales engineer with a tenant"""
    tenant = Tenant(name="Test Company", slug="test-company")
    db_session.add(tenant)
    db_session.flush()
    
    user = User(
        email="sales@test.com",
        full_name="Sales Engineer",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.SALES_ENGINEER,
        tenant_id=tenant.id,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user, tenant


def test_create_poc(client, sales_engineer_with_tenant, db_session):
    """Test creating a new POC"""
    user, tenant = sales_engineer_with_tenant
    
    # Login
    login_response = client.post("/auth/login", json={
        "email": "sales@test.com",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]
    
    # Create POC
    response = client.post(
        "/pocs/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test POC",
            "description": "A test POC",
            "customer_company_name": "Customer Corp",
            "start_date": "2024-01-01",
            "end_date": "2024-03-01",
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test POC"
    assert data["status"] == "draft"


def test_list_pocs(client, sales_engineer_with_tenant, db_session):
    """Test listing POCs"""
    user, tenant = sales_engineer_with_tenant
    
    # Create some POCs
    poc1 = POC(
        title="POC 1",
        customer_company_name="Customer 1",
        tenant_id=tenant.id,
        created_by=user.id,
        status=POCStatus.DRAFT,
    )
    poc2 = POC(
        title="POC 2",
        customer_company_name="Customer 2",
        tenant_id=tenant.id,
        created_by=user.id,
        status=POCStatus.ACTIVE,
    )
    db_session.add_all([poc1, poc2])
    db_session.commit()
    
    # Login
    login_response = client.post("/auth/login", json={
        "email": "sales@test.com",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]
    
    # List POCs
    response = client.get(
        "/pocs/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_get_poc_detail(client, sales_engineer_with_tenant, db_session):
    """Test getting POC details"""
    user, tenant = sales_engineer_with_tenant
    
    poc = POC(
        title="Detailed POC",
        customer_company_name="Customer",
        tenant_id=tenant.id,
        created_by=user.id,
        status=POCStatus.ACTIVE,
    )
    db_session.add(poc)
    db_session.commit()
    
    # Login
    login_response = client.post("/auth/login", json={
        "email": "sales@test.com",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]
    
    # Get POC
    response = client.get(
        f"/pocs/{poc.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Detailed POC"


def test_update_poc(client, sales_engineer_with_tenant, db_session):
    """Test updating a POC"""
    user, tenant = sales_engineer_with_tenant
    
    poc = POC(
        title="Original Title",
        customer_company_name="Customer",
        tenant_id=tenant.id,
        created_by=user.id,
        status=POCStatus.DRAFT,
    )
    db_session.add(poc)
    db_session.commit()
    
    # Login
    login_response = client.post("/auth/login", json={
        "email": "sales@test.com",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]
    
    # Update POC
    response = client.put(
        f"/pocs/{poc.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Updated Title",
            "status": "active"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "active"


def test_archive_poc(client, sales_engineer_with_tenant, db_session):
    """Test archiving a POC"""
    user, tenant = sales_engineer_with_tenant
    
    poc = POC(
        title="POC to Archive",
        customer_company_name="Customer",
        tenant_id=tenant.id,
        created_by=user.id,
        status=POCStatus.COMPLETED,
    )
    db_session.add(poc)
    db_session.commit()
    
    # Login
    login_response = client.post("/auth/login", json={
        "email": "sales@test.com",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]
    
    # Archive POC
    response = client.delete(
        f"/pocs/{poc.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    
    # Verify status
    db_session.refresh(poc)
    assert poc.status == POCStatus.ARCHIVED
