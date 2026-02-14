"""User schemas"""

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    full_name: str
    role: UserRole


class UserCreate(UserBase):
    """Schema for creating a user"""

    password: str
    tenant_id: Optional[int] = None


class UserUpdate(BaseModel):
    """Schema for updating a user"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    # is_active is NOT allowed here - use DELETE /users/{id} or POST /users/{id}/reactivate instead


class UserInvite(BaseModel):
    """Schema for inviting a user"""

    email: EmailStr
    full_name: str
    role: UserRole


class User(UserBase):
    """Schema for user response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    tenant_id: Optional[int]
    created_at: datetime
    last_login: Optional[datetime]


class Token(BaseModel):
    """Schema for authentication token"""

    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Schema for login request"""

    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    """Schema for password change"""

    old_password: str
    new_password: str
