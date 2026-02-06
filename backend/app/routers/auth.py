"""Authentication router"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.user_tenant_role import UserTenantRole
from app.schemas.user import LoginRequest, Token, PasswordChange
from app.schemas.multi_tenant_auth import (
    TenantSelectionResponse, 
    TenantOption, 
    SelectTenantRequest,
    TokenWithTenant,
    TenantSwitchRequest
)
from app.auth import verify_password, create_access_token, get_current_user, get_password_hash
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TenantSelectionResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return tenant selection options.
    If user has multiple tenants, they need to select one before getting a token.
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been blocked. Please contact support.",
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Platform admins don't belong to any tenant - handle them specially
    if user.role.value == "platform_admin":
        # Create access token without tenant context
        access_token = create_access_token(data={"sub": user.email})
        return TenantSelectionResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            tenants=[],
            requires_selection=False,
            access_token=access_token,
            token_type="bearer"
        )
    
    # Get all tenant associations for this user
    tenant_roles = db.query(UserTenantRole).filter(
        UserTenantRole.user_id == user.id
    ).all()
    
    if not tenant_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any tenant",
        )
    
    # Build tenant options
    tenant_options = []
    for tr in tenant_roles:
        tenant_name = None
        tenant_slug = None
        if tr.tenant:
            tenant_name = tr.tenant.name
            tenant_slug = tr.tenant.slug
            # Check if tenant is active
            if not tr.tenant.is_active:
                continue
        
        tenant_options.append(TenantOption(
            tenant_id=tr.tenant_id,
            tenant_name=tenant_name,
            tenant_slug=tenant_slug,
            role=tr.role.value,
            is_default=tr.is_default
        ))
    
    if not tenant_options:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active tenants available for this user",
        )
    
    return TenantSelectionResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        tenants=tenant_options,
        requires_selection=len(tenant_options) > 1
    )


@router.post("/select-tenant", response_model=TokenWithTenant)
def select_tenant(
    request: SelectTenantRequest,
    db: Session = Depends(get_db)
):
    """
    After login, select a tenant and receive an access token with tenant context.
    Requires re-authentication for security.
    """
    # Re-authenticate user
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Find the tenant role association
    tenant_role = db.query(UserTenantRole).filter(
        UserTenantRole.user_id == user.id,
        UserTenantRole.tenant_id == request.tenant_id
    ).first()
    
    if not tenant_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this tenant",
        )
    
    # Verify tenant is active
    if tenant_role.tenant_id and tenant_role.tenant and not tenant_role.tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This tenant is inactive",
        )
    
    # Create access token with tenant context
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "role": tenant_role.role.value
        },
        expires_delta=access_token_expires,
        tenant_id=request.tenant_id
    )
    
    tenant_name = tenant_role.tenant.name if tenant_role.tenant else None
    tenant_slug = tenant_role.tenant.slug if tenant_role.tenant else None
    
    return TokenWithTenant(
        access_token=access_token,
        token_type="bearer",
        tenant_id=request.tenant_id,
        tenant_name=tenant_name,
        tenant_slug=tenant_slug,
        role=tenant_role.role.value,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name
    )


@router.post("/switch-tenant", response_model=TokenWithTenant)
def switch_tenant(
    switch_request: TenantSwitchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Switch to a different tenant during an active session.
    Returns a new token with the new tenant context.
    """
    # Find the tenant role association
    tenant_role = db.query(UserTenantRole).filter(
        UserTenantRole.user_id == current_user.id,
        UserTenantRole.tenant_id == switch_request.tenant_id
    ).first()
    
    if not tenant_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this tenant",
        )
    
    # Verify tenant is active
    if tenant_role.tenant_id and tenant_role.tenant and not tenant_role.tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This tenant is inactive",
        )
    
    # Create new access token with new tenant context
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(current_user.id), 
            "email": current_user.email, 
            "role": tenant_role.role.value
        },
        expires_delta=access_token_expires,
        tenant_id=switch_request.tenant_id
    )
    
    tenant_name = tenant_role.tenant.name if tenant_role.tenant else None
    tenant_slug = tenant_role.tenant.slug if tenant_role.tenant else None
    
    return TokenWithTenant(
        access_token=access_token,
        token_type="bearer",
        tenant_id=switch_request.tenant_id,
        tenant_name=tenant_name,
        tenant_slug=tenant_slug,
        role=tenant_role.role.value,
        user_id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name
    )


@router.get("/me")
def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information including all tenant associations"""
    # Get current tenant context from token
    current_tenant_id = getattr(current_user, '_current_tenant_id', None)
    current_role = getattr(current_user, '_current_role', None)
    
    # Get all tenant associations
    tenant_roles = db.query(UserTenantRole).filter(
        UserTenantRole.user_id == current_user.id
    ).all()
    
    tenants = []
    for tr in tenant_roles:
        tenant_info = {
            "tenant_id": tr.tenant_id,
            "role": tr.role.value,
            "is_default": tr.is_default,
        }
        if tr.tenant:
            tenant_info.update({
                "tenant_name": tr.tenant.name,
                "tenant_slug": tr.tenant.slug,
                "is_active": tr.tenant.is_active,
            })
        tenants.append(tenant_info)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "current_tenant_id": current_tenant_id,
        "current_role": current_role.value if current_role else None,
        "tenants": tenants,
    }


@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password",
        )
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/refresh", response_model=TokenWithTenant)
def refresh_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh access token, maintaining current tenant context"""
    current_tenant_id = getattr(current_user, '_current_tenant_id', None)
    current_role = getattr(current_user, '_current_role', None)
    
    # If no tenant context, get default
    if current_tenant_id is None:
        default_tenant_role = current_user.get_default_tenant_role()
        if default_tenant_role:
            current_tenant_id = default_tenant_role.tenant_id
            current_role = default_tenant_role.role
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(current_user.id), 
            "email": current_user.email, 
            "role": current_role.value if current_role else "customer"
        },
        expires_delta=access_token_expires,
        tenant_id=current_tenant_id
    )
    
    # Get tenant info
    tenant_name = None
    tenant_slug = None
    if current_tenant_id:
        tenant_role = db.query(UserTenantRole).filter(
            UserTenantRole.user_id == current_user.id,
            UserTenantRole.tenant_id == current_tenant_id
        ).first()
        if tenant_role and tenant_role.tenant:
            tenant_name = tenant_role.tenant.name
            tenant_slug = tenant_role.tenant.slug
    
    return TokenWithTenant(
        access_token=access_token,
        token_type="bearer",
        tenant_id=current_tenant_id,
        tenant_name=tenant_name,
        tenant_slug=tenant_slug,
        role=current_role.value if current_role else "customer",
        user_id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name
    )
