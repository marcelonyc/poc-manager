"""POC Invitation router"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, timezone
import secrets

from app.database import get_db
from app.models.user import User, UserRole
from app.models.poc import POC, POCParticipant
from app.models.poc_invitation import POCInvitation, POCInvitationStatus
from app.models.user_tenant_role import UserTenantRole
from app.schemas.poc_invitation import (
    POCInvitationCreate,
    POCInvitationResponse,
    POCInvitationAccept,
    POCInvitationToken,
)
from app.auth import get_current_user, get_password_hash, get_current_tenant_id
from app.services.email import send_poc_invitation_email_with_tracking

router = APIRouter(
    prefix="/pocs/{poc_id}/invitations", tags=["POC Invitations"]
)
public_router = APIRouter(
    prefix="/poc-invitations", tags=["POC Invitations - Public"]
)


def generate_invitation_token() -> str:
    """Generate a secure random token for invitation"""
    return secrets.token_urlsafe(32)


@router.post(
    "/",
    response_model=POCInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_poc_invitation(
    poc_id: int,
    invitation_data: POCInvitationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Create a POC invitation"""
    # Check if POC exists and user has access
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POC not found",
        )

    # Check if user has permission (must be in same tenant or Platform Admin)
    if (
        current_user.role != UserRole.PLATFORM_ADMIN
        and tenant_id != poc.tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    # Check for existing pending invitation
    existing_invitation = (
        db.query(POCInvitation)
        .filter(
            POCInvitation.poc_id == poc_id,
            POCInvitation.email == invitation_data.email,
            POCInvitation.status == POCInvitationStatus.PENDING,
        )
        .first()
    )

    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pending invitation already exists for this email",
        )

    # Check if user is already a participant
    existing_user = (
        db.query(User).filter(User.email == invitation_data.email).first()
    )
    if existing_user:
        existing_participant = (
            db.query(POCParticipant)
            .filter(
                POCParticipant.poc_id == poc_id,
                POCParticipant.user_id == existing_user.id,
            )
            .first()
        )
        if existing_participant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a participant in this POC",
            )

    # Create invitation with 24-hour expiry
    token = generate_invitation_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    invitation = POCInvitation(
        poc_id=poc_id,
        email=invitation_data.email,
        full_name=invitation_data.full_name,
        token=token,
        status=POCInvitationStatus.PENDING,
        invited_by=current_user.id,
        is_customer=invitation_data.is_customer,
        personal_message=invitation_data.personal_message,
        expires_at=expires_at,
        email_sent=False,
        resend_count=0,
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    # Send invitation email in background
    background_tasks.add_task(
        send_poc_invitation_email_with_tracking,
        invitation_id=invitation.id,
        recipient=invitation_data.email,
        full_name=invitation_data.full_name,
        poc_title=poc.title,
        token=token,
        invited_by_name=current_user.full_name,
        personal_message=invitation_data.personal_message,
        tenant=poc.tenant,
    )

    return invitation


@router.get("/", response_model=List[POCInvitationResponse])
def list_poc_invitations(
    poc_id: int,
    status_filter: POCInvitationStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    List all invitations for a specific POC.

    Returns invitations sent to participants for this POC, sorted by creation
    date (newest first). Supports filtering by invitation status. The poc_id
    is provided as a path parameter from the router prefix.

    Route: GET /pocs/{poc_id}/invitations/?status_filter=

    Path parameters:
        poc_id (int): The unique identifier of the POC (from URL path).

    Query parameters:
        status_filter (str, optional): Filter by status — one of "pending", "accepted", "expired", "revoked", "failed".

    Returns:
        List of POC invitation objects, each containing:
            - id (int): Unique invitation identifier.
            - poc_id (int): Associated POC identifier.
            - email (str): Invitee email address.
            - full_name (str): Invitee display name.
            - is_customer (bool): Whether invitee is a customer participant.
            - token (str): Invitation token.
            - status (str): Current invitation status.
            - personal_message (str | null): Custom message included in invitation.
            - created_at (datetime): When the invitation was sent.
            - expires_at (datetime): Expiration timestamp.
            - accepted_at (datetime | null): When accepted.
            - resend_count (int): Number of times the invitation was resent.

    Errors:
        404 Not Found: POC does not exist.
        403 Forbidden: Caller's tenant does not match the POC's tenant.
        401 Unauthorized: Missing or invalid authentication token.
    """
    # Check if POC exists and user has access
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POC not found",
        )

    # Check permissions
    if (
        current_user.role != UserRole.PLATFORM_ADMIN
        and tenant_id != poc.tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    query = db.query(POCInvitation).filter(POCInvitation.poc_id == poc_id)

    if status_filter:
        query = query.filter(POCInvitation.status == status_filter)

    invitations = query.order_by(POCInvitation.created_at.desc()).all()
    return invitations


@router.post("/{invitation_id}/resend", response_model=POCInvitationResponse)
async def resend_poc_invitation(
    poc_id: int,
    invitation_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Resend a POC invitation (for pending, expired, or failed invitations)"""
    invitation = (
        db.query(POCInvitation)
        .filter(
            POCInvitation.id == invitation_id, POCInvitation.poc_id == poc_id
        )
        .first()
    )

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    # Check permissions
    poc = invitation.poc
    if (
        current_user.role != UserRole.PLATFORM_ADMIN
        and tenant_id != poc.tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    # Only allow resending for pending, expired or failed invitations
    if invitation.status not in [
        POCInvitationStatus.PENDING,
        POCInvitationStatus.EXPIRED,
        POCInvitationStatus.FAILED,
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot resend invitation with status: {invitation.status.value}",
        )

    # Generate new token and extend expiry
    invitation.token = generate_invitation_token()
    invitation.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    invitation.status = POCInvitationStatus.PENDING
    invitation.email_sent = False
    invitation.email_error = None
    invitation.resend_count += 1
    invitation.last_resent_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(invitation)

    # Send invitation email in background
    background_tasks.add_task(
        send_poc_invitation_email_with_tracking,
        invitation_id=invitation.id,
        recipient=invitation.email,
        full_name=invitation.full_name,
        poc_title=poc.title,
        token=invitation.token,
        invited_by_name=invitation.inviter.full_name,
        personal_message=invitation.personal_message,
        tenant=poc.tenant,
    )

    return invitation


@router.delete("/{invitation_id}")
def revoke_poc_invitation(
    poc_id: int,
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Revoke a pending POC invitation"""
    invitation = (
        db.query(POCInvitation)
        .filter(
            POCInvitation.id == invitation_id, POCInvitation.poc_id == poc_id
        )
        .first()
    )

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    # Check permissions
    poc = invitation.poc
    if (
        current_user.role != UserRole.PLATFORM_ADMIN
        and tenant_id != poc.tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    if invitation.status != POCInvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot revoke invitation with status: {invitation.status.value}",
        )

    invitation.status = POCInvitationStatus.REVOKED
    db.commit()

    return {"message": "Invitation revoked successfully"}


# Public endpoints (no authentication required)


@public_router.get("/validate/{token}", response_model=POCInvitationToken)
def validate_poc_invitation(token: str, db: Session = Depends(get_db)):
    """Validate a POC invitation token (public endpoint)"""
    invitation = (
        db.query(POCInvitation).filter(POCInvitation.token == token).first()
    )

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    if invitation.status != POCInvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation is {invitation.status.value}",
        )

    if invitation.expires_at < datetime.now(timezone.utc):
        invitation.status = POCInvitationStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )

    # Check if user already exists
    user_exists = (
        db.query(User).filter(User.email == invitation.email).first()
        is not None
    )

    return POCInvitationToken(
        poc_id=invitation.poc_id,
        poc_title=invitation.poc.title,
        email=invitation.email,
        full_name=invitation.full_name,
        is_customer=invitation.is_customer,
        invited_by_name=invitation.inviter.full_name,
        expires_at=invitation.expires_at,
        personal_message=invitation.personal_message,
        user_exists=user_exists,
    )


@public_router.post("/accept", status_code=status.HTTP_201_CREATED)
def accept_poc_invitation(
    accept_data: POCInvitationAccept, db: Session = Depends(get_db)
):
    """Accept a POC invitation

    For new users: Requires password, creates account and adds to POC
    For existing users: They should use the authenticated endpoint /accept-existing
    """
    invitation = (
        db.query(POCInvitation)
        .filter(POCInvitation.token == accept_data.token)
        .first()
    )

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    if invitation.status != POCInvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation is {invitation.status.value}",
        )

    if invitation.expires_at < datetime.now(timezone.utc):
        invitation.status = POCInvitationStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )

    # Check if user already exists
    user = db.query(User).filter(User.email == invitation.email).first()
    poc = invitation.poc

    if user:
        # Existing user - they must use the authenticated endpoint
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists. Please login and use the authenticated acceptance endpoint.",
        )

    # New user - password is required
    if not accept_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required for new users",
        )

    # Create new user account
    user = User(
        email=invitation.email,
        full_name=invitation.full_name,
        hashed_password=get_password_hash(accept_data.password),
        role=(
            UserRole.CUSTOMER
            if invitation.is_customer
            else UserRole.SALES_ENGINEER
        ),
        tenant_id=poc.tenant_id,  # Keep for backward compatibility
        is_active=True,
    )
    db.add(user)
    db.flush()

    # Create UserTenantRole entry for multi-tenant support
    # This is required for login to work properly
    user_tenant_role = UserTenantRole(
        user_id=user.id,
        tenant_id=poc.tenant_id,
        role=(
            UserRole.CUSTOMER
            if invitation.is_customer
            else UserRole.SALES_ENGINEER
        ),
        is_default=True,  # First tenant is default
    )
    db.add(user_tenant_role)
    db.flush()

    # Add user as POC participant
    participant = POCParticipant(
        poc_id=invitation.poc_id,
        user_id=user.id,
        is_sales_engineer=not invitation.is_customer,
        is_customer=invitation.is_customer,
    )
    db.add(participant)

    # Mark invitation as accepted
    invitation.status = POCInvitationStatus.ACCEPTED
    invitation.accepted_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "message": "Invitation accepted successfully",
        "user_created": user.id,
        "poc_id": invitation.poc_id,
    }


@public_router.post("/accept-existing", status_code=status.HTTP_200_OK)
def accept_poc_invitation_existing_user(
    accept_data: POCInvitationAccept,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept a POC invitation for an existing user (requires authentication)

    Existing users must be logged in to accept invitations.
    No password is required since they already have an account.
    """
    invitation = (
        db.query(POCInvitation)
        .filter(POCInvitation.token == accept_data.token)
        .first()
    )

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    if invitation.status != POCInvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation is {invitation.status.value}",
        )

    if invitation.expires_at < datetime.now(timezone.utc):
        invitation.status = POCInvitationStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )

    # Verify the invitation is for the current logged-in user
    if invitation.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation is not for your email address",
        )

    poc = invitation.poc

    # Check if user already has access to this tenant
    existing_tenant_role = (
        db.query(UserTenantRole)
        .filter(
            UserTenantRole.user_id == current_user.id,
            UserTenantRole.tenant_id == poc.tenant_id,
        )
        .first()
    )

    # If user doesn't have access to this tenant yet, add them
    if not existing_tenant_role:
        user_tenant_role = UserTenantRole(
            user_id=current_user.id,
            tenant_id=poc.tenant_id,
            role=(
                UserRole.CUSTOMER
                if invitation.is_customer
                else UserRole.SALES_ENGINEER
            ),
            is_default=False,  # Not default for existing users
        )
        db.add(user_tenant_role)
        db.flush()

    # Check if user is already a participant
    existing_participant = (
        db.query(POCParticipant)
        .filter(
            POCParticipant.poc_id == invitation.poc_id,
            POCParticipant.user_id == current_user.id,
        )
        .first()
    )

    if existing_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a participant in this POC",
        )

    # Add user as POC participant
    participant = POCParticipant(
        poc_id=invitation.poc_id,
        user_id=current_user.id,
        is_sales_engineer=not invitation.is_customer,
        is_customer=invitation.is_customer,
    )
    db.add(participant)

    # Mark invitation as accepted
    invitation.status = POCInvitationStatus.ACCEPTED
    invitation.accepted_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "message": "Invitation accepted successfully",
        "poc_id": invitation.poc_id,
    }
