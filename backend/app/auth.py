"""Authentication utilities"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.user import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, tenant_id: Optional[int] = None) -> str:
    """Create a JWT access token with optional tenant context"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Add tenant context if provided
    if tenant_id is not None:
        to_encode.update({"tenant_id": tenant_id})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user with tenant context"""
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been blocked. Please contact support.",
        )
    
    # Store tenant context from token in user object for easy access
    tenant_id = payload.get("tenant_id")
    if tenant_id is not None:
        # Set a dynamic attribute for current tenant context
        setattr(user, '_current_tenant_id', tenant_id)
        # Get the role for this tenant
        role = user.get_role_for_tenant(tenant_id)
        if role:
            setattr(user, '_current_role', role)
    
    return user


def get_current_tenant_id(current_user: User = Depends(get_current_user)) -> Optional[int]:
    """Extract current tenant ID from user context"""
    return getattr(current_user, '_current_tenant_id', None)


def get_current_role(current_user: User = Depends(get_current_user)) -> Optional[UserRole]:
    """Extract current role from user context"""
    return getattr(current_user, '_current_role', None)


def require_role(*roles: UserRole):
    """Dependency to require specific user roles in current tenant context"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        current_role = getattr(current_user, '_current_role', None)
        if current_role is None:
            # Fall back to checking any tenant role
            if not any(current_user.has_role(role) for role in roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {[r.value for r in roles]}",
                )
        elif current_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in roles]}",
            )
        return current_user
    return role_checker


# Convenience dependencies for common role checks
def require_platform_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require platform admin role"""
    current_role = getattr(current_user, '_current_role', None)
    if current_role != UserRole.PLATFORM_ADMIN and not current_user.has_role(UserRole.PLATFORM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform admin access required",
        )
    return current_user


def require_tenant_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require tenant admin role or higher"""
    current_role = getattr(current_user, '_current_role', None)
    allowed_roles = [UserRole.PLATFORM_ADMIN, UserRole.TENANT_ADMIN]
    
    if current_role is None:
        # Check if user has any of these roles in any tenant
        if not any(current_user.has_role(role) for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant admin access required",
            )
    elif current_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant admin access required",
        )
    return current_user


def require_administrator(current_user: User = Depends(get_current_user)) -> User:
    """Require administrator role or higher"""
    current_role = getattr(current_user, '_current_role', None)
    allowed_roles = [UserRole.PLATFORM_ADMIN, UserRole.TENANT_ADMIN, UserRole.ADMINISTRATOR]
    
    if current_role is None:
        if not any(current_user.has_role(role) for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrator access required",
            )
    elif current_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )
    return current_user


def require_sales_engineer(current_user: User = Depends(get_current_user)) -> User:
    """Require sales engineer role or higher"""
    current_role = getattr(current_user, '_current_role', None)
    allowed_roles = [
        UserRole.PLATFORM_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.ADMINISTRATOR,
        UserRole.SALES_ENGINEER
    ]
    
    if current_role is None:
        if not any(current_user.has_role(role) for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sales engineer access required",
            )
    elif current_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sales engineer access required",
        )
    return current_user


def check_tenant_access(user: User, tenant_id: int) -> bool:
    """Check if user has access to a specific tenant"""
    # Platform admin has access to all tenants
    if user.has_role(UserRole.PLATFORM_ADMIN):
        return True
    
    # Check if user has any role in the specified tenant
    return user.get_role_for_tenant(tenant_id) is not None
