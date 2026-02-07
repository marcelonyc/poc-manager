"""User Tenant Role schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserTenantRoleBase(BaseModel):
    """Base user-tenant-role schema"""

    user_id: int
    tenant_id: Optional[int]
    role: UserRole
    is_default: bool = False
    is_active: bool = True


class UserTenantRoleCreate(UserTenantRoleBase):
    """Schema for creating user-tenant-role association"""

    pass


class UserTenantRoleUpdate(BaseModel):
    """Schema for updating user-tenant-role association"""

    role: Optional[UserRole] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class UserTenantRole(UserTenantRoleBase):
    """Schema for user-tenant-role response"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
