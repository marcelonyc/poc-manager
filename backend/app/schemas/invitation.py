"""Invitation schemas"""

from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.invitation import InvitationStatus


class InvitationCreate(BaseModel):
    """Schema for creating an invitation"""

    email: EmailStr
    full_name: str


class InvitationResponse(BaseModel):
    """Schema for invitation response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    status: InvitationStatus
    invited_by_email: EmailStr
    role: Optional[str] = None
    tenant_id: Optional[int] = None
    created_at: datetime
    expires_at: datetime
    accepted_at: Optional[datetime] = None


class InvitationAccept(BaseModel):
    """Schema for accepting an invitation"""

    token: str
    password: str


class InvitationToken(BaseModel):
    """Schema for invitation token validation"""

    email: EmailStr
    full_name: str
    invited_by_email: EmailStr
    expires_at: datetime
    role: Optional[str] = None
    tenant_name: Optional[str] = None
