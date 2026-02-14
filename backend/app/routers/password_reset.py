"""Password reset router"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
import secrets
from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.password_reset import PasswordResetToken
from app.services.email import send_password_reset_email
from app.auth import get_password_hash

router = APIRouter(prefix="/auth", tags=["Authentication"])


class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset"""

    token: str
    new_password: str


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def request_password_reset(
    data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Request password reset via email.

    Purpose: Initiate password recovery flow. Always returns success (never indicates if email exists)
    to prevent user enumeration attacks. Only sends email if user account exists and is not blocked.

    Args:
        data: PasswordResetRequest with email address

    Returns:
        Dict with generic success message (same regardless of email validity)

    Note: Password reset links expire after 1 hour
    """
    # Find user by email
    user = db.query(User).filter(User.email == data.email).first()

    if user and not user.is_blocked:
        # Generate secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        # Create password reset token
        reset_token = PasswordResetToken(
            user_id=user.id, token=token, expires_at=expires_at
        )
        db.add(reset_token)
        db.commit()

        # Get tenant for email settings
        tenant = None
        if user.tenant_id:
            tenant = (
                db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
            )

        # Send email in background
        background_tasks.add_task(
            send_password_reset_email,
            recipient=user.email,
            full_name=user.full_name,
            token=token,
            tenant=tenant,
        )

    # Always return the same message to prevent user enumeration
    return {
        "message": "If the email address is associated with an account, you will receive a password reset link shortly."
    }


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """
    Reset password using valid token.

    Purpose: Complete password recovery by setting new password. Token must be valid, unexpired,
    and unused. Each token can only be used once.

    Args:
        data: PasswordResetConfirm with token and new_password

    Returns:
        Dict with success message

    Raises:
        400 Bad Request: Invalid, expired, or already-used token
        404 Not Found: User not found
    """
    # Find the token
    reset_token = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token == data.token)
        .first()
    )

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Check if token is expired
    if reset_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired",
        )

    # Check if token was already used
    if reset_token.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has already been used",
        )

    # Get the user
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update user password
    user.hashed_password = get_password_hash(data.new_password)

    # Mark token as used
    reset_token.used = True
    reset_token.used_at = datetime.now(timezone.utc)

    db.commit()

    return {"message": "Password has been reset successfully"}


@router.get("/validate-reset-token/{token}")
def validate_reset_token(token: str, db: Session = Depends(get_db)):
    """
    Validate password reset token.

    Purpose: Check if a reset token is valid, unexpired, and unused before password reset form.

    Args:
        token (str): Reset token from email link

    Returns:
        Dict indicating token validity

    Raises:
        400 Bad Request: Token invalid, expired, or already used
    """

    reset_token = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token == token)
        .first()
    )

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )

    if reset_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired",
        )

    if reset_token.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has already been used",
        )

    return {"valid": True, "message": "Token is valid"}
