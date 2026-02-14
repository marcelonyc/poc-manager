"""Success Criteria schemas"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class SuccessCriteriaBase(BaseModel):
    """Base success criteria schema"""

    title: str
    description: Optional[str] = None
    target_value: Optional[str] = None
    importance_level: int = 3  # 1-5 scale


class SuccessCriteriaCreate(SuccessCriteriaBase):
    """Schema for creating success criteria"""

    poc_id: int
    sort_order: int = 0


class SuccessCriteriaUpdate(BaseModel):
    """Schema for updating success criteria"""

    title: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[str] = None
    achieved_value: Optional[str] = None
    is_met: Optional[bool] = None
    importance_level: Optional[int] = None
    sort_order: Optional[int] = None


class SuccessCriteria(SuccessCriteriaBase):
    """Schema for success criteria response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    poc_id: int
    achieved_value: Optional[str]
    is_met: bool
    sort_order: int
    created_at: datetime
    updated_at: Optional[datetime]
