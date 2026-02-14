"""POC Invitation schemas"""

from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.poc_invitation import POCInvitationStatus


class POCInvitationCreate(BaseModel):
    """Schema for creating a POC invitation"""

    email: EmailStr
    full_name: str
    is_customer: bool = True
    personal_message: Optional[str] = None


class POCInvitationResponse(BaseModel):
    """Schema for POC invitation response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    poc_id: int
    email: EmailStr
    full_name: str
    status: POCInvitationStatus
    is_customer: bool
    personal_message: Optional[str]
    invited_by: int
    created_at: datetime
    expires_at: datetime
    accepted_at: Optional[datetime]
    email_sent: bool
    email_error: Optional[str]
    resend_count: int
    last_resent_at: Optional[datetime]


class POCInvitationAccept(BaseModel):
    """Schema for accepting a POC invitation"""

    token: str
    password: Optional[str] = None  # Required only if user doesn't exist


class POCInvitationToken(BaseModel):
    """Schema for POC invitation token validation"""

    poc_id: int
    poc_title: str
    email: EmailStr
    full_name: str
    is_customer: bool
    invited_by_name: str
    expires_at: datetime
    personal_message: Optional[str]
    user_exists: bool  # Whether user account already exists
