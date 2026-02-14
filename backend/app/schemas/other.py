"""Success criteria, comment, and resource schemas"""

from pydantic import BaseModel, field_validator, model_validator, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.resource import ResourceType


class SuccessCriteriaBase(BaseModel):
    """Base success criteria schema"""

    title: str
    description: Optional[str] = None
    target_value: Optional[str] = None
    sort_order: Optional[int] = 0


class SuccessCriteriaCreate(SuccessCriteriaBase):
    """Schema for creating success criteria"""

    pass


class SuccessCriteriaUpdate(BaseModel):
    """Schema for updating success criteria"""

    title: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[str] = None
    achieved_value: Optional[str] = None
    is_met: Optional[bool] = None
    sort_order: Optional[int] = None


class SuccessCriteria(SuccessCriteriaBase):
    """Schema for success criteria response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    poc_id: int
    achieved_value: Optional[str]
    is_met: bool
    created_at: datetime


class CommentBase(BaseModel):
    """Base comment schema"""

    subject: str
    content: str
    is_internal: bool = False

    @field_validator("content")
    @classmethod
    def validate_content_length(cls, v):
        if len(v) > 1000:
            raise ValueError("Content must be 1000 characters or less")
        return v


class CommentCreate(BaseModel):
    """Schema for creating a comment"""

    subject: str
    content: str
    is_internal: bool = False
    poc_task_id: Optional[int] = None
    poc_task_group_id: Optional[int] = None

    @field_validator("content")
    @classmethod
    def validate_content_length(cls, v):
        if len(v) > 1000:
            raise ValueError("Content must be 1000 characters or less")
        return v

    @model_validator(mode="after")
    def validate_task_or_taskgroup(self):
        """Ensure comment is associated with either a task or task group"""
        if not self.poc_task_id and not self.poc_task_group_id:
            raise ValueError(
                "Comment must be associated with either a task (poc_task_id) or task group (poc_task_group_id)"
            )
        if self.poc_task_id and self.poc_task_group_id:
            raise ValueError(
                "Comment must be associated with either a task or task group, not both"
            )
        return self


class CommentUpdate(BaseModel):
    """Schema for updating a comment"""

    subject: Optional[str] = None
    content: Optional[str] = None
    is_internal: Optional[bool] = None

    @field_validator("content")
    @classmethod
    def validate_content_length_update(cls, v):
        if v and len(v) > 1000:
            raise ValueError("Content must be 1000 characters or less")
        return v


class Comment(CommentBase):
    """Schema for comment response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int]
    poc_id: Optional[int]
    poc_task_id: Optional[int]
    poc_task_group_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    user: Optional[dict] = None


class ResourceBase(BaseModel):
    """Base resource schema"""

    title: str
    description: Optional[str] = None
    resource_type: ResourceType
    content: str
    sort_order: Optional[int] = 0


class ResourceCreate(ResourceBase):
    """Schema for creating a resource"""

    success_criteria_id: Optional[int] = None


class ResourceUpdate(BaseModel):
    """Schema for updating a resource"""

    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    success_criteria_id: Optional[int] = None
    sort_order: Optional[int] = None


class Resource(ResourceBase):
    """Schema for resource response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    poc_id: Optional[int] = None
    poc_task_id: Optional[int] = None
    poc_task_group_id: Optional[int] = None
    success_criteria_id: Optional[int]
    created_at: datetime
