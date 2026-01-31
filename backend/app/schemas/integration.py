"""Integration schemas"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.integration import IntegrationType


class IntegrationConfigBase(BaseModel):
    """Base integration configuration schema"""
    integration_type: IntegrationType
    is_enabled: bool = True


class SlackConfig(BaseModel):
    """Slack integration configuration"""
    token: str
    channel: str


class JiraConfig(BaseModel):
    """Jira integration configuration"""
    url: str
    email: str
    api_token: str
    project_key: Optional[str] = None


class GitHubConfig(BaseModel):
    """GitHub integration configuration"""
    token: str
    default_repo: Optional[str] = None


class EmailConfig(BaseModel):
    """Email integration configuration"""
    server: str
    port: int
    username: str
    password: str
    from_address: str
    tls: bool = True


class IntegrationCreate(IntegrationConfigBase):
    """Schema for creating an integration"""
    config: Dict[str, Any]


class IntegrationUpdate(BaseModel):
    """Schema for updating an integration"""
    is_enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class Integration(IntegrationConfigBase):
    """Schema for integration response"""
    id: int
    tenant_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class IntegrationDetail(Integration):
    """Schema for detailed integration response with config"""
    config: Dict[str, Any] = {}
