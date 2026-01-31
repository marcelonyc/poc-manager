"""Invitation schemas"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.invitation import InvitationStatus


class InvitationCreate(BaseModel):
    """Schema for creating an invitation"""
    email: EmailStr
    full_name: str


class InvitationResponse(BaseModel):
    """Schema for invitation response"""
    id: int
    email: EmailStr
    full_name: str
    status: InvitationStatus
    invited_by_email: EmailStr
    created_at: datetime
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


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
