"""API Key schemas"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class APIKeyExpiration(str, Enum):
    """Allowed expiration durations for API keys"""

    SIX_MONTHS = "6_months"
    ONE_YEAR = "1_year"
    TWO_YEARS = "2_years"


class APIKeyCreate(BaseModel):
    """Schema for creating an API key"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Friendly name for the key",
    )
    expiration: APIKeyExpiration


class APIKeyExtend(BaseModel):
    """Schema for extending an API key's expiration"""

    expiration: APIKeyExpiration


class APIKeyResponse(BaseModel):
    """Schema for API key response (without the actual key)"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    key_prefix: str
    expires_at: datetime
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]


class APIKeyCreated(BaseModel):
    """Schema returned when an API key is created — includes the raw key (shown only once)"""

    id: int
    name: str
    key_prefix: str
    api_key: str  # The full key — displayed only at creation time
    expires_at: datetime
    created_at: datetime
    message: str = (
        "Save this API key now. It cannot be recovered later. "
        "We recommend storing it in a secrets vault such as Dashlane, 1Password, or HashiCorp Vault."
    )
