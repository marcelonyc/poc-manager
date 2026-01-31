"""Task schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.models.task import TaskStatus

if TYPE_CHECKING:
    pass


class TaskBase(BaseModel):
    """Base task schema"""
    title: str
    description: Optional[str] = None


class TaskCreate(TaskBase):
    """Schema for creating a task template"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = None
    description: Optional[str] = None


class Task(TaskBase):
    """Schema for task response"""
    id: int
    tenant_id: int
    created_by: int
    is_template: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskGroupBase(BaseModel):
    """Base task group schema"""
    title: str
    description: Optional[str] = None


class TaskGroupCreate(TaskGroupBase):
    """Schema for creating a task group template"""
    pass


class TaskGroupUpdate(BaseModel):
    """Schema for updating a task group"""
    title: Optional[str] = None
    description: Optional[str] = None


class TaskGroup(TaskGroupBase):
    """Schema for task group response"""
    id: int
    tenant_id: int
    created_by: int
    is_template: bool
    created_at: datetime
    tasks: List['Task'] = []
    
    class Config:
        from_attributes = True


class POCTaskBase(BaseModel):
    """Base POC task schema"""
    title: str
    description: Optional[str] = None
    sort_order: Optional[int] = 0


class POCTaskCreate(POCTaskBase):
    """Schema for creating a POC task"""
    task_id: Optional[int] = None  # Reference to template
    success_criteria_ids: Optional[list[int]] = []


class POCTaskUpdate(BaseModel):
    """Schema for updating a POC task"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    success_level: Optional[int] = None
    sort_order: Optional[int] = None


class POCTask(POCTaskBase):
    """Schema for POC task response"""
    id: int
    poc_id: int
    task_id: Optional[int]
    status: TaskStatus
    success_level: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class POCTaskGroupBase(BaseModel):
    """Base POC task group schema"""
    title: str
    description: Optional[str] = None
    sort_order: Optional[int] = 0


class POCTaskGroupCreate(POCTaskGroupBase):
    """Schema for creating a POC task group"""
    task_group_id: Optional[int] = None
    success_criteria_ids: Optional[list[int]] = []


class POCTaskGroupUpdate(BaseModel):
    """Schema for updating a POC task group"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    success_level: Optional[int] = None
    sort_order: Optional[int] = None


class POCTaskGroup(POCTaskGroupBase):
    """Schema for POC task group response"""
    id: int
    poc_id: int
    task_group_id: Optional[int]
    status: TaskStatus
    success_level: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
