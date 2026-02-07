"""User router"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    User as UserSchema,
    UserInvite,
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
    """Update user details"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check permissions
    if current_user.role != UserRole.PLATFORM_ADMIN:
        if user.tenant_id != tenant_id or user.id == current_user.id:
            if current_user.role not in [
                UserRole.TENANT_ADMIN,
                UserRole.ADMINISTRATOR,
            ]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

    # Update fields
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Deactivate a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check access
    if (
        current_user.role != UserRole.PLATFORM_ADMIN
        and user.tenant_id != tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.is_active = False
    db.commit()

    return {"message": "User deactivated successfully"}


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
