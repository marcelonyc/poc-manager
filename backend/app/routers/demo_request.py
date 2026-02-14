"""Demo request endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import secrets
import re

from app.database import get_db
from app.models.demo_request import (
    DemoRequest,
    EmailVerificationToken,
    DemoConversionRequest,
)
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.models.tenant_invitation import (
    TenantInvitation,
    TenantInvitationStatus,
)
from app.models.user_tenant_role import UserTenantRole
from app.schemas.demo_request import (
    DemoRequestCreate,
    DemoRequestResponse,
    VerifyEmailRequest,
    SetPasswordRequest,
    DemoConversionRequestCreate,
    DemoConversionRequestResponse,
    ApproveConversionRequest,
    DemoUserResponse,
    DemoUserList,
    BlockUserRequest,
    UpgradeAccountRequest,
    ResendEmailRequest,
)
from app.services.email import (
    send_demo_verification_email,
    send_demo_welcome_email,
    send_demo_conversion_request_email,
    send_demo_account_started_email,
    send_tenant_invitation_email,
)
from app.auth import get_password_hash, get_current_user, get_current_tenant_id
from app.config import settings
from app.utils.demo_limits import get_demo_limits_info
from app.services.demo_seed import seed_demo_account

router = APIRouter(prefix="/demo", tags=["demo"])


def generate_tenant_slug(company_name: str) -> str:
    """Generate a unique tenant slug from company name"""
    # Remove special characters and convert to lowercase
    slug = re.sub(r"[^a-z0-9]+", "-", company_name.lower()).strip("-")
    # Add random suffix to ensure uniqueness
    slug = f"{slug}-demo-{secrets.token_hex(4)}"
    return slug


@router.post(
    "/request",
    response_model=DemoRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def request_demo_account(
    data: DemoRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Request a demo account.

    If the email belongs to an existing user, we:
    1. Create the demo tenant immediately
    2. Send them an invitation to join the demo tenant
    3. They can accept by logging in with their existing credentials

    If it's a new user, follow the normal flow:
    1. Create demo request
    2. Send email verification
    3. They set password and tenant is created
    """
    # Check if email already exists in users
    existing_user = db.query(User).filter(User.email == data.email).first()

    if existing_user:
        # Existing user requesting demo - create tenant and send invitation

        # Create demo tenant immediately
        tenant_slug = generate_tenant_slug(data.company_name)
        demo_tenant = Tenant(
            name=data.company_name,
            slug=tenant_slug,
            is_demo=True,
            sales_engineers_count=data.sales_engineers_count,
            pocs_per_quarter=data.pocs_per_quarter,
            contact_email=data.email,
            is_active=True,
        )
        db.add(demo_tenant)
        db.commit()
        db.refresh(demo_tenant)

        # Create tenant invitation for existing user
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        tenant_invitation = TenantInvitation(
            email=data.email,
            tenant_id=demo_tenant.id,
            role=UserRole.TENANT_ADMIN,
            token=token,
            status=TenantInvitationStatus.PENDING,
            invited_by_user_id=existing_user.id,  # Self-invitation for demo
            invited_by_email="demo-system@pocmanager.com",
            expires_at=expires_at,
        )
        db.add(tenant_invitation)
        db.commit()

        # Send invitation email
        background_tasks.add_task(
            send_tenant_invitation_email,
            recipient=data.email,
            tenant_name=data.company_name,
            role="Tenant Admin",
            token=token,
            invited_by="POC Manager Demo System",
        )

        # Create a demo request record for tracking
        demo_request = DemoRequest(
            name=data.name,
            email=data.email,
            company_name=data.company_name,
            sales_engineers_count=data.sales_engineers_count,
            pocs_per_quarter=data.pocs_per_quarter,
            is_verified=True,  # Already verified (existing user)
            verified_at=datetime.now(timezone.utc),
            is_completed=False,  # Will be completed when they accept invitation
            tenant_id=demo_tenant.id,
            user_id=existing_user.id,
        )
        db.add(demo_request)
        db.commit()
        db.refresh(demo_request)

        platform_admins = (
            db.query(User)
            .filter(
                User.role == UserRole.PLATFORM_ADMIN,
                User.is_active == True,
            )
            .all()
        )

        for admin in platform_admins:
            background_tasks.add_task(
                send_demo_account_started_email,
                admin.email,
                data.name,
                data.email,
                data.company_name,
                data.sales_engineers_count,
                data.pocs_per_quarter,
                True,
            )

        return demo_request

    # New user - follow normal demo request flow
    # Check if email already exists in pending demo requests
    existing_request = (
        db.query(DemoRequest)
        .filter(
            DemoRequest.email == data.email, DemoRequest.is_completed == False
        )
        .first()
    )

    if existing_request:
        # Resend verification email for the existing request
        token = secrets.token_urlsafe(32)
        verification_token = EmailVerificationToken(
            demo_request_id=existing_request.id,
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        db.add(verification_token)
        db.commit()

        background_tasks.add_task(
            send_demo_verification_email,
            existing_request.email,
            existing_request.name,
            token,
        )

        return existing_request

    # Create new demo request
    demo_request = DemoRequest(
        name=data.name,
        email=data.email,
        company_name=data.company_name,
        sales_engineers_count=data.sales_engineers_count,
        pocs_per_quarter=data.pocs_per_quarter,
    )
    db.add(demo_request)
    db.commit()
    db.refresh(demo_request)

    platform_admins = (
        db.query(User)
        .filter(
            User.role == UserRole.PLATFORM_ADMIN,
            User.is_active == True,
        )
        .all()
    )

    for admin in platform_admins:
        background_tasks.add_task(
            send_demo_account_started_email,
            admin.email,
            data.name,
            data.email,
            data.company_name,
            data.sales_engineers_count,
            data.pocs_per_quarter,
            False,
        )

    # Create verification token
    token = secrets.token_urlsafe(32)
    verification_token = EmailVerificationToken(
        demo_request_id=demo_request.id,
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db.add(verification_token)
    db.commit()

    # Send verification email in background
    background_tasks.add_task(
        send_demo_verification_email,
        demo_request.email,
        demo_request.name,
        token,
    )

    return demo_request


@router.post("/verify-email")
async def verify_demo_email(
    data: VerifyEmailRequest, db: Session = Depends(get_db)
):
    """Verify email address for demo request"""
    # Find verification token
    verification_token = (
        db.query(EmailVerificationToken)
        .filter(EmailVerificationToken.token == data.token)
        .first()
    )

    if not verification_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid verification token",
        )

    if verification_token.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has already been used",
        )

    if datetime.now(timezone.utc) > verification_token.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired",
        )

    # Mark demo request as verified
    demo_request = verification_token.demo_request
    demo_request.is_verified = True
    demo_request.verified_at = datetime.now(timezone.utc)

    # Mark token as used
    verification_token.used = True
    verification_token.used_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "message": "Email verified successfully. Please set your password to complete setup."
    }


@router.post("/set-password")
async def set_demo_password(
    data: SetPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Set password and complete demo account setup for new users"""
    # Find verification token
    verification_token = (
        db.query(EmailVerificationToken)
        .filter(EmailVerificationToken.token == data.token)
        .first()
    )

    if not verification_token or not verification_token.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unverified token",
        )

    demo_request = verification_token.demo_request

    if demo_request.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Demo account setup is already complete",
        )

    # Create tenant
    tenant_slug = generate_tenant_slug(demo_request.company_name)
    tenant = Tenant(
        name=demo_request.company_name,
        slug=tenant_slug,
        is_demo=True,
        sales_engineers_count=demo_request.sales_engineers_count,
        pocs_per_quarter=demo_request.pocs_per_quarter,
        contact_email=demo_request.email,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    # Create user (without role/tenant_id, will use user_tenant_roles)
    user = User(
        email=demo_request.email,
        full_name=demo_request.name,
        hashed_password=get_password_hash(data.password),
        is_active=True,
        is_demo=True,
        # Note: role and tenant_id columns still exist but deprecated
        role=UserRole.TENANT_ADMIN,  # Keep for backward compatibility during migration
        tenant_id=tenant.id,  # Keep for backward compatibility during migration
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create user-tenant-role association (new multi-tenant approach)
    user_tenant_role = UserTenantRole(
        user_id=user.id,
        tenant_id=tenant.id,
        role=UserRole.TENANT_ADMIN,
        is_default=True,
    )
    db.add(user_tenant_role)
    db.commit()

    # Update demo request
    demo_request.is_completed = True
    demo_request.completed_at = datetime.now(timezone.utc)
    demo_request.tenant_id = tenant.id
    demo_request.user_id = user.id
    db.commit()

    # Seed dummy data for the demo account
    seed_result = seed_demo_account(db, tenant.id, user.id)

    # Send welcome email in background
    background_tasks.add_task(
        send_demo_welcome_email,
        demo_request.email,
        demo_request.name,
        demo_request.company_name,
        tenant_slug,
    )

    return {
        "message": "Demo account setup complete!",
        "tenant_slug": tenant_slug,
        "user_id": user.id,
        "seed_result": seed_result,
    }


@router.get("/validate-token/{token}")
async def validate_verification_token(
    token: str, db: Session = Depends(get_db)
):
    """
    Validate a demo request email verification token.

    Public endpoint (no authentication required). Checks whether the token
    exists and has not expired. Returns the demo request details associated
    with the token to populate the setup form.

    Route: GET /demo/validate-token/{token}

    Path parameters:
        token (str): The email verification token.

    Returns:
        Dict containing:
            - valid (bool): Always true if returned successfully.
            - is_verified (bool): Whether the demo request email has been verified.
            - is_completed (bool): Whether the demo account setup is complete.
            - name (str): Requestor's name.
            - email (str): Requestor's email.
            - company_name (str): Requestor's company name.

    Errors:
        404 Not Found: Token does not exist.
        400 Bad Request: Token has expired.
    """
    verification_token = (
        db.query(EmailVerificationToken)
        .filter(EmailVerificationToken.token == token)
        .first()
    )

    if not verification_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid token"
        )

    if datetime.now(timezone.utc) > verification_token.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token has expired"
        )

    demo_request = verification_token.demo_request

    return {
        "valid": True,
        "is_verified": demo_request.is_verified,
        "is_completed": demo_request.is_completed,
        "name": demo_request.name,
        "email": demo_request.email,
        "company_name": demo_request.company_name,
    }


@router.post(
    "/request-conversion", response_model=DemoConversionRequestResponse
)
async def request_demo_conversion(
    data: DemoConversionRequestCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Request conversion of demo account to real account"""
    # Check if user's tenant is a demo account
    if not current_user.tenant or not current_user.tenant.is_demo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint is only for demo accounts",
        )

    # Check if there's already a pending request
    existing_request = (
        db.query(DemoConversionRequest)
        .filter(
            DemoConversionRequest.tenant_id == tenant_id,
            DemoConversionRequest.status == "pending",
        )
        .first()
    )

    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A conversion request is already pending for this account",
        )

    # Create conversion request
    conversion_request = DemoConversionRequest(
        tenant_id=tenant_id,
        requested_by_user_id=current_user.id,
        reason=data.reason,
    )
    db.add(conversion_request)
    db.commit()
    db.refresh(conversion_request)

    # Send email to ALL platform admin users
    platform_admins = (
        db.query(User)
        .filter(
            User.role == UserRole.PLATFORM_ADMIN,
            User.is_active == True,
        )
        .all()
    )

    for admin in platform_admins:
        background_tasks.add_task(
            send_demo_conversion_request_email,
            admin.email,
            current_user.tenant.name,
            current_user.full_name,
            current_user.email,
            data.reason or "No reason provided",
            conversion_request.id,
        )

    return conversion_request


@router.post("/conversions/{request_id}/approve")
async def approve_demo_conversion(
    request_id: int,
    data: ApproveConversionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Approve or reject demo conversion request (Platform Admin only)"""
    # Check if user is platform admin
    if current_user.role != UserRole.PLATFORM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only platform administrators can approve conversions",
        )

    # Find conversion request
    conversion_request = (
        db.query(DemoConversionRequest)
        .filter(DemoConversionRequest.id == request_id)
        .first()
    )

    if not conversion_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversion request not found",
        )

    if conversion_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This request has already been processed",
        )

    # Update request
    conversion_request.approved = data.approved
    conversion_request.status = "approved" if data.approved else "rejected"
    conversion_request.approved_by_user_id = current_user.id
    conversion_request.approved_at = datetime.now(timezone.utc)

    if not data.approved and data.rejection_reason:
        conversion_request.rejection_reason = data.rejection_reason

    # If approved, convert tenant to non-demo
    if data.approved:
        tenant = conversion_request.tenant
        tenant.is_demo = False
        # Remove demo limits by setting them to None
        tenant.sales_engineers_count = None
        tenant.pocs_per_quarter = None

    db.commit()

    return {
        "message": f"Conversion request {'approved' if data.approved else 'rejected'} successfully",
        "request_id": conversion_request.id,
        "status": conversion_request.status,
    }


@router.get("/conversions", response_model=list[DemoConversionRequestResponse])
async def list_conversion_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all demo-to-production conversion requests.

    Returns all conversion requests across the platform, sorted by creation
    date (newest first). Use this to review and manage pending demo account
    upgrade requests.

    Route: GET /demo/conversions

    Returns:
        List of conversion request objects, each containing:
            - id (int): Unique request identifier.
            - tenant_id (int): Demo tenant requesting conversion.
            - requested_by_user_id (int): User who initiated the request.
            - reason (str | null): Reason for conversion.
            - status (str): One of "pending", "approved", "rejected".
            - approved (bool | null): Whether the request was approved.
            - approved_by_user_id (int | null): Admin who processed the request.
            - approved_at (datetime | null): When the request was processed.
            - rejection_reason (str | null): Reason if rejected.
            - created_at (datetime): When the request was submitted.

    Errors:
        403 Forbidden: Caller is not a platform admin.
        401 Unauthorized: Missing or invalid authentication token.
    """
    if current_user.role != UserRole.PLATFORM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only platform administrators can view conversion requests",
        )

    requests = (
        db.query(DemoConversionRequest)
        .order_by(DemoConversionRequest.created_at.desc())
        .all()
    )

    return requests


@router.get("/limits")
async def get_demo_limits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Get demo account limits and current usage.

    Returns the resource limits configured for the demo tenant and how much
    of each limit has been consumed. Useful for showing usage gauges in the
    demo account UI.

    Route: GET /demo/limits

    Returns:
        Dict containing limit and usage information for the demo tenant,
        including resource caps and current consumption counts.

    Errors:
        401 Unauthorized: Missing or invalid authentication token.
    """
    return get_demo_limits_info(db, tenant_id, current_user.tenant)


# Platform Admin Demo Management Endpoints


@router.get("/users", response_model=DemoUserList)
async def list_demo_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all demo account requests.

    Returns every demo request submitted to the platform, sorted by creation
    date (newest first). Includes verification and completion status as well
    as linked tenant information.

    Route: GET /demo/users

    Returns:
        Object containing:
            - total (int): Total number of demo requests.
            - users (list): Demo request objects, each with:
                - id (int): Unique demo request identifier.
                - name (str): Requestor name.
                - email (str): Requestor email.
                - company_name (str): Company name.
                - sales_engineers_count (int | null): Requested SE count.
                - pocs_per_quarter (int | null): Requested POC quota.
                - is_verified (bool): Email verified.
                - is_completed (bool): Account setup completed.
                - tenant_id (int | null): Created tenant ID.
                - user_id (int | null): Created user ID.
                - tenant_name (str | null): Created tenant name.
                - created_at (datetime): Request submission time.
                - verified_at (datetime | null): Email verification time.
                - completed_at (datetime | null): Account setup completion time.

    Errors:
        403 Forbidden: Caller is not a platform admin.
        401 Unauthorized: Missing or invalid authentication token.
    """
    if current_user.role != UserRole.PLATFORM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only platform administrators can view demo requests",
        )

    # Query all demo requests
    demo_requests = (
        db.query(DemoRequest).order_by(DemoRequest.created_at.desc()).all()
    )

    # Build response with tenant names
    requests_response = []
    for demo_req in demo_requests:
        tenant_name = None
        if demo_req.tenant_id and demo_req.tenant:
            tenant_name = demo_req.tenant.name

        requests_response.append(
            DemoUserResponse(
                id=demo_req.id,
                name=demo_req.name,
                email=demo_req.email,
                company_name=demo_req.company_name,
                sales_engineers_count=demo_req.sales_engineers_count,
                pocs_per_quarter=demo_req.pocs_per_quarter,
                is_verified=demo_req.is_verified,
                is_completed=demo_req.is_completed,
                tenant_id=demo_req.tenant_id,
                user_id=demo_req.user_id,
                tenant_name=tenant_name,
                created_at=demo_req.created_at,
                verified_at=demo_req.verified_at,
                completed_at=demo_req.completed_at,
            )
        )

    return DemoUserList(total=len(requests_response), users=requests_response)


@router.post("/users/{user_id}/block")
async def block_demo_user(
    user_id: int,
    data: BlockUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Block or unblock a demo user (Platform Admin only)"""
    if current_user.role != UserRole.PLATFORM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only platform administrators can block users",
        )

    # Find the demo request by ID
    demo_request = (
        db.query(DemoRequest).filter(DemoRequest.id == user_id).first()
    )

    if not demo_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo request not found",
        )

    # If the demo request has been completed and has a user, block that user
    if demo_request.is_completed and demo_request.user_id:
        user = db.query(User).filter(User.id == demo_request.user_id).first()
        if user:
            user.is_blocked = data.is_blocked
            db.commit()
            action = "blocked" if data.is_blocked else "unblocked"
            return {
                "message": f"User {action} successfully",
                "user_id": user_id,
                "is_blocked": user.is_blocked,
            }

    # If not completed yet, we can't block (no user exists)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Cannot block a demo request that hasn't been completed yet",
    )


@router.post("/users/{user_id}/upgrade")
async def upgrade_demo_account(
    user_id: int,
    data: UpgradeAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upgrade a demo account to a real account (Platform Admin only)"""
    if current_user.role != UserRole.PLATFORM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only platform administrators can upgrade accounts",
        )

    # Find the demo request by ID
    demo_request = (
        db.query(DemoRequest).filter(DemoRequest.id == user_id).first()
    )

    if not demo_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo request not found",
        )

    if not demo_request.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upgrade a demo request that hasn't been completed yet",
        )

    # Upgrade the associated user and tenant
    if demo_request.user_id:
        user = db.query(User).filter(User.id == demo_request.user_id).first()
        if user:
            user.is_demo = False

    if demo_request.tenant_id:
        tenant = (
            db.query(Tenant)
            .filter(Tenant.id == demo_request.tenant_id)
            .first()
        )
        if tenant:
            tenant.is_demo = False
            # Remove demo limits
            tenant.sales_engineers_count = None
            tenant.pocs_per_quarter = None

            # Upgrade all users in the tenant
            tenant_users = (
                db.query(User).filter(User.tenant_id == tenant.id).all()
            )
            for tenant_user in tenant_users:
                tenant_user.is_demo = False

    db.commit()

    return {
        "message": "Account upgraded to real account successfully",
        "user_id": user_id,
        "tenant_id": demo_request.tenant_id,
    }


@router.post("/users/{user_id}/resend-email")
async def resend_demo_email(
    user_id: int,
    data: ResendEmailRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Resend verification or welcome email (Platform Admin only)"""
    if current_user.role != UserRole.PLATFORM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only platform administrators can resend emails",
        )

    # Find the demo request by ID
    demo_request = (
        db.query(DemoRequest).filter(DemoRequest.id == user_id).first()
    )

    if not demo_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo request not found",
        )

    # If not verified yet, resend verification email
    if not demo_request.is_verified:
        # Create new verification token
        token = secrets.token_urlsafe(32)
        verification_token = EmailVerificationToken(
            demo_request_id=demo_request.id,
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        db.add(verification_token)
        db.commit()

        background_tasks.add_task(
            send_demo_verification_email,
            demo_request.email,
            demo_request.name,
            token,
        )

        return {
            "message": "Verification email sent successfully",
            "user_id": user_id,
            "email": demo_request.email,
        }

    # If completed, resend welcome email
    if demo_request.is_completed and demo_request.tenant:
        background_tasks.add_task(
            send_demo_welcome_email,
            demo_request.email,
            demo_request.name,
            demo_request.tenant.name,
            demo_request.tenant.slug,
        )

        return {
            "message": "Welcome email sent successfully",
            "user_id": user_id,
            "email": demo_request.email,
        }

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Cannot resend email for this demo request state",
    )
