"""POC Public Link schemas"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class POCPublicLinkCreate(BaseModel):
    """Schema for creating a public link"""

    pass  # No additional fields needed, poc_id comes from URL


class POCPublicLinkResponse(BaseModel):
    """Schema for public link response"""

    id: int
    poc_id: int
    tenant_id: int
    created_by: int
    access_token: str
    is_deleted: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class POCPublicLinkDetail(BaseModel):
    """Schema for public link detail with access URL"""

    id: int
    poc_id: int
    access_token: str
    access_url: str  # Full URL for sharing
    created_at: datetime
    created_by: int

    model_config = ConfigDict(from_attributes=True)


class POCPublicLinkDelete(BaseModel):
    """Schema for deleting a public link"""

    pass
