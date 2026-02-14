"""Invitation router for Platform Admin invites"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, timezone
import secrets
from app.database import get_db
from app.models.user import User, UserRole
from app.models.invitation import Invitation, InvitationStatus
from app.models.user_tenant_role import UserTenantRole
from app.schemas.invitation import (
    InvitationCreate,
    InvitationResponse,
    InvitationAccept,
    InvitationToken,
)
from app.auth import require_platform_admin, get_password_hash
from app.services.email import send_invitation_email

router = APIRouter(prefix="/invitations", tags=["Invitations"])


def generate_invitation_token() -> str:
    """Generate a secure random token for invitation"""
    return secrets.token_urlsafe(32)


def _ensure_utc(dt: datetime) -> datetime:
    """Ensure a datetime is timezone-aware (UTC)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@router.post(
    "/", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED
)
async def create_invitation(
    invitation_data: InvitationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
):
    """
    Create a Platform Admin invitation.

    Purpose: Invite a new user to become a Platform Admin. Sends email with acceptance link.
    Invitations expire after 7 days. Each email can have only one pending invitation.

    Args:
        invitation_data: InvitationCreate with email and full_name

    Returns:
        InvitationResponse with invitation details and status

    Requires: Platform Admin role

    Raises:
        400 Bad Request: User already exists or pending invitation exists
        403 Forbidden: Insufficient permissions
    """
    # Check if user already exists
    existing_user = (
        db.query(User).filter(User.email == invitation_data.email).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Check for existing pending invitation
    existing_invitation = (
        db.query(Invitation)
        .filter(
            Invitation.email == invitation_data.email,
            Invitation.status == InvitationStatus.PENDING,
        )
        .first()
    )

    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pending invitation already exists for this email",
        )

    # Create invitation
    token = generate_invitation_token()
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=7
    )  # 7 days expiry

    invitation = Invitation(
        email=invitation_data.email,
        full_name=invitation_data.full_name,
        token=token,
        status=InvitationStatus.PENDING,
        invited_by_email=current_user.email,
        expires_at=expires_at,
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    # Send invitation email in background
    background_tasks.add_task(
        send_invitation_email,
        recipient=invitation_data.email,
        full_name=invitation_data.full_name,
        token=token,
        invited_by=current_user.full_name,
    )

    return invitation


@router.get("/", response_model=List[InvitationResponse])
def list_invitations(
    skip: int = 0,
    limit: int = 100,
    status_filter: InvitationStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
):
    """
    List Platform Admin invitations.

    Returns all invitations sent to prospective platform admins, sorted by
    creation date (newest first). Supports filtering by invitation status.

    Route: GET /invitations/?skip=0&limit=100&status_filter=

    Query parameters:
        skip (int, default 0): Number of records to skip for pagination.
        limit (int, default 100): Maximum number of records to return.
        status_filter (str, optional): Filter by status — one of "pending", "accepted", "expired", "revoked".

    Returns:
        List of invitation objects, each containing:
            - id (int): Unique invitation identifier.
            - email (str): Invitee email address.
            - full_name (str): Invitee display name.
            - token (str): Invitation token.
            - status (str): Current status.
            - invited_by_email (str): Email of the admin who sent the invitation.
            - created_at (datetime): When the invitation was sent.
            - expires_at (datetime): Expiration timestamp.
            - accepted_at (datetime | null): When the invitation was accepted.

    Errors:
        403 Forbidden: Caller is not a platform admin.
        401 Unauthorized: Missing or invalid authentication token.
    """
    query = db.query(Invitation)

    if status_filter:
        query = query.filter(Invitation.status == status_filter)

    invitations = (
        query.order_by(Invitation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return invitations


@router.get("/validate/{token}", response_model=InvitationToken)
def validate_invitation(token: str, db: Session = Depends(get_db)):
    """
    Validate a platform admin invitation token.

    Public endpoint (no authentication required). Checks whether the token
    exists, is still pending, and has not expired. Use this before showing
    the registration form to the invitee.

    Route: GET /invitations/validate/{token}

    Path parameters:
        token (str): The invitation token from the email link.

    Returns:
        Invitation token details:
            - email (str): Invitee email address.
            - full_name (str): Invitee display name.
            - invited_by_email (str): Email of the inviting admin.
            - expires_at (datetime): Token expiration timestamp.

    Errors:
        404 Not Found: Token does not exist.
        400 Bad Request: Invitation is not pending or has expired.
    """
    invitation = db.query(Invitation).filter(Invitation.token == token).first()

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    if invitation.status != InvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation is {invitation.status.value}",
        )

    if _ensure_utc(invitation.expires_at) < datetime.now(timezone.utc):
        # Mark as expired
        invitation.status = InvitationStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )

    return InvitationToken(
        email=invitation.email,
        full_name=invitation.full_name,
        invited_by_email=invitation.invited_by_email,
        expires_at=invitation.expires_at,
        role=invitation.role,
        tenant_name=invitation.tenant.name if invitation.tenant else None,
    )


@router.post("/accept", status_code=status.HTTP_201_CREATED)
def accept_invitation(
    accept_data: InvitationAccept, db: Session = Depends(get_db)
):
    """Accept an invitation and create Platform Admin account (public endpoint)"""
    invitation = (
        db.query(Invitation)
        .filter(Invitation.token == accept_data.token)
        .first()
    )

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    if invitation.status != InvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation is {invitation.status.value}",
        )

    if _ensure_utc(invitation.expires_at) < datetime.now(timezone.utc):
        invitation.status = InvitationStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )

    # Check if user was created in the meantime
    existing_user = (
        db.query(User).filter(User.email == invitation.email).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Determine role: use stored role or default to platform_admin (backward compat)
    user_role = (
        UserRole(invitation.role)
        if invitation.role
        else UserRole.PLATFORM_ADMIN
    )
    user_tenant_id = invitation.tenant_id  # None for platform admins

    # Create user with the appropriate role
    user = User(
        email=invitation.email,
        full_name=invitation.full_name,
        hashed_password=get_password_hash(accept_data.password),
        role=user_role,
        tenant_id=user_tenant_id,
        is_active=True,
    )

    db.add(user)
    db.flush()

    # Create user_tenant_role entry for tenant-scoped users
    if user_tenant_id is not None:
        user_tenant_role = UserTenantRole(
            user_id=user.id,
            tenant_id=user_tenant_id,
            role=user_role,
            is_default=True,
        )
        db.add(user_tenant_role)

    # Mark invitation as accepted
    invitation.status = InvitationStatus.ACCEPTED
    invitation.accepted_at = datetime.now(timezone.utc)

    db.commit()

    role_display = user_role.value.replace("_", " ").title()
    return {
        "message": f"{role_display} account created successfully",
        "email": user.email,
    }


@router.delete("/{invitation_id}")
def revoke_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
):
    """Revoke a pending invitation (Platform Admin only)"""
    invitation = (
        db.query(Invitation).filter(Invitation.id == invitation_id).first()
    )

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    if invitation.status != InvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot revoke invitation with status: {invitation.status.value}",
        )

    invitation.status = InvitationStatus.REVOKED
    db.commit()

    return {"message": "Invitation revoked successfully"}
