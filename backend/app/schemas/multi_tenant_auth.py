"""Multi-tenant authentication schemas"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class TenantOption(BaseModel):
    """Tenant selection option"""
    tenant_id: Optional[int]
    tenant_name: Optional[str]
    tenant_slug: Optional[str]
    role: str
    is_default: bool
    
    class Config:
        from_attributes = True


class TenantSelectionResponse(BaseModel):
    """Response after initial login showing available tenants"""
    user_id: int
    email: str
    full_name: str
    tenants: List[TenantOption]
    requires_selection: bool  # True if user has multiple tenants
    access_token: Optional[str] = None  # Provided directly for platform admins
    token_type: Optional[str] = None  # "bearer" for platform admins
    
    class Config:
        from_attributes = True


class SelectTenantRequest(BaseModel):
    """Request to select a specific tenant for the session"""
    tenant_id: Optional[int]  # None for platform admin global access
    email: str  # Re-authentication required
    password: str  # Re-authentication required


class TenantSwitchRequest(BaseModel):
    """Request to switch to a different tenant during session"""
    tenant_id: Optional[int]


class TokenWithTenant(BaseModel):
    """JWT token response with tenant context"""
    access_token: str
    token_type: str
    tenant_id: Optional[int]
    tenant_name: Optional[str]
    tenant_slug: Optional[str]
    role: str
    user_id: int
    email: str
    full_name: str


class TenantInvitationCreate(BaseModel):
    """Create invitation for existing user to join tenant"""
    email: EmailStr
    role: str  # Role they'll have in this tenant
    

class TenantInvitationResponse(BaseModel):
    """Tenant invitation response"""
    id: int
    email: str
    tenant_id: int
    tenant_name: str
    role: str
    token: str
    status: str
    invited_by_email: str
    created_at: datetime
    expires_at: datetime
    accepted_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TenantInvitationAccept(BaseModel):
    """Accept tenant invitation (existing user)"""
    token: str
