"""Demo request schemas"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class DemoRequestCreate(BaseModel):
    """Schema for creating a demo request"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    company_name: str = Field(..., min_length=1, max_length=200)
    sales_engineers_count: int = Field(..., ge=1, le=1000)
    pocs_per_quarter: int = Field(..., ge=1, le=1000)


class DemoRequestResponse(BaseModel):
    """Schema for demo request response"""
    id: int
    name: str
    email: str
    company_name: str
    sales_engineers_count: int
    pocs_per_quarter: int
    is_verified: bool
    is_completed: bool
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: datetime
    verified_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class VerifyEmailRequest(BaseModel):
    """Schema for verifying email with token"""
    token: str


class SetPasswordRequest(BaseModel):
    """Schema for setting password after email verification"""
    token: str
    password: str = Field(..., min_length=8)


class DemoConversionRequestCreate(BaseModel):
    """Schema for requesting demo to real conversion"""
    reason: Optional[str] = Field(None, max_length=1000)


class DemoConversionRequestResponse(BaseModel):
    """Schema for demo conversion request response"""
    id: int
    tenant_id: int
    requested_by_user_id: int
    reason: Optional[str] = None
    status: str
    approved: bool
    approved_by_user_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ApproveConversionRequest(BaseModel):
    """Schema for approving/rejecting conversion"""
    approved: bool
    rejection_reason: Optional[str] = Field(None, max_length=1000)


class DemoUserResponse(BaseModel):
    """Schema for demo request in list"""
    id: int
    name: str
    email: str
    company_name: str
    sales_engineers_count: int
    pocs_per_quarter: int
    is_verified: bool
    is_completed: bool
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    tenant_name: Optional[str] = None
    created_at: datetime
    verified_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class DemoUserList(BaseModel):
    """Schema for paginated demo request list"""
    total: int
    users: list[DemoUserResponse]  # Keep name as 'users' for frontend compatibility


class BlockUserRequest(BaseModel):
    """Schema for blocking/unblocking a user"""
    is_blocked: bool
    reason: Optional[str] = None


class UpgradeAccountRequest(BaseModel):
    """Schema for upgrading demo to real account"""
    pass  # No additional fields needed


class ResendEmailRequest(BaseModel):
    """Schema for resending verification email"""
    pass  # No additional fields needed

