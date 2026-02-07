"""Tenant invitation router - for inviting existing users to additional tenants"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, timezone
import secrets

from app.database import get_db
from app.models.user import User, UserRole
from app.models.tenant_invitation import (
    TenantInvitation,
    TenantInvitationStatus,
)
from app.models.user_tenant_role import UserTenantRole
from app.schemas.multi_tenant_auth import (
    TenantInvitationCreate,
    TenantInvitationResponse,
    TenantInvitationAccept,
)
from app.auth import (
    get_current_user,
    require_tenant_admin,
    get_current_tenant_id,
)
from app.services.email import send_tenant_invitation_email
from app.services.demo_seed import seed_demo_account

router = APIRouter(prefix="/tenant-invitations", tags=["Tenant Invitations"])


def generate_invitation_token() -> str:
    """Generate a secure random token for invitation"""
    return secrets.token_urlsafe(32)


@router.post(
    "/",
    response_model=TenantInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tenant_invitation(
    invitation_data: TenantInvitationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin),
):
    """
    Invite an existing user to join this tenant with a specific role.
    Tenant Admin or Platform Admin only.
    """
    current_tenant_id = get_current_tenant_id(current_user)

    if not current_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tenant context. Please select a tenant first.",
        )

    # Check if user exists
    invited_user = (
        db.query(User).filter(User.email == invitation_data.email).first()
    )
    if not invited_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found with this email. Use the regular user creation flow for new users.",
        )

    # Check if user already has access to this tenant
    existing_access = (
        db.query(UserTenantRole)
        .filter(
            UserTenantRole.user_id == invited_user.id,
            UserTenantRole.tenant_id == current_tenant_id,
        )
        .first()
    )

    if existing_access:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has access to this tenant",
        )

    # Check for existing pending invitation
    existing_invitation = (
        db.query(TenantInvitation)
        .filter(
            TenantInvitation.email == invitation_data.email,
            TenantInvitation.tenant_id == current_tenant_id,
            TenantInvitation.status == TenantInvitationStatus.PENDING,
        )
        .first()
    )

    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pending invitation already exists for this user to this tenant",
        )

    # Validate role
    try:
        role = UserRole(invitation_data.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role specified",
        )

    # Create invitation
    token = generate_invitation_token()
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=7
    )  # 7 days expiry

    invitation = TenantInvitation(
        email=invitation_data.email,
        tenant_id=current_tenant_id,
        role=role,
        token=token,
        status=TenantInvitationStatus.PENDING,
        invited_by_user_id=current_user.id,
        invited_by_email=current_user.email,
        expires_at=expires_at,
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    # Send invitation email in background
    tenant_name = invitation.tenant.name if invitation.tenant else "Unknown"
    background_tasks.add_task(
        send_tenant_invitation_email,
        recipient=invitation_data.email,
        tenant_name=tenant_name,
        role=role.value,
        token=token,
        invited_by=current_user.full_name,
    )

    return TenantInvitationResponse(
        id=invitation.id,
        email=invitation.email,
        tenant_id=invitation.tenant_id,
        tenant_name=tenant_name,
        role=invitation.role.value,
        token=invitation.token,
        status=invitation.status.value,
        invited_by_email=invitation.invited_by_email,
        created_at=invitation.created_at,
        expires_at=invitation.expires_at,
        accepted_at=invitation.accepted_at,
    )


@router.get("/", response_model=List[TenantInvitationResponse])
def list_tenant_invitations(
    skip: int = 0,
    limit: int = 100,
    status_filter: TenantInvitationStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin),
):
    """List all tenant invitations for current tenant"""
    current_tenant_id = get_current_tenant_id(current_user)

    if not current_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tenant context",
        )

    query = db.query(TenantInvitation).filter(
        TenantInvitation.tenant_id == current_tenant_id
    )

    if status_filter:
        query = query.filter(TenantInvitation.status == status_filter)

    invitations = (
        query.order_by(TenantInvitation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for inv in invitations:
        tenant_name = inv.tenant.name if inv.tenant else "Unknown"
        result.append(
            TenantInvitationResponse(
                id=inv.id,
                email=inv.email,
                tenant_id=inv.tenant_id,
                tenant_name=tenant_name,
                role=inv.role.value,
                token=inv.token,
                status=inv.status.value,
                invited_by_email=inv.invited_by_email,
                created_at=inv.created_at,
                expires_at=inv.expires_at,
                accepted_at=inv.accepted_at,
            )
        )

    return result


@router.get("/validate/{token}")
def validate_tenant_invitation(token: str, db: Session = Depends(get_db)):
    """Validate a tenant invitation token (public endpoint for existing users)"""
    invitation = (
        db.query(TenantInvitation)
        .filter(TenantInvitation.token == token)
        .first()
    )

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    if invitation.status != TenantInvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation is {invitation.status.value}",
        )

    if invitation.expires_at < datetime.now(timezone.utc):
        # Mark as expired
        invitation.status = TenantInvitationStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )

    tenant_name = invitation.tenant.name if invitation.tenant else "Unknown"

    return {
        "email": invitation.email,
        "tenant_id": invitation.tenant_id,
        "tenant_name": tenant_name,
        "role": invitation.role.value,
        "invited_by_email": invitation.invited_by_email,
        "expires_at": invitation.expires_at,
    }


@router.post("/accept", status_code=status.HTTP_200_OK)
def accept_tenant_invitation(
    accept_data: TenantInvitationAccept,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Accept a tenant invitation. User must be logged in.
    This adds the user to the tenant with the specified role.
    """
    invitation = (
        db.query(TenantInvitation)
        .filter(TenantInvitation.token == accept_data.token)
        .first()
    )

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    if invitation.status != TenantInvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation is {invitation.status.value}",
        )

    if invitation.expires_at < datetime.now(timezone.utc):
        invitation.status = TenantInvitationStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )

    # Verify the invitation is for this user
    if invitation.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation is not for your email address",
        )

    # Check if user already has access (shouldn't happen, but just in case)
    existing_access = (
        db.query(UserTenantRole)
        .filter(
            UserTenantRole.user_id == current_user.id,
            UserTenantRole.tenant_id == invitation.tenant_id,
        )
        .first()
    )

    if existing_access:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have access to this tenant",
        )

    # Add user to tenant with the specified role
    user_tenant_role = UserTenantRole(
        user_id=current_user.id,
        tenant_id=invitation.tenant_id,
        role=invitation.role,
        is_default=False,  # Don't make it default, user can change later
    )

    db.add(user_tenant_role)

    # Mark invitation as accepted
    invitation.status = TenantInvitationStatus.ACCEPTED
    invitation.accepted_at = datetime.now(timezone.utc)

    # Check if this is a demo tenant and if it's empty (no sample data yet)
    tenant = invitation.tenant
    is_demo_tenant = tenant and tenant.is_demo

    # Check if tenant already has sample data (check for demo users or POCs)
    has_sample_data = False
    if is_demo_tenant:
        # Check if there are already demo users or POCs in this tenant
        from app.models.poc import POC

        existing_pocs = (
            db.query(POC).filter(POC.tenant_id == tenant.id).count()
        )
        existing_demo_users = (
            db.query(User)
            .filter(
                User.tenant_id == tenant.id,
                User.is_demo == True,
                User.id != current_user.id,
            )
            .count()
        )
        has_sample_data = existing_pocs > 0 or existing_demo_users > 0

    db.commit()

    # Seed demo data if this is a demo tenant without existing data
    if (
        is_demo_tenant
        and not has_sample_data
        and invitation.role == UserRole.TENANT_ADMIN
    ):
        try:
            seed_result = seed_demo_account(db, tenant.id, current_user.id)
            db.commit()

            # Mark associated demo request as completed
            from app.models.demo_request import DemoRequest

            demo_request = (
                db.query(DemoRequest)
                .filter(
                    DemoRequest.tenant_id == tenant.id,
                    DemoRequest.email == current_user.email,
                    DemoRequest.is_completed == False,
                )
                .first()
            )

            if demo_request:
                demo_request.is_completed = True
                demo_request.completed_at = datetime.now(timezone.utc)
                db.commit()
        except Exception as e:
            # Log error but don't fail the invitation acceptance
            print(
                f"Warning: Failed to seed demo data for tenant {tenant.id}: {e}"
            )

    tenant_name = invitation.tenant.name if invitation.tenant else "Unknown"

    return {
        "message": f"Successfully joined {tenant_name} as {invitation.role.value}",
        "tenant_id": invitation.tenant_id,
        "tenant_name": tenant_name,
        "role": invitation.role.value,
    }


@router.delete("/{invitation_id}")
def revoke_tenant_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin),
):
    """Revoke a tenant invitation"""
    current_tenant_id = get_current_tenant_id(current_user)

    invitation = (
        db.query(TenantInvitation)
        .filter(
            TenantInvitation.id == invitation_id,
            TenantInvitation.tenant_id == current_tenant_id,
        )
        .first()
    )

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    if invitation.status != TenantInvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only revoke pending invitations",
        )

    invitation.status = TenantInvitationStatus.REVOKED
    db.commit()

    return {"message": "Invitation revoked successfully"}
