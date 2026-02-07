"""User router"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User, UserRole
from app.models.user_tenant_role import UserTenantRole
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    User as UserSchema,
    UserInvite,
)
from app.schemas.user_tenant_role import (
    UserTenantRole as UserTenantRoleSchema,
    UserTenantRoleUpdate,
)
from app.auth import (
    require_platform_admin,
    require_tenant_admin,
    require_administrator,
    get_current_user,
    get_current_tenant_id,
    get_password_hash,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    session_tenant_id: int = Depends(get_current_tenant_id),
):
    """Create a new user"""
    # Check permissions based on role being created
    if user_data.role == UserRole.PLATFORM_ADMIN:
        if current_user.role != UserRole.PLATFORM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can create platform admins",
            )
    elif user_data.role == UserRole.TENANT_ADMIN:
        if current_user.role not in [UserRole.PLATFORM_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
    elif user_data.role in [UserRole.ADMINISTRATOR, UserRole.SALES_ENGINEER]:
        if current_user.role not in [
            UserRole.PLATFORM_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.ADMINISTRATOR,
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

    # Check if user exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Inherit tenant from JWT session tenant if not specified
    tenant_id = user_data.tenant_id
    if tenant_id is None and current_user.role != UserRole.PLATFORM_ADMIN:
        tenant_id = session_tenant_id

    # Create user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        tenant_id=user_tenant_id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.get("/", response_model=List[UserSchema])
def list_users(
    skip: int = 0,
    limit: int = 100,
    tenant_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List users"""
    query = db.query(User)

    # Filter by tenant for non-platform admins
    if current_user.role == UserRole.PLATFORM_ADMIN:
        if tenant_id:
            query = query.filter(User.tenant_id == tenant_id)
    else:
        user_tenant_id = get_current_tenant_id(current_user)
        query = query.filter(User.tenant_id == user_tenant_id)

    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserSchema)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Get user details"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check access
    if current_user.role != UserRole.PLATFORM_ADMIN:
        if user.tenant_id != tenant_id and user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,  # Don't leak existence
                detail="User not found",
            )

    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Update user details (email, full_name only - not is_active)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # CRITICAL: Check tenant context first
    # Tenant-scoped users cannot modify users table directly
    if tenant_id is not None:
        # User is in tenant context - query their role in this specific tenant
        current_user_tenant_role = (
            db.query(UserTenantRole)
            .filter(
                UserTenantRole.user_id == current_user.id,
                UserTenantRole.tenant_id == tenant_id,
            )
            .first()
        )

        if not current_user_tenant_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this tenant",
            )

        current_role = current_user_tenant_role.role

        # Tenant admins can only update users in their tenant
        # But they CANNOT modify the users table - only user_tenant_roles
        if current_role not in [UserRole.TENANT_ADMIN, UserRole.ADMINISTRATOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        # Check if target user belongs to this tenant
        target_user_tenant_role = (
            db.query(UserTenantRole)
            .filter(
                UserTenantRole.user_id == user_id,
                UserTenantRole.tenant_id == tenant_id,
            )
            .first()
        )

        if not target_user_tenant_role and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in this tenant",
            )
    else:
        # No tenant context - must be platform admin
        if (
            current_user.role != UserRole.PLATFORM_ADMIN
            and current_user.id != user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Platform admin privileges required",
            )

    # Update fields (is_active is not in UserUpdate schema, so it cannot be modified here)
    update_data = user_data.dict(exclude_unset=True)

    # Double-check: Ensure is_active cannot be modified via this endpoint
    if "is_active" in update_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Use DELETE /users/{id} or POST /users/{id}/reactivate to modify activation status",
        )

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Deactivate a user in the current tenant (Tenant Admin) or platform-wide (Platform Admin only)"""

    # CRITICAL: Determine if user is a platform admin
    # Platform admins should NEVER have tenant context
    # If tenant_id exists, user is NOT a platform admin (even if they have the role in users table)

    if tenant_id is not None:
        # User is in a tenant context - query their role in this specific tenant
        current_user_tenant_role = (
            db.query(UserTenantRole)
            .filter(
                UserTenantRole.user_id == current_user.id,
                UserTenantRole.tenant_id == tenant_id,
            )
            .first()
        )

        if not current_user_tenant_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this tenant",
            )

        current_role = current_user_tenant_role.role

        # Tenant-scoped users can NEVER modify platform-level is_active
        # They can only modify tenant-level is_active
        if current_role not in [UserRole.TENANT_ADMIN, UserRole.ADMINISTRATOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to deactivate users",
            )

        # Deactivate user in THIS tenant only
        user_tenant_role = (
            db.query(UserTenantRole)
            .filter(
                UserTenantRole.user_id == user_id,
                UserTenantRole.tenant_id == tenant_id,
            )
            .first()
        )

        if not user_tenant_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in this tenant",
            )

        user_tenant_role.is_active = False
        db.commit()
        return {"message": "User deactivated in tenant successfully"}

    else:
        # No tenant context - check if user is actually a platform admin
        # This should only happen for true platform admins
        if current_user.role != UserRole.PLATFORM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Platform admin privileges required",
            )

        # Platform admin can deactivate at platform level
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.is_active = False
        db.commit()
        return {"message": "User deactivated at platform level"}


@router.post("/invite", status_code=status.HTTP_201_CREATED)
def invite_user(
    invite_data: UserInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Invite a new user (sends email with temporary password)"""
    # Check permissions
    if invite_data.role in [UserRole.PLATFORM_ADMIN]:
        if current_user.role != UserRole.PLATFORM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

    # Check if user exists
    existing = db.query(User).filter(User.email == invite_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Generate temporary password (in real app, use secure random)
    temp_password = "ChangeMe123!"

    # Create user
    user = User(
        email=invite_data.email,
        full_name=invite_data.full_name,
        hashed_password=get_password_hash(temp_password),
        role=invite_data.role,
        tenant_id=tenant_id,
        is_active=True,
    )
    db.add(user)
    db.commit()

    # TODO: Send invitation email with temp password

    return {
        "message": "User invited successfully",
        "user_id": user.id,
        "temporary_password": temp_password,  # Remove in production
    }


@router.post("/{user_id}/reactivate")
def reactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Reactivate a user in the current tenant (Tenant Admin) or platform-wide (Platform Admin only)"""

    # CRITICAL: Determine if user is a platform admin
    # Platform admins should NEVER have tenant context
    # If tenant_id exists, user is NOT a platform admin (even if they have the role in users table)

    if tenant_id is not None:
        # User is in a tenant context - query their role in this specific tenant
        current_user_tenant_role = (
            db.query(UserTenantRole)
            .filter(
                UserTenantRole.user_id == current_user.id,
                UserTenantRole.tenant_id == tenant_id,
            )
            .first()
        )

        if not current_user_tenant_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this tenant",
            )

        current_role = current_user_tenant_role.role

        # Tenant-scoped users can NEVER modify platform-level is_active
        # They can only modify tenant-level is_active
        if current_role not in [UserRole.TENANT_ADMIN, UserRole.ADMINISTRATOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to reactivate users",
            )

        # Reactivate user in THIS tenant only
        user_tenant_role = (
            db.query(UserTenantRole)
            .filter(
                UserTenantRole.user_id == user_id,
                UserTenantRole.tenant_id == tenant_id,
            )
            .first()
        )

        if not user_tenant_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in this tenant",
            )

        user_tenant_role.is_active = True
        db.commit()
        return {"message": "User reactivated in tenant successfully"}

    else:
        # No tenant context - check if user is actually a platform admin
        # This should only happen for true platform admins
        if current_user.role != UserRole.PLATFORM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Platform admin privileges required",
            )

        # Platform admin can reactivate at platform level
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.is_active = True
        db.commit()
        return {"message": "User reactivated at platform level"}


@router.get(
    "/{user_id}/tenant-roles", response_model=List[UserTenantRoleSchema]
)
def get_user_tenant_roles(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all tenant roles for a user (Platform Admin only)"""
    # Get the current user's actual role from the database
    # For platform admins, tenant_id will be None
    current_tenant_id = get_current_tenant_id(current_user)

    if current_tenant_id is None:
        # No tenant context - use the role from users table (platform admin)
        current_role = current_user.role
    else:
        # Query the database for the user's role in this specific tenant
        current_user_tenant_role = (
            db.query(UserTenantRole)
            .filter(
                UserTenantRole.user_id == current_user.id,
                UserTenantRole.tenant_id == current_tenant_id,
            )
            .first()
        )

        if not current_user_tenant_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this tenant",
            )

        current_role = current_user_tenant_role.role

    if current_role != UserRole.PLATFORM_ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    tenant_roles = (
        db.query(UserTenantRole)
        .filter(UserTenantRole.user_id == user_id)
        .all()
    )

    return tenant_roles


@router.put(
    "/{user_id}/tenant-roles/{tenant_id}", response_model=UserTenantRoleSchema
)
def update_user_tenant_role(
    user_id: int,
    tenant_id: int,
    update_data: UserTenantRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    session_tenant_id: int = Depends(get_current_tenant_id),
):
    """Update user's tenant role (is_active, role, or is_default)"""
    # Find the user-tenant-role association
    user_tenant_role = (
        db.query(UserTenantRole)
        .filter(
            UserTenantRole.user_id == user_id,
            UserTenantRole.tenant_id == tenant_id,
        )
        .first()
    )

    if not user_tenant_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User-tenant association not found",
        )

    # Get the current user's actual role in this tenant from the database
    # Do NOT use current_user.role as it's deprecated and could be wrong
    if session_tenant_id is None:
        # No tenant context - must be a platform admin
        current_role = current_user.role
    else:
        # Query the database for the user's role in this specific tenant
        current_user_tenant_role = (
            db.query(UserTenantRole)
            .filter(
                UserTenantRole.user_id == current_user.id,
                UserTenantRole.tenant_id == session_tenant_id,
            )
            .first()
        )

        if not current_user_tenant_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this tenant",
            )

        current_role = current_user_tenant_role.role

    # Check permissions
    if current_role == UserRole.PLATFORM_ADMIN:
        # Platform admins can update any field
        pass
    elif current_role in [UserRole.TENANT_ADMIN, UserRole.ADMINISTRATOR]:
        # Tenant admins can only update users in their own tenant
        if tenant_id != session_tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify users in other tenants",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    # Update fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(user_tenant_role, field, value)

    db.commit()
    db.refresh(user_tenant_role)

    return user_tenant_role
