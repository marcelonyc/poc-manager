"""Tenant schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class TenantBase(BaseModel):
    """Base tenant schema"""
    name: str
    slug: str
    primary_color: Optional[str] = "#0066cc"
    secondary_color: Optional[str] = "#333333"
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None


class TenantCreate(TenantBase):
    """Schema for creating a tenant"""
    initial_admin_email: EmailStr
    initial_admin_name: str
    initial_admin_password: str


class TenantUpdate(BaseModel):
    """Schema for updating a tenant"""
    name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    tenant_admin_limit: Optional[int] = None
    administrator_limit: Optional[int] = None
    sales_engineer_limit: Optional[int] = None
    customer_limit: Optional[int] = None
    is_active: Optional[bool] = None
    # Email configuration
    custom_mail_server: Optional[str] = None
    custom_mail_port: Optional[int] = None
    custom_mail_username: Optional[str] = None
    custom_mail_password: Optional[str] = None
    custom_mail_from: Optional[str] = None
    custom_mail_tls: Optional[bool] = None


class TenantEmailConfig(BaseModel):
    """Schema for tenant email configuration"""
    custom_mail_server: Optional[str] = None
    custom_mail_port: Optional[int] = None
    custom_mail_username: Optional[str] = None
    custom_mail_password: Optional[str] = None
    custom_mail_from: Optional[str] = None
    custom_mail_tls: Optional[bool] = True


class Tenant(TenantBase):
    """Schema for tenant response"""
    id: int
    logo_url: Optional[str] = None
    tenant_admin_limit: int
    administrator_limit: int
    sales_engineer_limit: int
    customer_limit: int
    is_active: bool
    created_at: datetime
    # Email configuration (masked for security)
    has_custom_mail_config: bool = False
    custom_mail_server: Optional[str] = None
    custom_mail_port: Optional[int] = None
    custom_mail_from: Optional[str] = None
    custom_mail_tls: Optional[bool] = None
    
    class Config:
        from_attributes = True
