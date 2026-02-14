"""Task Template Resource schemas"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class TaskResourceBase(BaseModel):
    """Base task resource schema"""

    title: str
    description: Optional[str] = None
    resource_type: str  # link, code, text, file
    content: str
    sort_order: int = 0


class TaskResourceCreate(TaskResourceBase):
    """Schema for creating a task resource"""

    pass


class TaskResourceUpdate(BaseModel):
    """Schema for updating a task resource"""

    title: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    content: Optional[str] = None
    sort_order: Optional[int] = None


class TaskResource(TaskResourceBase):
    """Schema for task resource response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    created_at: datetime
    updated_at: Optional[datetime]


class TaskGroupResource(TaskResourceBase):
    """Schema for task group resource response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    task_group_id: int
    created_at: datetime
    updated_at: Optional[datetime]
