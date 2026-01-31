"""Tests for tenant management"""
import pytest
from app.models.tenant import Tenant
from app.models.user import User, UserRole


def test_create_tenant(client, platform_admin_token):
    """Test creating a new tenant"""
    response = client.post(
        "/tenants/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={
            "name": "Test Company",
            "slug": "test-company",
            "initial_admin_email": "admin@test.com",
            "initial_admin_name": "Test Admin",
            "initial_admin_password": "admin123",
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Company"
    assert data["slug"] == "test-company"


def test_create_duplicate_tenant(client, platform_admin_token, db_session):
    """Test creating tenant with duplicate slug"""
    # Create first tenant
    tenant = Tenant(name="Existing", slug="existing")
    db_session.add(tenant)
    db_session.commit()
    
    # Try to create duplicate
    response = client.post(
        "/tenants/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={
            "name": "Another Company",
            "slug": "existing",
            "initial_admin_email": "admin@another.com",
            "initial_admin_name": "Admin",
            "initial_admin_password": "pass123",
        }
    )
    
    assert response.status_code == 400


def test_list_tenants(client, platform_admin_token, db_session):
    """Test listing all tenants"""
    # Create some tenants
    tenant1 = Tenant(name="Company 1", slug="company-1")
    tenant2 = Tenant(name="Company 2", slug="company-2")
    db_session.add_all([tenant1, tenant2])
    db_session.commit()
    
    response = client.get(
        "/tenants/",
        headers={"Authorization": f"Bearer {platform_admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_get_tenant(client, platform_admin_token, db_session):
    """Test getting tenant details"""
    tenant = Tenant(name="Test Company", slug="test-company")
    db_session.add(tenant)
    db_session.commit()
    
    response = client.get(
        f"/tenants/{tenant.id}",
        headers={"Authorization": f"Bearer {platform_admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Company"


def test_update_tenant(client, platform_admin_token, db_session):
    """Test updating tenant details"""
    tenant = Tenant(name="Old Name", slug="old-name")
    db_session.add(tenant)
    db_session.commit()
    
    response = client.put(
        f"/tenants/{tenant.id}",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={"name": "New Name"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"


def test_deactivate_tenant(client, platform_admin_token, db_session):
    """Test deactivating a tenant"""
    tenant = Tenant(name="Active Company", slug="active", is_active=True)
    db_session.add(tenant)
    db_session.commit()
    
    response = client.delete(
        f"/tenants/{tenant.id}",
        headers={"Authorization": f"Bearer {platform_admin_token}"}
    )
    
    assert response.status_code == 200
    
    # Verify deactivation
    db_session.refresh(tenant)
    assert tenant.is_active == False
