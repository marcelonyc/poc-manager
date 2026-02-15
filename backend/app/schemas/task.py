"""Task schemas"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date
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

    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    created_by: int
    is_template: bool
    created_at: datetime


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

    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    created_by: int
    is_template: bool
    created_at: datetime
    tasks: List["Task"] = []


class POCTaskBase(BaseModel):
    """Base POC task schema"""

    title: str
    description: Optional[str] = None
    sort_order: Optional[int] = 0
    start_date: Optional[date] = None
    due_date: Optional[date] = None


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
    success_criteria_ids: Optional[List[int]] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None


class POCTaskAssignee(BaseModel):
    """Schema for task assignee response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    participant_id: int
    participant_name: str
    participant_email: str
    assigned_at: datetime


class POCTaskAssignRequest(BaseModel):
    """Schema for assigning/unassigning participants to a task"""

    participant_ids: List[int]


class POCTask(POCTaskBase):
    """Schema for POC task response"""

    id: int
    poc_id: int
    task_id: Optional[int]
    status: TaskStatus
    success_level: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    assignees: List[POCTaskAssignee] = []
    success_criteria_ids: List[int] = []

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class POCTaskGroupBase(BaseModel):
    """Base POC task group schema"""

    title: str
    description: Optional[str] = None
    sort_order: Optional[int] = 0
    start_date: Optional[date] = None
    due_date: Optional[date] = None


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
    start_date: Optional[date] = None
    due_date: Optional[date] = None


class POCTaskGroup(POCTaskGroupBase):
    """Schema for POC task group response"""

    id: int
    poc_id: int
    task_group_id: Optional[int]
    status: TaskStatus
    success_level: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    success_criteria_ids: List[int] = []
    tasks: List[POCTask] = []

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
