"""Tests for POC invitation endpoints"""

import pytest
from datetime import datetime, timedelta, timezone
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.models.poc import POC, POCStatus, POCParticipant
from app.models.poc_invitation import POCInvitation, POCInvitationStatus


def test_create_poc_invitation(client, db_session, admin_token):
    """Test creating a POC invitation"""
    # Create test tenant, user, and POC
    tenant = Tenant(name="Test Tenant", subdomain="test")
    db_session.add(tenant)
    db_session.flush()

    user = (
        db_session.query(User)
        .filter(User.role == UserRole.ADMINISTRATOR)
        .first()
    )
    user.tenant_id = tenant.id

    poc = POC(
        title="Test POC",
        description="Test Description",
        customer_company_name="Test Customer",
        tenant_id=tenant.id,
        created_by=user.id,
        status=POCStatus.ACTIVE,
    )
    db_session.add(poc)
    db_session.commit()

    response = client.post(
        f"/pocs/{poc.id}/invitations/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "customer@example.com",
            "full_name": "Customer User",
            "is_customer": True,
            "personal_message": "Welcome to our POC!",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "customer@example.com"
    assert data["status"] == "pending"
    assert data["is_customer"] is True


def test_create_duplicate_invitation(client, db_session, admin_token):
    """Test that duplicate pending invitations are rejected"""
    tenant = Tenant(name="Test Tenant", subdomain="test")
    db_session.add(tenant)
    db_session.flush()

    user = (
        db_session.query(User)
        .filter(User.role == UserRole.ADMINISTRATOR)
        .first()
    )
    user.tenant_id = tenant.id

    poc = POC(
        title="Test POC",
        description="Test Description",
        customer_company_name="Test Customer",
        tenant_id=tenant.id,
        created_by=user.id,
        status=POCStatus.ACTIVE,
    )
    db_session.add(poc)
    db_session.commit()

    # Create first invitation
    invitation = POCInvitation(
        poc_id=poc.id,
        email="duplicate@example.com",
        full_name="Duplicate User",
        token="testtoken123",
        status=POCInvitationStatus.PENDING,
        invited_by=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db_session.add(invitation)
    db_session.commit()

    # Try to create duplicate
    response = client.post(
        f"/pocs/{poc.id}/invitations/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "duplicate@example.com",
            "full_name": "Duplicate User",
            "is_customer": True,
        },
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_list_poc_invitations(client, db_session, admin_token):
    """Test listing POC invitations"""
    tenant = Tenant(name="Test Tenant", subdomain="test")
    db_session.add(tenant)
    db_session.flush()

    user = (
        db_session.query(User)
        .filter(User.role == UserRole.ADMINISTRATOR)
        .first()
    )
    user.tenant_id = tenant.id

    poc = POC(
        title="Test POC",
        description="Test Description",
        customer_company_name="Test Customer",
        tenant_id=tenant.id,
        created_by=user.id,
        status=POCStatus.ACTIVE,
    )
    db_session.add(poc)
    db_session.flush()

    # Create test invitations
    invitation1 = POCInvitation(
        poc_id=poc.id,
        email="user1@example.com",
        full_name="User One",
        token="token1",
        status=POCInvitationStatus.PENDING,
        invited_by=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    invitation2 = POCInvitation(
        poc_id=poc.id,
        email="user2@example.com",
        full_name="User Two",
        token="token2",
        status=POCInvitationStatus.ACCEPTED,
        invited_by=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        accepted_at=datetime.now(timezone.utc),
    )
    db_session.add_all([invitation1, invitation2])
    db_session.commit()

    response = client.get(
        f"/pocs/{poc.id}/invitations/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_resend_expired_invitation(client, db_session, admin_token):
    """Test resending an expired invitation"""
    tenant = Tenant(name="Test Tenant", subdomain="test")
    db_session.add(tenant)
    db_session.flush()

    user = (
        db_session.query(User)
        .filter(User.role == UserRole.ADMINISTRATOR)
        .first()
    )
    user.tenant_id = tenant.id

    poc = POC(
        title="Test POC",
        description="Test Description",
        customer_company_name="Test Customer",
        tenant_id=tenant.id,
        created_by=user.id,
        status=POCStatus.ACTIVE,
    )
    db_session.add(poc)
    db_session.flush()

    # Create expired invitation
    invitation = POCInvitation(
        poc_id=poc.id,
        email="expired@example.com",
        full_name="Expired User",
        token="expiredtoken",
        status=POCInvitationStatus.EXPIRED,
        invited_by=user.id,
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    db_session.add(invitation)
    db_session.commit()

    response = client.post(
        f"/pocs/{poc.id}/invitations/{invitation.id}/resend",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert data["resend_count"] == 1


def test_validate_poc_invitation(client, db_session):
    """Test validating a POC invitation token"""
    tenant = Tenant(name="Test Tenant", subdomain="test")
    db_session.add(tenant)
    db_session.flush()

    user = User(
        email="inviter@example.com",
        full_name="Inviter User",
        hashed_password="test",
        role=UserRole.ADMINISTRATOR,
        tenant_id=tenant.id,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    poc = POC(
        title="Test POC",
        description="Test Description",
        customer_company_name="Test Customer",
        tenant_id=tenant.id,
        created_by=user.id,
        status=POCStatus.ACTIVE,
    )
    db_session.add(poc)
    db_session.flush()

    invitation = POCInvitation(
        poc_id=poc.id,
        email="validate@example.com",
        full_name="Validate User",
        token="validatetoken",
        status=POCInvitationStatus.PENDING,
        invited_by=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db_session.add(invitation)
    db_session.commit()

    response = client.get(
        f"/pocs/{poc.id}/invitations/public/validate/validatetoken"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "validate@example.com"
    assert data["poc_title"] == "Test POC"


def test_validate_expired_invitation(client, db_session):
    """Test validating an expired invitation"""
    tenant = Tenant(name="Test Tenant", subdomain="test")
    db_session.add(tenant)
    db_session.flush()

    user = User(
        email="inviter@example.com",
        full_name="Inviter User",
        hashed_password="test",
        role=UserRole.ADMINISTRATOR,
        tenant_id=tenant.id,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    poc = POC(
        title="Test POC",
        description="Test Description",
        customer_company_name="Test Customer",
        tenant_id=tenant.id,
        created_by=user.id,
        status=POCStatus.ACTIVE,
    )
    db_session.add(poc)
    db_session.flush()

    invitation = POCInvitation(
        poc_id=poc.id,
        email="expired@example.com",
        full_name="Expired User",
        token="expiredtoken",
        status=POCInvitationStatus.PENDING,
        invited_by=user.id,
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    db_session.add(invitation)
    db_session.commit()

    response = client.get(
        f"/pocs/{poc.id}/invitations/public/validate/expiredtoken"
    )

    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


def test_accept_poc_invitation_new_user(client, db_session):
    """Test accepting a POC invitation as a new user"""
    tenant = Tenant(name="Test Tenant", subdomain="test")
    db_session.add(tenant)
    db_session.flush()

    user = User(
        email="inviter@example.com",
        full_name="Inviter User",
        hashed_password="test",
        role=UserRole.ADMINISTRATOR,
        tenant_id=tenant.id,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    poc = POC(
        title="Test POC",
        description="Test Description",
        customer_company_name="Test Customer",
        tenant_id=tenant.id,
        created_by=user.id,
        status=POCStatus.ACTIVE,
    )
    db_session.add(poc)
    db_session.flush()

    invitation = POCInvitation(
        poc_id=poc.id,
        email="newuser@example.com",
        full_name="New User",
        token="accepttoken",
        status=POCInvitationStatus.PENDING,
        invited_by=user.id,
        is_customer=True,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db_session.add(invitation)
    db_session.commit()

    response = client.post(
        f"/pocs/{poc.id}/invitations/public/accept",
        json={"token": "accepttoken", "password": "securepassword123"},
    )

    assert response.status_code == 201
    assert "accepted successfully" in response.json()["message"]

    # Verify user was created
    new_user = (
        db_session.query(User)
        .filter(User.email == "newuser@example.com")
        .first()
    )
    assert new_user is not None
    assert new_user.role == UserRole.CUSTOMER

    # Verify participant was added
    participant = (
        db_session.query(POCParticipant)
        .filter(
            POCParticipant.poc_id == poc.id,
            POCParticipant.user_id == new_user.id,
        )
        .first()
    )
    assert participant is not None
    assert participant.is_customer is True

    # Verify invitation was marked as accepted
    db_session.refresh(invitation)
    assert invitation.status == POCInvitationStatus.ACCEPTED
    assert invitation.accepted_at is not None


def test_revoke_poc_invitation(client, db_session, admin_token):
    """Test revoking a POC invitation"""
    tenant = Tenant(name="Test Tenant", subdomain="test")
    db_session.add(tenant)
    db_session.flush()

    user = (
        db_session.query(User)
        .filter(User.role == UserRole.ADMINISTRATOR)
        .first()
    )
    user.tenant_id = tenant.id

    poc = POC(
        title="Test POC",
        description="Test Description",
        customer_company_name="Test Customer",
        tenant_id=tenant.id,
        created_by=user.id,
        status=POCStatus.ACTIVE,
    )
    db_session.add(poc)
    db_session.flush()

    invitation = POCInvitation(
        poc_id=poc.id,
        email="revoke@example.com",
        full_name="Revoke User",
        token="revoketoken",
        status=POCInvitationStatus.PENDING,
        invited_by=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db_session.add(invitation)
    db_session.commit()

    response = client.delete(
        f"/pocs/{poc.id}/invitations/{invitation.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert "revoked successfully" in response.json()["message"]

    # Verify invitation status
    db_session.refresh(invitation)
    assert invitation.status == POCInvitationStatus.REVOKED
