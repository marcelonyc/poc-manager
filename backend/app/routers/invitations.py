"""Invitation router for Platform Admin invites"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import secrets
from app.database import get_db
from app.models.user import User, UserRole
from app.models.invitation import Invitation, InvitationStatus
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


@router.post("/", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_invitation(
    invitation_data: InvitationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin)
):
    """Create a Platform Admin invitation (Platform Admin only)"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == invitation_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    
    # Check for existing pending invitation
    existing_invitation = db.query(Invitation).filter(
        Invitation.email == invitation_data.email,
        Invitation.status == InvitationStatus.PENDING
    ).first()
    
    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pending invitation already exists for this email",
        )
    
    # Create invitation
    token = generate_invitation_token()
    expires_at = datetime.utcnow() + timedelta(days=7)  # 7 days expiry
    
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
    current_user: User = Depends(require_platform_admin)
):
    """List all Platform Admin invitations (Platform Admin only)"""
    query = db.query(Invitation)
    
    if status_filter:
        query = query.filter(Invitation.status == status_filter)
    
    invitations = query.order_by(Invitation.created_at.desc()).offset(skip).limit(limit).all()
    return invitations


@router.get("/validate/{token}", response_model=InvitationToken)
def validate_invitation(
    token: str,
    db: Session = Depends(get_db)
):
    """Validate an invitation token (public endpoint)"""
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
    
    if invitation.expires_at < datetime.utcnow():
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
    )


@router.post("/accept", status_code=status.HTTP_201_CREATED)
def accept_invitation(
    accept_data: InvitationAccept,
    db: Session = Depends(get_db)
):
    """Accept an invitation and create Platform Admin account (public endpoint)"""
    invitation = db.query(Invitation).filter(Invitation.token == accept_data.token).first()
    
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
    
    if invitation.expires_at < datetime.utcnow():
        invitation.status = InvitationStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )
    
    # Check if user was created in the meantime
    existing_user = db.query(User).filter(User.email == invitation.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    
    # Create Platform Admin user
    user = User(
        email=invitation.email,
        full_name=invitation.full_name,
        hashed_password=get_password_hash(accept_data.password),
        role=UserRole.PLATFORM_ADMIN,
        tenant_id=None,  # Platform Admins don't belong to a tenant
        is_active=True,
    )
    
    db.add(user)
    
    # Mark invitation as accepted
    invitation.status = InvitationStatus.ACCEPTED
    invitation.accepted_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Platform Admin account created successfully",
        "email": user.email,
    }


@router.delete("/{invitation_id}")
def revoke_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin)
):
    """Revoke a pending invitation (Platform Admin only)"""
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    
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
