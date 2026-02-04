"""POC Invitation router"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import secrets

from app.database import get_db
from app.models.user import User, UserRole
from app.models.poc import POC, POCParticipant
from app.models.poc_invitation import POCInvitation, POCInvitationStatus
from app.schemas.poc_invitation import (
    POCInvitationCreate,
    POCInvitationResponse,
    POCInvitationAccept,
    POCInvitationToken,
)
from app.auth import get_current_user, get_password_hash
from app.services.email import send_poc_invitation_email_with_tracking

router = APIRouter(prefix="/pocs/{poc_id}/invitations", tags=["POC Invitations"])


def generate_invitation_token() -> str:
    """Generate a secure random token for invitation"""
    return secrets.token_urlsafe(32)


@router.post("/", response_model=POCInvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_poc_invitation(
    poc_id: int,
    invitation_data: POCInvitationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    if current_user.role != UserRole.PLATFORM_ADMIN and current_user.tenant_id != poc.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    
    # Check for existing pending invitation
    existing_invitation = db.query(POCInvitation).filter(
        POCInvitation.poc_id == poc_id,
        POCInvitation.email == invitation_data.email,
        POCInvitation.status == POCInvitationStatus.PENDING
    ).first()
    
    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pending invitation already exists for this email",
        )
    
    # Check if user is already a participant
    existing_user = db.query(User).filter(User.email == invitation_data.email).first()
    if existing_user:
        existing_participant = db.query(POCParticipant).filter(
            POCParticipant.poc_id == poc_id,
            POCParticipant.user_id == existing_user.id
        ).first()
        if existing_participant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a participant in this POC",
            )
    
    # Create invitation with 24-hour expiry
    token = generate_invitation_token()
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
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
        resend_count=0
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
        tenant=poc.tenant
    )
    
    return invitation


@router.get("/", response_model=List[POCInvitationResponse])
def list_poc_invitations(
    poc_id: int,
    status_filter: POCInvitationStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all invitations for a POC"""
    # Check if POC exists and user has access
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POC not found",
        )
    
    # Check permissions
    if current_user.role != UserRole.PLATFORM_ADMIN and current_user.tenant_id != poc.tenant_id:
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
    current_user: User = Depends(get_current_user)
):
    """Resend a POC invitation (for pending, expired, or failed invitations)"""
    invitation = db.query(POCInvitation).filter(
        POCInvitation.id == invitation_id,
        POCInvitation.poc_id == poc_id
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )
    
    # Check permissions
    poc = invitation.poc
    if current_user.role != UserRole.PLATFORM_ADMIN and current_user.tenant_id != poc.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    
    # Only allow resending for pending, expired or failed invitations
    if invitation.status not in [POCInvitationStatus.PENDING, POCInvitationStatus.EXPIRED, POCInvitationStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot resend invitation with status: {invitation.status.value}",
        )
    
    # Generate new token and extend expiry
    invitation.token = generate_invitation_token()
    invitation.expires_at = datetime.utcnow() + timedelta(hours=24)
    invitation.status = POCInvitationStatus.PENDING
    invitation.email_sent = False
    invitation.email_error = None
    invitation.resend_count += 1
    invitation.last_resent_at = datetime.utcnow()
    
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
        tenant=poc.tenant
    )
    
    return invitation


@router.delete("/{invitation_id}")
def revoke_poc_invitation(
    poc_id: int,
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revoke a pending POC invitation"""
    invitation = db.query(POCInvitation).filter(
        POCInvitation.id == invitation_id,
        POCInvitation.poc_id == poc_id
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )
    
    # Check permissions
    poc = invitation.poc
    if current_user.role != UserRole.PLATFORM_ADMIN and current_user.tenant_id != poc.tenant_id:
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

@router.get("/public/validate/{token}", response_model=POCInvitationToken)
def validate_poc_invitation(
    token: str,
    db: Session = Depends(get_db)
):
    """Validate a POC invitation token (public endpoint)"""
    invitation = db.query(POCInvitation).filter(POCInvitation.token == token).first()
    
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
    
    if invitation.expires_at < datetime.utcnow():
        invitation.status = POCInvitationStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )
    
    return POCInvitationToken(
        poc_id=invitation.poc_id,
        poc_title=invitation.poc.title,
        email=invitation.email,
        full_name=invitation.full_name,
        is_customer=invitation.is_customer,
        invited_by_name=invitation.inviter.full_name,
        expires_at=invitation.expires_at,
        personal_message=invitation.personal_message
    )


@router.post("/public/accept", status_code=status.HTTP_201_CREATED)
def accept_poc_invitation(
    accept_data: POCInvitationAccept,
    db: Session = Depends(get_db)
):
    """Accept a POC invitation (public endpoint)"""
    invitation = db.query(POCInvitation).filter(POCInvitation.token == accept_data.token).first()
    
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
    
    if invitation.expires_at < datetime.utcnow():
        invitation.status = POCInvitationStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )
    
    # Check if user already exists
    user = db.query(User).filter(User.email == invitation.email).first()
    
    if not user:
        # Create new user account
        poc = invitation.poc
        user = User(
            email=invitation.email,
            full_name=invitation.full_name,
            hashed_password=get_password_hash(accept_data.password),
            role=UserRole.CUSTOMER if invitation.is_customer else UserRole.SALES_ENGINEER,
            tenant_id=poc.tenant_id,
            is_active=True,
        )
        db.add(user)
        db.flush()
    
    # Add user as POC participant
    participant = POCParticipant(
        poc_id=invitation.poc_id,
        user_id=user.id,
        is_sales_engineer=not invitation.is_customer,
        is_customer=invitation.is_customer
    )
    db.add(participant)
    
    # Mark invitation as accepted
    invitation.status = POCInvitationStatus.ACCEPTED
    invitation.accepted_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Invitation accepted successfully",
        "user_created": user.id,
        "poc_id": invitation.poc_id
    }
