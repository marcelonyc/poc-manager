"""Tests for Platform Admin invitation functionality"""

import pytest
from datetime import datetime, timedelta, timezone
from app.models.user import User, UserRole
from app.models.invitation import Invitation, InvitationStatus
from app.models.tenant import Tenant
from app.models.user_tenant_role import UserTenantRole


def test_create_invitation_as_platform_admin(client, platform_admin_token):
    """Test that Platform Admin can create invitations"""
    response = client.post(
        "/invitations/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={"email": "newadmin@example.com", "full_name": "New Admin"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newadmin@example.com"
    assert data["full_name"] == "New Admin"
    assert data["status"] == "pending"
    assert "token" not in data  # Token should not be in response


def test_create_invitation_non_platform_admin(client, tenant_admin_token):
    """Test that non-Platform Admin cannot create invitations"""
    response = client.post(
        "/invitations/",
        headers={"Authorization": f"Bearer {tenant_admin_token}"},
        json={"email": "newadmin@example.com", "full_name": "New Admin"},
    )
    assert response.status_code == 403


def test_create_invitation_duplicate_email(
    client, platform_admin_token, db_session
):
    """Test that invitation fails for existing user email"""
    # Create a user first
    user = User(
        email="existing@example.com",
        full_name="Existing User",
        hashed_password="hashedpass",
        role=UserRole.PLATFORM_ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/invitations/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={"email": "existing@example.com", "full_name": "New Admin"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_create_invitation_duplicate_pending(
    client, platform_admin_token, db_session
):
    """Test that duplicate pending invitations are not allowed"""
    # Create first invitation
    response1 = client.post(
        "/invitations/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={"email": "invited@example.com", "full_name": "Invited User"},
    )
    assert response1.status_code == 201

    # Try to create second invitation for same email
    response2 = client.post(
        "/invitations/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
        json={"email": "invited@example.com", "full_name": "Invited User"},
    )
    assert response2.status_code == 400
    assert "Pending invitation already exists" in response2.json()["detail"]


def test_list_invitations(client, platform_admin_token, db_session):
    """Test listing invitations"""
    # Create some invitations
    for i in range(3):
        invitation = Invitation(
            email=f"test{i}@example.com",
            full_name=f"Test User {i}",
            token=f"token{i}",
            status=InvitationStatus.PENDING,
            invited_by_email="admin@example.com",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db_session.add(invitation)
    db_session.commit()

    response = client.get(
        "/invitations/",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_list_invitations_non_platform_admin(client, tenant_admin_token):
    """Test that non-Platform Admin cannot list invitations"""
    response = client.get(
        "/invitations/",
        headers={"Authorization": f"Bearer {tenant_admin_token}"},
    )
    assert response.status_code == 403


def test_validate_invitation_valid(client, db_session):
    """Test validating a valid invitation"""
    invitation = Invitation(
        email="valid@example.com",
        full_name="Valid User",
        token="validtoken123",
        status=InvitationStatus.PENDING,
        invited_by_email="admin@example.com",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db_session.add(invitation)
    db_session.commit()

    response = client.get("/invitations/validate/validtoken123")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "valid@example.com"
    assert data["full_name"] == "Valid User"


def test_validate_invitation_not_found(client):
    """Test validating non-existent invitation"""
    response = client.get("/invitations/validate/nonexistenttoken")
    assert response.status_code == 404


def test_validate_invitation_expired(client, db_session):
    """Test validating expired invitation"""
    invitation = Invitation(
        email="expired@example.com",
        full_name="Expired User",
        token="expiredtoken123",
        status=InvitationStatus.PENDING,
        invited_by_email="admin@example.com",
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),  # Expired
    )
    db_session.add(invitation)
    db_session.commit()

    response = client.get("/invitations/validate/expiredtoken123")
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


def test_accept_invitation(client, db_session):
    """Test accepting an invitation"""
    invitation = Invitation(
        email="accept@example.com",
        full_name="Accept User",
        token="accepttoken123",
        status=InvitationStatus.PENDING,
        invited_by_email="admin@example.com",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db_session.add(invitation)
    db_session.commit()

    response = client.post(
        "/invitations/accept",
        json={"token": "accepttoken123", "password": "securepassword123"},
    )
    assert response.status_code == 201
    assert "created successfully" in response.json()["message"]

    # Verify user was created
    user = (
        db_session.query(User)
        .filter(User.email == "accept@example.com")
        .first()
    )
    assert user is not None
    assert user.role == UserRole.PLATFORM_ADMIN
    assert user.tenant_id is None

    # Verify invitation was marked as accepted
    db_session.refresh(invitation)
    assert invitation.status == InvitationStatus.ACCEPTED
    assert invitation.accepted_at is not None


def test_accept_invitation_expired(client, db_session):
    """Test accepting expired invitation"""
    invitation = Invitation(
        email="expired@example.com",
        full_name="Expired User",
        token="expiredtoken456",
        status=InvitationStatus.PENDING,
        invited_by_email="admin@example.com",
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db_session.add(invitation)
    db_session.commit()

    response = client.post(
        "/invitations/accept",
        json={"token": "expiredtoken456", "password": "securepassword123"},
    )
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


def test_revoke_invitation(client, platform_admin_token, db_session):
    """Test revoking an invitation"""
    invitation = Invitation(
        email="revoke@example.com",
        full_name="Revoke User",
        token="revoketoken123",
        status=InvitationStatus.PENDING,
        invited_by_email="admin@example.com",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db_session.add(invitation)
    db_session.commit()
    invitation_id = invitation.id

    response = client.delete(
        f"/invitations/{invitation_id}",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
    )
    assert response.status_code == 200
    assert "revoked successfully" in response.json()["message"]

    # Verify invitation status
    db_session.refresh(invitation)
    assert invitation.status == InvitationStatus.REVOKED


def test_revoke_invitation_non_platform_admin(
    client, tenant_admin_token, db_session
):
    """Test that non-Platform Admin cannot revoke invitations"""
    invitation = Invitation(
        email="test@example.com",
        full_name="Test User",
        token="testtoken123",
        status=InvitationStatus.PENDING,
        invited_by_email="admin@example.com",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db_session.add(invitation)
    db_session.commit()

    response = client.delete(
        f"/invitations/{invitation.id}",
        headers={"Authorization": f"Bearer {tenant_admin_token}"},
    )
    assert response.status_code == 403


def test_revoke_invitation_already_accepted(
    client, platform_admin_token, db_session
):
    """Test that accepted invitations cannot be revoked"""
    invitation = Invitation(
        email="accepted@example.com",
        full_name="Accepted User",
        token="acceptedtoken123",
        status=InvitationStatus.ACCEPTED,
        invited_by_email="admin@example.com",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        accepted_at=datetime.now(timezone.utc),
    )
    db_session.add(invitation)
    db_session.commit()

    response = client.delete(
        f"/invitations/{invitation.id}",
        headers={"Authorization": f"Bearer {platform_admin_token}"},
    )
    assert response.status_code == 400
    assert "Cannot revoke" in response.json()["detail"]


def test_accept_team_member_invitation_with_role_and_tenant(
    client, db_session
):
    """Test accepting an invitation that has a role and tenant (team member flow)"""
    tenant = Tenant(name="Team Tenant", slug="team")
    db_session.add(tenant)
    db_session.commit()

    invitation = Invitation(
        email="teammember@example.com",
        full_name="Team Member",
        token="teamtoken123",
        status=InvitationStatus.PENDING,
        invited_by_email="admin@tenant.com",
        role="sales_engineer",
        tenant_id=tenant.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db_session.add(invitation)
    db_session.commit()

    response = client.post(
        "/invitations/accept",
        json={
            "token": "teamtoken123",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 201
    assert "created successfully" in response.json()["message"]

    # Verify user was created with the correct role and tenant
    user = (
        db_session.query(User)
        .filter(User.email == "teammember@example.com")
        .first()
    )
    assert user is not None
    assert user.role == UserRole.SALES_ENGINEER
    assert user.tenant_id == tenant.id

    # Verify user_tenant_role was created
    utr = (
        db_session.query(UserTenantRole)
        .filter(
            UserTenantRole.user_id == user.id,
            UserTenantRole.tenant_id == tenant.id,
        )
        .first()
    )
    assert utr is not None
    assert utr.role == UserRole.SALES_ENGINEER
    assert utr.is_default is True


def test_validate_team_member_invitation_shows_role_and_tenant(
    client, db_session
):
    """Test that validating a team member invitation returns role and tenant info"""
    tenant = Tenant(name="Validate Tenant", slug="validate")
    db_session.add(tenant)
    db_session.commit()

    invitation = Invitation(
        email="validate@example.com",
        full_name="Validate User",
        token="validateteamtoken",
        status=InvitationStatus.PENDING,
        invited_by_email="admin@tenant.com",
        role="administrator",
        tenant_id=tenant.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db_session.add(invitation)
    db_session.commit()

    response = client.get("/invitations/validate/validateteamtoken")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "validate@example.com"
    assert data["role"] == "administrator"
    assert data["tenant_name"] == "Validate Tenant"


def test_accept_invitation_without_role_defaults_to_platform_admin(
    client, db_session
):
    """Test that invitations without a role default to platform_admin (backward compat)"""
    invitation = Invitation(
        email="legacy@example.com",
        full_name="Legacy Admin",
        token="legacytoken123",
        status=InvitationStatus.PENDING,
        invited_by_email="admin@example.com",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db_session.add(invitation)
    db_session.commit()

    response = client.post(
        "/invitations/accept",
        json={
            "token": "legacytoken123",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 201

    user = (
        db_session.query(User)
        .filter(User.email == "legacy@example.com")
        .first()
    )
    assert user is not None
    assert user.role == UserRole.PLATFORM_ADMIN
    assert user.tenant_id is None
