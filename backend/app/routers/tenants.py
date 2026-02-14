"""Tenant router - Platform Admin only"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from pathlib import Path
from app.database import get_db
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.config import settings
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    Tenant as TenantSchema,
    TenantEmailConfig,
    TestEmailRequest,
)
from app.models.user_tenant_role import UserTenantRole
from app.auth import (
    require_platform_admin,
    require_tenant_admin,
    get_current_user,
    get_password_hash,
    get_current_tenant_id,
)
from app.config import settings
from app.services.email import send_email

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post(
    "/", response_model=TenantSchema, status_code=status.HTTP_201_CREATED
)
def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
):
    """
    Create a new tenant and initialize with a tenant admin.

    Purpose: Set up a new tenant (organization) in the platform with custom branding,
    contact information, and user limits. Creates an initial tenant admin account.

    Args:
        tenant_data: TenantCreate object containing:
            - name (str): Tenant display name
            - slug (str): URL-friendly tenant identifier (must be unique)
            - primary_color (str): Primary brand color (hex code)
            - secondary_color (str): Secondary brand color (hex code)
            - contact_email (str): Tenant contact email
            - contact_phone (str): Tenant contact phone
            - initial_admin_email (str): Email for initial tenant admin
            - initial_admin_name (str): Name for initial tenant admin
            - initial_admin_password (str): Password for initial tenant admin

    Returns:
        TenantSchema with created tenant details including tenant ID and configuration

    Requires: Platform Admin authentication

    Raises:
        400 Bad Request: Tenant slug already exists
        403 Forbidden: User is not a Platform Admin
    """
    # Check if tenant with same slug exists
    existing = db.query(Tenant).filter(Tenant.slug == tenant_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant with this slug already exists",
        )

    # Create tenant
    tenant = Tenant(
        name=tenant_data.name,
        slug=tenant_data.slug,
        primary_color=tenant_data.primary_color,
        secondary_color=tenant_data.secondary_color,
        contact_email=tenant_data.contact_email,
        contact_phone=tenant_data.contact_phone,
        tenant_admin_limit=settings.DEFAULT_TENANT_ADMIN_LIMIT,
        administrator_limit=settings.DEFAULT_ADMINISTRATOR_LIMIT,
        sales_engineer_limit=settings.DEFAULT_SALES_ENGINEER_LIMIT,
        account_executive_limit=settings.DEFAULT_ACCOUNT_EXECUTIVE_LIMIT,
        customer_limit=settings.DEFAULT_CUSTOMER_LIMIT,
    )
    db.add(tenant)
    db.flush()

    # Create initial tenant admin
    admin_user = User(
        email=tenant_data.initial_admin_email,
        full_name=tenant_data.initial_admin_name,
        hashed_password=get_password_hash(tenant_data.initial_admin_password),
        role=UserRole.TENANT_ADMIN,
        tenant_id=tenant.id,
        is_active=True,
    )
    db.add(admin_user)
    db.flush()

    # Create user_tenant_role entry so user can log in
    user_tenant_role = UserTenantRole(
        user_id=admin_user.id,
        tenant_id=tenant.id,
        role=UserRole.TENANT_ADMIN,
        is_default=True,
    )
    db.add(user_tenant_role)
    db.commit()
    db.refresh(tenant)

    return tenant


@router.get("/", response_model=List[TenantSchema])
def list_tenants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
):
    """
    List all tenants on the platform.

    Returns a paginated list of every tenant with their configuration,
    branding, and computed status fields. Only accessible to platform admins.

    Route: GET /tenants/?skip=0&limit=100

    Query parameters:
        skip (int, default 0): Number of records to skip for pagination.
        limit (int, default 100): Maximum number of records to return.

    Returns:
        List of tenant objects, each containing:
            - id (int): Unique tenant identifier.
            - name (str): Tenant display name.
            - slug (str): URL-safe tenant identifier.
            - is_active (bool): Whether the tenant is active.
            - contact_email (str | null): Primary contact email.
            - primary_color (str | null): Brand primary color hex.
            - logo_url (str | null): URL to tenant logo.
            - has_custom_mail_config (bool): Whether custom SMTP is configured.
            - has_ollama_api_key (bool): Whether AI assistant API key is set.
            - created_at (datetime): Creation timestamp.

    Errors:
        403 Forbidden: Caller is not a platform admin.
        401 Unauthorized: Missing or invalid authentication token.
    """
    tenants = db.query(Tenant).offset(skip).limit(limit).all()
    # Add computed property for each tenant
    result = []
    for tenant in tenants:
        tenant_dict = {
            **tenant.__dict__,
            "has_custom_mail_config": bool(
                tenant.custom_mail_server and tenant.custom_mail_username
            ),
            "has_ollama_api_key": bool(tenant.ollama_api_key),
            "ollama_model": settings.OLLAMA_MODEL,
        }
        result.append(tenant_dict)
    return result


@router.get("/{tenant_id}", response_model=TenantSchema)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Get tenant details by ID.

    Retrieves a tenant's complete configuration including branding, contact
    info, email settings, and user limits. Platform admins can view any
    tenant; other users can only view the tenant matching their session context.

    Route: GET /tenants/{tenant_id}

    Path parameters:
        tenant_id (int): The unique identifier of the tenant to retrieve.

    Returns:
        Tenant object containing:
            - id (int): Unique tenant identifier.
            - name (str): Tenant display name.
            - slug (str): URL-safe tenant identifier.
            - is_active (bool): Whether the tenant is active.
            - contact_email (str | null): Primary contact email.
            - primary_color (str | null): Brand primary color hex.
            - secondary_color (str | null): Brand secondary color hex.
            - logo_url (str | null): URL to tenant logo.
            - max_users (int | null): User limit for this tenant.
            - has_custom_mail_config (bool): Whether custom SMTP is configured.
            - has_ollama_api_key (bool): Whether AI assistant API key is set.
            - created_at (datetime): Creation timestamp.

    Errors:
        404 Not Found: Tenant does not exist or caller lacks access.
        401 Unauthorized: Missing or invalid authentication token.
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Check access
    if (
        current_user.role != UserRole.PLATFORM_ADMIN
        and user_tenant_id != tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Add computed property for email config status
    tenant_dict = {
        **tenant.__dict__,
        "has_custom_mail_config": bool(
            tenant.custom_mail_server and tenant.custom_mail_username
        ),
        "has_ollama_api_key": bool(tenant.ollama_api_key),
        "ollama_model": settings.OLLAMA_MODEL,
    }

    return tenant_dict


@router.put("/{tenant_id}", response_model=TenantSchema)
def update_tenant(
    tenant_id: int,
    tenant_data: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin),
    user_tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Update tenant configuration.

    Purpose: Modify tenant branding, contact information, colors, and other settings.
    Only Tenant Admins can update their own tenant. Platform Admins can update is_active status.

    Args:
        tenant_id (int): ID of tenant to update
        tenant_data: TenantUpdate object with fields to update

    Returns:
        Updated TenantSchema

    Requires: Tenant Admin (update own tenant) or Platform Admin (full control)

    Raises:
        404 Not Found: Tenant not found
        403 Forbidden: Only Platform Admins can change is_active status
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Check access
    if (
        current_user.role != UserRole.PLATFORM_ADMIN
        and user_tenant_id != tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Only Platform Admins can change is_active
    update_data = tenant_data.model_dump(exclude_unset=True)
    if (
        "is_active" in update_data
        and current_user.role != UserRole.PLATFORM_ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Platform Admins can activate/deactivate tenants",
        )

    # Update fields
    for field, value in update_data.items():
        setattr(tenant, field, value)

    db.commit()
    db.refresh(tenant)
    return tenant


@router.put("/{tenant_id}/email-config")
def update_email_config(
    tenant_id: int,
    email_config: TenantEmailConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin),
    user_tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Update tenant SMTP email configuration.

    Purpose: Configure custom SMTP server settings for sending tenant-specific emails.
    Allows tenants to use their own mail server instead of platform default.

    Args:
        tenant_id (int): ID of tenant to configure
        email_config: TenantEmailConfig with SMTP server details:
            - custom_mail_server (str): SMTP server address
            - custom_mail_port (int): SMTP port
            - custom_mail_username (str): SMTP username
            - custom_mail_password (str): SMTP password
            - custom_mail_from_address (str): Sender email address

    Returns:
        Dict with message: Email configuration updated successfully

    Requires: Tenant Admin in this tenant

    Raises:
        404 Not Found: Tenant not found
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Check access
    if (
        current_user.role != UserRole.PLATFORM_ADMIN
        and user_tenant_id != tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Update email config
    config_data = email_config.model_dump(exclude_unset=True)
    for field, value in config_data.items():
        setattr(tenant, field, value)

    db.commit()
    return {"message": "Email configuration updated successfully"}


@router.post("/{tenant_id}/test-email")
async def send_test_email(
    tenant_id: int,
    test_request: TestEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin),
    user_tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Send a test email to verify SMTP configuration.

    Purpose: Validate that custom SMTP email configuration is working correctly
    by sending a test email to a specified address.

    Args:
        tenant_id (int): ID of tenant with SMTP configuration to test
        test_request: TestEmailRequest containing:
            - recipient_email (str): Email address to receive test message

    Returns:
        Dict with success status and confirmation message

    Requires: Tenant Admin in this tenant

    Raises:
        404 Not Found: Tenant not found
        500 Internal Server Error: SMTP configuration error or sending failed
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Check access
    if (
        current_user.role != UserRole.PLATFORM_ADMIN
        and user_tenant_id != tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Prepare test email content
    subject = "POC Manager - Test Email"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #4F46E5;">Email Configuration Test</h2>
            <p>This is a test email from POC Manager.</p>
            <p>If you received this email, your SMTP configuration is working correctly!</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="color: #666; font-size: 14px;">
                <strong>Tenant:</strong> {tenant.name}<br>
                <strong>Sent by:</strong> {current_user.full_name} ({current_user.email})<br>
                <strong>Configuration:</strong> {"Custom SMTP" if tenant.custom_mail_server else "Platform Default"}
            </p>
        </body>
    </html>
    """

    try:
        await send_email(
            recipients=[test_request.recipient_email],
            subject=subject,
            body=body,
            tenant=tenant,
            html=True,
        )
        return {
            "success": True,
            "message": f"Test email sent successfully to {test_request.recipient_email}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test email: {str(e)}",
        )


@router.post("/{tenant_id}/logo")
async def upload_tenant_logo(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin),
    logo: UploadFile = File(...),
    user_tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Upload tenant logo image.

    Purpose: Upload and store a logo image for tenant branding. Replaces existing logo if present.
    Supported formats: JPEG, PNG, GIF, WebP (max 2MB).

    Args:
        tenant_id (int): ID of tenant
        logo: UploadFile image file (must be valid image format, max 2MB)

    Returns:
        Dict with message and logo_url for accessing the uploaded image

    Requires: Tenant Admin in this tenant

    Raises:
        400 Bad Request: Invalid file type or file too large
        404 Not Found: Tenant not found
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Check access
    if (
        current_user.role != UserRole.PLATFORM_ADMIN
        and user_tenant_id != tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Validate file type
    allowed_types = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
    ]
    if logo.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: JPEG, PNG, GIF, WebP",
        )

    # Validate file size (max 2MB for logo)
    content = await logo.read()
    if len(content) > 2 * 1024 * 1024:  # 2MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size: 2MB",
        )

    # Create uploads directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR) / "logos"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_ext = logo.filename.split(".")[-1] if "." in logo.filename else "png"
    filename = f"{tenant.slug}_{uuid.uuid4().hex[:8]}.{file_ext}"
    file_path = upload_dir / filename

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    # Delete old logo if exists
    if tenant.logo_url:
        old_path = Path(settings.UPLOAD_DIR) / tenant.logo_url.lstrip("/")
        if old_path.exists():
            old_path.unlink()

    # Update tenant logo URL
    tenant.logo_url = f"/uploads/logos/{filename}"
    db.commit()

    return {
        "message": "Logo uploaded successfully",
        "logo_url": tenant.logo_url,
    }


@router.delete("/{tenant_id}/logo")
def delete_tenant_logo(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin),
    user_tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Delete tenant logo image.

    Purpose: Remove the logo image associated with a tenant.

    Args:
        tenant_id (int): ID of tenant

    Returns:
        Dict with message: Logo deleted successfully

    Requires: Tenant Admin in this tenant

    Raises:
        404 Not Found: Tenant not found
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Check access
    if (
        current_user.role != UserRole.PLATFORM_ADMIN
        and user_tenant_id != tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Delete file if exists
    if tenant.logo_url:
        file_path = Path(settings.UPLOAD_DIR) / tenant.logo_url.lstrip("/")
        if file_path.exists():
            file_path.unlink()

        tenant.logo_url = None
        db.commit()

    return {"message": "Logo deleted successfully"}


@router.get("/stats/platform", response_model=dict)
def get_platform_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
):
    """
    Get platform-wide statistics and analytics.

    Returns aggregate metrics about the entire platform including tenant counts,
    user totals, branding adoption, and recent login activity. Designed for
    the platform admin dashboard.

    Route: GET /tenants/stats/platform

    Returns:
        Dict containing:
            - active_tenants (int): Count of tenants with is_active=true.
            - inactive_tenants (int): Count of tenants with is_active=false.
            - total_users (int): Total user count across all tenants.
            - logos_uploaded (int): Number of tenants with custom logos.
            - recent_logins (int): Users who logged in within the last 24 hours.

    Errors:
        403 Forbidden: Caller is not a platform admin.
        401 Unauthorized: Missing or invalid authentication token.
    """
    from datetime import datetime, timedelta

    # Active and inactive tenants
    active_tenants = db.query(Tenant).filter(Tenant.is_active == True).count()
    inactive_tenants = (
        db.query(Tenant).filter(Tenant.is_active == False).count()
    )

    # Total users
    total_users = db.query(User).count()

    # Tenants with logos uploaded
    tenants_with_logos = (
        db.query(Tenant).filter(Tenant.logo_url.isnot(None)).count()
    )

    # Users logged in within last 24 hours
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    recent_logins = (
        db.query(User).filter(User.last_login >= twenty_four_hours_ago).count()
    )

    return {
        "active_tenants": active_tenants,
        "inactive_tenants": inactive_tenants,
        "total_users": total_users,
        "logos_uploaded": tenants_with_logos,
        "recent_logins": recent_logins,
    }


@router.delete("/{tenant_id}")
def deactivate_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin),
):
    """
    Deactivate a tenant.

    Purpose: Disable a tenant and prevent its users from accessing the platform.
    Data is retained but not accessible. Use for suspending or retiring tenants.

    Args:
        tenant_id (int): ID of tenant to deactivate

    Returns:
        Dict with message: Tenant deactivated successfully

    Requires: Platform Admin authentication

    Raises:
        404 Not Found: Tenant not found
    """

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    tenant.is_active = False
    db.commit()

    return {"message": "Tenant deactivated successfully"}
