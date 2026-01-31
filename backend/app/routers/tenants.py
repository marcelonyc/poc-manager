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
from app.schemas.tenant import TenantCreate, TenantUpdate, Tenant as TenantSchema, TenantEmailConfig
from app.auth import require_platform_admin, require_tenant_admin, get_current_user, get_password_hash
from app.config import settings

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post("/", response_model=TenantSchema, status_code=status.HTTP_201_CREATED)
def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin)
):
    """Create a new tenant (Platform Admin only)"""
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
    db.commit()
    db.refresh(tenant)
    
    return tenant


@router.get("/", response_model=List[TenantSchema])
def list_tenants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin)
):
    """List all tenants (Platform Admin only)"""
    tenants = db.query(Tenant).offset(skip).limit(limit).all()
    # Add computed property for each tenant
    result = []
    for tenant in tenants:
        tenant_dict = {
            **tenant.__dict__,
            "has_custom_mail_config": bool(tenant.custom_mail_server and tenant.custom_mail_username)
        }
        result.append(tenant_dict)
    return result


@router.get("/{tenant_id}", response_model=TenantSchema)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tenant details"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    # Check access
    if current_user.role != UserRole.PLATFORM_ADMIN and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    # Add computed property for email config status
    tenant_dict = {
        **tenant.__dict__,
        "has_custom_mail_config": bool(tenant.custom_mail_server and tenant.custom_mail_username)
    }
    
    return tenant_dict


@router.put("/{tenant_id}", response_model=TenantSchema)
def update_tenant(
    tenant_id: int,
    tenant_data: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin)
):
    """Update tenant details"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    # Check access
    if current_user.role != UserRole.PLATFORM_ADMIN and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    # Only Platform Admins can change is_active
    update_data = tenant_data.dict(exclude_unset=True)
    if 'is_active' in update_data and current_user.role != UserRole.PLATFORM_ADMIN:
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
    current_user: User = Depends(require_tenant_admin)
):
    """Update tenant email configuration"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    # Check access
    if current_user.role != UserRole.PLATFORM_ADMIN and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    # Update email config
    config_data = email_config.dict(exclude_unset=True)
    for field, value in config_data.items():
        setattr(tenant, field, value)
    
    db.commit()
    return {"message": "Email configuration updated successfully"}


@router.post("/{tenant_id}/logo")
async def upload_tenant_logo(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin),
    logo: UploadFile = File(...)
):
    """Upload tenant logo (Tenant Admin only)"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    # Check access
    if current_user.role != UserRole.PLATFORM_ADMIN and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
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
    file_ext = logo.filename.split('.')[-1] if '.' in logo.filename else 'png'
    filename = f"{tenant.slug}_{uuid.uuid4().hex[:8]}.{file_ext}"
    file_path = upload_dir / filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Delete old logo if exists
    if tenant.logo_url:
        old_path = Path(settings.UPLOAD_DIR) / tenant.logo_url.lstrip('/')
        if old_path.exists():
            old_path.unlink()
    
    # Update tenant logo URL
    tenant.logo_url = f"/uploads/logos/{filename}"
    db.commit()
    
    return {
        "message": "Logo uploaded successfully",
        "logo_url": tenant.logo_url
    }


@router.delete("/{tenant_id}/logo")
def delete_tenant_logo(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin)
):
    """Delete tenant logo (Tenant Admin only)"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    # Check access
    if current_user.role != UserRole.PLATFORM_ADMIN and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    # Delete file if exists
    if tenant.logo_url:
        file_path = Path(settings.UPLOAD_DIR) / tenant.logo_url.lstrip('/')
        if file_path.exists():
            file_path.unlink()
        
        tenant.logo_url = None
        db.commit()
    
    return {"message": "Logo deleted successfully"}


@router.get("/stats/platform", response_model=dict)
def get_platform_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin)
):
    """Get platform-wide statistics (Platform Admin only)"""
    from datetime import datetime, timedelta
    
    # Active and inactive tenants
    active_tenants = db.query(Tenant).filter(Tenant.is_active == True).count()
    inactive_tenants = db.query(Tenant).filter(Tenant.is_active == False).count()
    
    # Total users
    total_users = db.query(User).count()
    
    # Tenants with logos uploaded
    tenants_with_logos = db.query(Tenant).filter(Tenant.logo_url.isnot(None)).count()
    
    # Users logged in within last 24 hours
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    recent_logins = db.query(User).filter(
        User.last_login >= twenty_four_hours_ago
    ).count()
    
    return {
        "active_tenants": active_tenants,
        "inactive_tenants": inactive_tenants,
        "total_users": total_users,
        "logos_uploaded": tenants_with_logos,
        "recent_logins": recent_logins
    }


@router.delete("/{tenant_id}")
def deactivate_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_admin)
):
    """Deactivate a tenant (Platform Admin only)"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    tenant.is_active = False
    db.commit()
    
    return {"message": "Tenant deactivated successfully"}
