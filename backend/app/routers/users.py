"""User router"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User, UserRole
from app.models.user_tenant_role import UserTenantRole
from app.models.tenant import Tenant
from datetime import datetime, timedelta, timezone
import secrets
from app.models.invitation import Invitation, InvitationStatus
from app.services.email import (
    send_tenant_invitation_email,
    send_user_invitation_email,
)
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
    elif user_data.role in [
        UserRole.ADMINISTRATOR,
        UserRole.SALES_ENGINEER,
        UserRole.ACCOUNT_EXECUTIVE,
    ]:
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
        tenant_id=tenant_id,
        is_active=True,
    )
    db.add(user)
    db.flush()

    # Create user_tenant_role entry so user can log in
    if tenant_id is not None:
        user_tenant_role = UserTenantRole(
            user_id=user.id,
            tenant_id=tenant_id,
            role=user_data.role,
            is_default=True,
        )
        db.add(user_tenant_role)

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
    session_tenant_id: int = Depends(get_current_tenant_id),
):
    """
    List users with tenant-specific activation status.

    Returns a paginated list of users. When called within a tenant context,
    the is_active field reflects the user's status in that specific tenant
    (from user_tenant_roles), not the platform-level status. Platform admins
    without tenant context see the global users table is_active value.

    Route: GET /users/?skip=0&limit=100&tenant_id=

    Query parameters:
        skip (int, default 0): Number of records to skip for pagination.
        limit (int, default 100): Maximum number of records to return.
        tenant_id (int, optional): Filter by tenant ID (platform admin only, no tenant context).

    Returns:
        List of user objects, each containing:
            - id (int): Unique user identifier.
            - email (str): User email address.
            - full_name (str): User display name.
            - role (str): User role — one of "platform_admin", "tenant_admin", "administrator", "sales_engineer", "customer".
            - is_active (bool): Activation status (tenant-specific when in tenant context).
            - tenant_id (int | null): Primary tenant association.
            - created_at (datetime): Account creation timestamp.
            - last_login (datetime | null): Last login timestamp.

    Errors:
        401 Unauthorized: Missing or invalid authentication token.
    """

    # For tenant-scoped requests, we need to join with user_tenant_roles
    # to get the tenant-specific is_active status
    if session_tenant_id is not None:
        # Query users joined with their tenant roles
        results = (
            db.query(User, UserTenantRole)
            .join(
                UserTenantRole,
                (UserTenantRole.user_id == User.id)
                & (UserTenantRole.tenant_id == session_tenant_id),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        # Build response with tenant-specific is_active
        users_with_tenant_status = []
        for user, tenant_role in results:
            user_dict = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": tenant_role.is_active,  # Use tenant-specific is_active
                "tenant_id": user.tenant_id,
                "created_at": user.created_at,
                "last_login": user.last_login,
            }
            users_with_tenant_status.append(user_dict)

        return users_with_tenant_status
    else:
        # Platform admin without tenant context - return users table is_active
        query = db.query(User)
        if tenant_id:
            query = query.filter(User.tenant_id == tenant_id)

        users = query.offset(skip).limit(limit).all()
        return users


@router.get("/{user_id}", response_model=UserSchema)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Get user details by ID.

    Retrieve a single user's profile. Non-platform-admin callers can only
    access users within their own tenant or their own profile. Returns 404
    instead of 403 to avoid leaking user existence across tenants.

    Route: GET /users/{user_id}

    Path parameters:
        user_id (int): The unique identifier of the user to retrieve.

    Returns:
        User object containing:
            - id (int): Unique user identifier.
            - email (str): User email address.
            - full_name (str): User display name.
            - role (str): User role.
            - is_active (bool): Whether the user account is active.
            - tenant_id (int | null): Primary tenant association.
            - created_at (datetime): Account creation timestamp.
            - last_login (datetime | null): Last login timestamp.

    Errors:
        404 Not Found: User does not exist or caller lacks access.
        401 Unauthorized: Missing or invalid authentication token.
    """
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
    update_data = user_data.model_dump(exclude_unset=True)

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
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Invite a user to a tenant. If the user already exists but is not
    associated with this tenant, add them to user_tenant_roles and send
    an email notification without changing their password."""
    # Check permissions
    if invite_data.role in [UserRole.PLATFORM_ADMIN]:
        if current_user.role != UserRole.PLATFORM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

    # Resolve tenant name for email notifications
    tenant = None
    if tenant_id is not None:
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    # Check if user already exists
    existing = db.query(User).filter(User.email == invite_data.email).first()
    if existing:
        # User exists — check if already associated with this tenant
        if tenant_id is not None:
            existing_role = (
                db.query(UserTenantRole)
                .filter(
                    UserTenantRole.user_id == existing.id,
                    UserTenantRole.tenant_id == tenant_id,
                )
                .first()
            )
            if existing_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is already a member of this tenant",
                )

            # Add existing user to the tenant (do NOT change password)
            user_tenant_role = UserTenantRole(
                user_id=existing.id,
                tenant_id=tenant_id,
                role=invite_data.role,
                is_default=False,
            )
            db.add(user_tenant_role)
            db.commit()

            # Send email notification about the new tenant association
            tenant_name = tenant.name if tenant else "Unknown"
            background_tasks.add_task(
                send_tenant_invitation_email,
                recipient=existing.email,
                tenant_name=tenant_name,
                role=invite_data.role.value,
                token="",  # No token needed — user already has an account
                invited_by=current_user.full_name or current_user.email,
            )

            return {
                "message": "Existing user added to tenant successfully",
                "user_id": existing.id,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

    # New user — create an invitation (user sets their own password)
    # Check for existing pending invitation
    existing_invitation = (
        db.query(Invitation)
        .filter(
            Invitation.email == invite_data.email,
            Invitation.status == InvitationStatus.PENDING,
        )
        .first()
    )
    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending invitation already exists for this email",
        )

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    invitation = Invitation(
        email=invite_data.email,
        full_name=invite_data.full_name,
        token=token,
        status=InvitationStatus.PENDING,
        invited_by_email=current_user.email,
        role=invite_data.role.value,
        tenant_id=tenant_id,
        expires_at=expires_at,
    )
    db.add(invitation)
    db.commit()

    # Send invitation email with acceptance link
    tenant_name = tenant.name if tenant else None
    background_tasks.add_task(
        send_user_invitation_email,
        email=invite_data.email,
        full_name=invite_data.full_name,
        role=invite_data.role.value,
        token=token,
        tenant=tenant,
    )

    return {
        "message": "Invitation sent successfully. The user will receive an email to set their password.",
        "invitation_id": invitation.id,
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
    """
    List all tenant role associations for a user.

    Returns every tenant the user belongs to along with their role and
    activation status in each tenant. Platform admins can view any user's
    tenant roles; other users can only view their own.

    Route: GET /users/{user_id}/tenant-roles

    Path parameters:
        user_id (int): The unique identifier of the user whose tenant roles to retrieve.

    Returns:
        List of user-tenant-role objects, each containing:
            - id (int): Unique association identifier.
            - user_id (int): The user's identifier.
            - tenant_id (int): The tenant identifier.
            - role (str): Role in this tenant — one of "tenant_admin", "administrator", "sales_engineer", "customer".
            - is_active (bool): Whether the user is active in this tenant.
            - is_default (bool): Whether this is the user's default tenant.

    Errors:
        403 Forbidden: Caller is not a platform admin and user_id does not match their own.
        401 Unauthorized: Missing or invalid authentication token.
    """
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
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(user_tenant_role, field, value)

    db.commit()
    db.refresh(user_tenant_role)

    return user_tenant_role
