"""Task router"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.task import Task, TaskGroup, POCTask, POCTaskGroup, TaskStatus
from app.models.success_criteria import TaskSuccessCriteria
from app.models.poc import POC
from app.models.task_template_resource import TaskTemplateResource
from app.models.task_group_resource import TaskGroupResource
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    Task as TaskSchema,
    TaskGroupCreate,
    TaskGroupUpdate,
    TaskGroup as TaskGroupSchema,
    POCTaskCreate,
    POCTaskUpdate,
    POCTask as POCTaskSchema,
    POCTaskGroupCreate,
    POCTaskGroupUpdate,
    POCTaskGroup as POCTaskGroupSchema,
)
from app.schemas.task_resource import (
    TaskResourceCreate,
    TaskResourceUpdate,
    TaskResource as TaskResourceSchema,
    TaskGroupResource as TaskGroupResourceSchema,
)
from app.auth import (
    require_administrator,
    require_sales_engineer,
    get_current_user,
    get_current_tenant_id,
    check_tenant_access,
)
from app.utils.demo_limits import (
    check_demo_task_limit,
    check_demo_task_group_limit,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# Task Templates
@router.post(
    "/templates",
    response_model=TaskSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_task_template(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Create a reusable task template"""
    # Check demo limits
    check_demo_task_limit(db, tenant_id, current_user.tenant)

    task = Task(
        title=task_data.title,
        description=task_data.description,
        tenant_id=tenant_id,
        created_by=current_user.id,
        is_template=True,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/templates", response_model=List[TaskSchema])
def list_task_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """List task templates"""
    tasks = (
        db.query(Task)
        .filter(Task.tenant_id == tenant_id, Task.is_template == True)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return tasks


@router.put("/templates/{task_id}", response_model=TaskSchema)
def update_task_template(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Update a task template"""
    # Fetch with tenant filter to prevent enumeration
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.tenant_id == tenant_id)
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    update_data = task_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


# Task Group Templates
@router.post(
    "/groups/templates",
    response_model=TaskGroupSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_task_group_template(
    group_data: TaskGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Create a reusable task group template"""
    # Check demo limits
    check_demo_task_group_limit(db, tenant_id, current_user.tenant)

    task_group = TaskGroup(
        title=group_data.title,
        description=group_data.description,
        tenant_id=tenant_id,
        created_by=current_user.id,
        is_template=True,
    )
    db.add(task_group)
    db.commit()
    db.refresh(task_group)
    return task_group


@router.get("/groups/templates", response_model=List[TaskGroupSchema])
def list_task_group_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """List task group templates"""
    groups = (
        db.query(TaskGroup)
        .filter(
            TaskGroup.tenant_id == tenant_id,
            TaskGroup.is_template == True,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    return groups


@router.put("/groups/templates/{group_id}", response_model=TaskGroupSchema)
def update_task_group_template(
    group_id: int,
    group_data: TaskGroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Update a task group"""
    # Fetch with tenant filter to prevent enumeration
    task_group = (
        db.query(TaskGroup)
        .filter(TaskGroup.id == group_id, TaskGroup.tenant_id == tenant_id)
        .first()
    )
    if not task_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task group not found",
        )

    update_data = group_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task_group, field, value)

    db.commit()
    db.refresh(task_group)
    return task_group


@router.get("/groups/{group_id}/tasks", response_model=List[TaskSchema])
def get_task_group_tasks(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Get tasks in a task group"""
    # Fetch with tenant filter to prevent enumeration
    group = (
        db.query(TaskGroup)
        .filter(TaskGroup.id == group_id, TaskGroup.tenant_id == tenant_id)
        .first()
    )
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task group not found",
        )

    return group.tasks


@router.post("/groups/{group_id}/tasks/{task_id}")
def add_task_to_group(
    group_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
):
    """Add a task to a task group"""
    group = db.query(TaskGroup).filter(TaskGroup.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task group not found",
        )

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    if not check_tenant_access(current_user, group.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Check if task already in group
    if task in group.tasks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already in group",
        )

    group.tasks.append(task)
    db.commit()

    return {"message": "Task added to group successfully"}


@router.delete("/groups/{group_id}/tasks/{task_id}")
def remove_task_from_group(
    group_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
):
    """Remove a task from a task group"""
    group = db.query(TaskGroup).filter(TaskGroup.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task group not found",
        )

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    if not check_tenant_access(current_user, group.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Check if task in group
    if task not in group.tasks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Task not in group"
        )

    group.tasks.remove(task)
    db.commit()

    return {"message": "Task removed from group successfully"}


# POC Tasks
@router.post(
    "/pocs/{poc_id}/tasks",
    response_model=POCTaskSchema,
    status_code=status.HTTP_201_CREATED,
)
def add_task_to_poc(
    poc_id: int,
    task_data: POCTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """Add a task to a POC"""
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="POC not found"
        )

    if not check_tenant_access(current_user, poc.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Create POC task
    poc_task = POCTask(
        poc_id=poc_id,
        task_id=task_data.task_id,
        title=task_data.title,
        description=task_data.description,
        sort_order=task_data.sort_order,
        status=TaskStatus.NOT_STARTED,
    )
    db.add(poc_task)
    db.flush()

    # Link to success criteria
    if task_data.success_criteria_ids:
        for criteria_id in task_data.success_criteria_ids:
            link = TaskSuccessCriteria(
                success_criteria_id=criteria_id, poc_task_id=poc_task.id
            )
            db.add(link)

    db.commit()
    db.refresh(poc_task)
    return poc_task


@router.get("/pocs/{poc_id}/tasks", response_model=List[POCTaskSchema])
def list_poc_tasks(
    poc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List tasks for a POC"""
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="POC not found"
        )

    tasks = (
        db.query(POCTask)
        .filter(POCTask.poc_id == poc_id)
        .order_by(POCTask.sort_order)
        .all()
    )
    return tasks


@router.put("/pocs/{poc_id}/tasks/{task_id}", response_model=POCTaskSchema)
def update_poc_task(
    poc_id: int,
    task_id: int,
    task_data: POCTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a POC task"""
    poc_task = (
        db.query(POCTask)
        .filter(POCTask.id == task_id, POCTask.poc_id == poc_id)
        .first()
    )
    if not poc_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    update_data = task_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(poc_task, field, value)

    # Mark completed_at if status changed to completed
    if task_data.status == TaskStatus.COMPLETED and not poc_task.completed_at:
        poc_task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(poc_task)
    return poc_task


@router.delete("/pocs/{poc_id}/tasks/{task_id}")
def delete_poc_task(
    poc_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """Remove a task from a POC"""
    poc_task = (
        db.query(POCTask)
        .filter(POCTask.id == task_id, POCTask.poc_id == poc_id)
        .first()
    )
    if not poc_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    db.delete(poc_task)
    db.commit()
    return {"message": "Task removed successfully"}


# POC Task Groups
@router.post(
    "/pocs/{poc_id}/task-groups",
    response_model=POCTaskGroupSchema,
    status_code=status.HTTP_201_CREATED,
)
def add_task_group_to_poc(
    poc_id: int,
    group_data: POCTaskGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """Add a task group to a POC"""
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="POC not found"
        )

    poc_task_group = POCTaskGroup(
        poc_id=poc_id,
        task_group_id=group_data.task_group_id,
        title=group_data.title,
        description=group_data.description,
        sort_order=group_data.sort_order,
        status=TaskStatus.NOT_STARTED,
    )
    db.add(poc_task_group)
    db.flush()

    # Link to success criteria
    if group_data.success_criteria_ids:
        for criteria_id in group_data.success_criteria_ids:
            link = TaskSuccessCriteria(
                success_criteria_id=criteria_id,
                poc_task_group_id=poc_task_group.id,
            )
            db.add(link)

    db.commit()
    db.refresh(poc_task_group)
    return poc_task_group


@router.get(
    "/pocs/{poc_id}/task-groups", response_model=List[POCTaskGroupSchema]
)
def list_poc_task_groups(
    poc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List task groups for a POC"""
    groups = (
        db.query(POCTaskGroup)
        .filter(POCTaskGroup.poc_id == poc_id)
        .order_by(POCTaskGroup.sort_order)
        .all()
    )
    return groups


@router.put(
    "/pocs/{poc_id}/task-groups/{group_id}", response_model=POCTaskGroupSchema
)
def update_poc_task_group(
    poc_id: int,
    group_id: int,
    group_data: POCTaskGroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a POC task group"""
    poc_group = (
        db.query(POCTaskGroup)
        .filter(POCTaskGroup.id == group_id, POCTaskGroup.poc_id == poc_id)
        .first()
    )
    if not poc_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task group not found",
        )

    update_data = group_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(poc_group, field, value)

    if (
        group_data.status == TaskStatus.COMPLETED
        and not poc_group.completed_at
    ):
        poc_group.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(poc_group)
    return poc_group


@router.get(
    "/pocs/{poc_id}/task-groups/{group_id}/tasks",
    response_model=List[POCTaskSchema],
)
def get_poc_task_group_tasks(
    poc_id: int,
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tasks for a POC task group

    Returns POC tasks that were created from the task group's template tasks.
    If the task group has a template, returns tasks that match the template's task IDs.
    """
    # Get the POC task group
    poc_group = (
        db.query(POCTaskGroup)
        .filter(POCTaskGroup.id == group_id, POCTaskGroup.poc_id == poc_id)
        .first()
    )

    if not poc_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task group not found",
        )

    # If this group has a template, get tasks from that template
    if poc_group.task_group_id:
        task_group = (
            db.query(TaskGroup)
            .filter(TaskGroup.id == poc_group.task_group_id)
            .first()
        )
        if task_group and task_group.tasks:
            # Get template task IDs
            template_task_ids = [t.id for t in task_group.tasks]

            # Find POC tasks that were created from these template tasks
            poc_tasks = (
                db.query(POCTask)
                .filter(
                    POCTask.poc_id == poc_id,
                    POCTask.task_id.in_(template_task_ids),
                )
                .order_by(POCTask.sort_order)
                .all()
            )

            return poc_tasks

    # If no template or no tasks found, return empty list
    return []


# Task Template Resources
@router.post(
    "/templates/{task_id}/resources",
    response_model=TaskResourceSchema,
    status_code=status.HTTP_201_CREATED,
)
def add_resource_to_task_template(
    task_id: int,
    resource_data: TaskResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Add a resource to a task template"""
    # Check demo resource limit
    from app.utils.demo_limits import check_demo_resource_limit

    check_demo_resource_limit(db, tenant_id, current_user.tenant)

    # Fetch with tenant filter to prevent enumeration
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.tenant_id == tenant_id)
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    resource = TaskTemplateResource(
        task_id=task_id,
        title=resource_data.title,
        description=resource_data.description,
        resource_type=resource_data.resource_type,
        content=resource_data.content,
        sort_order=resource_data.sort_order,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.get(
    "/templates/{task_id}/resources", response_model=List[TaskResourceSchema]
)
def list_task_template_resources(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List resources for a task template"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    if not check_tenant_access(current_user, task.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    resources = (
        db.query(TaskTemplateResource)
        .filter(TaskTemplateResource.task_id == task_id)
        .order_by(TaskTemplateResource.sort_order)
        .all()
    )
    return resources


@router.put(
    "/templates/{task_id}/resources/{resource_id}",
    response_model=TaskResourceSchema,
)
def update_task_template_resource(
    task_id: int,
    resource_id: int,
    resource_data: TaskResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
):
    """Update a task template resource"""
    resource = (
        db.query(TaskTemplateResource)
        .filter(
            TaskTemplateResource.id == resource_id,
            TaskTemplateResource.task_id == task_id,
        )
        .first()
    )
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    task = db.query(Task).filter(Task.id == task_id).first()
    if not check_tenant_access(current_user, task.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    update_data = resource_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)

    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/templates/{task_id}/resources/{resource_id}")
def delete_task_template_resource(
    task_id: int,
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
):
    """Delete a task template resource"""
    resource = (
        db.query(TaskTemplateResource)
        .filter(
            TaskTemplateResource.id == resource_id,
            TaskTemplateResource.task_id == task_id,
        )
        .first()
    )
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    task = db.query(Task).filter(Task.id == task_id).first()
    if not check_tenant_access(current_user, task.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    db.delete(resource)
    db.commit()
    return {"message": "Resource deleted successfully"}


# Task Group Resources
@router.post(
    "/groups/templates/{group_id}/resources",
    response_model=TaskGroupResourceSchema,
    status_code=status.HTTP_201_CREATED,
)
def add_resource_to_task_group(
    group_id: int,
    resource_data: TaskResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Add a resource to a task group template"""
    # Check demo resource limit
    from app.utils.demo_limits import check_demo_resource_limit

    check_demo_resource_limit(db, tenant_id, current_user.tenant)

    # Fetch with tenant filter to prevent enumeration
    task_group = (
        db.query(TaskGroup)
        .filter(TaskGroup.id == group_id, TaskGroup.tenant_id == tenant_id)
        .first()
    )
    if not task_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task group not found",
        )

    resource = TaskGroupResource(
        task_group_id=group_id,
        title=resource_data.title,
        description=resource_data.description,
        resource_type=resource_data.resource_type,
        content=resource_data.content,
        sort_order=resource_data.sort_order,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.get(
    "/groups/templates/{group_id}/resources",
    response_model=List[TaskGroupResourceSchema],
)
def list_task_group_resources(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List resources for a task group template"""
    task_group = db.query(TaskGroup).filter(TaskGroup.id == group_id).first()
    if not task_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task group not found",
        )

    if not check_tenant_access(current_user, task_group.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    resources = (
        db.query(TaskGroupResource)
        .filter(TaskGroupResource.task_group_id == group_id)
        .order_by(TaskGroupResource.sort_order)
        .all()
    )
    return resources


@router.put(
    "/groups/templates/{group_id}/resources/{resource_id}",
    response_model=TaskGroupResourceSchema,
)
def update_task_group_resource(
    group_id: int,
    resource_id: int,
    resource_data: TaskResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
):
    """Update a task group resource"""
    resource = (
        db.query(TaskGroupResource)
        .filter(
            TaskGroupResource.id == resource_id,
            TaskGroupResource.task_group_id == group_id,
        )
        .first()
    )
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    task_group = db.query(TaskGroup).filter(TaskGroup.id == group_id).first()
    if not check_tenant_access(current_user, task_group.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    update_data = resource_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)

    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/groups/templates/{group_id}/resources/{resource_id}")
def delete_task_group_resource(
    group_id: int,
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
):
    """Delete a task group resource"""
    resource = (
        db.query(TaskGroupResource)
        .filter(
            TaskGroupResource.id == resource_id,
            TaskGroupResource.task_group_id == group_id,
        )
        .first()
    )
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    task_group = db.query(TaskGroup).filter(TaskGroup.id == group_id).first()
    if not check_tenant_access(current_user, task_group.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    db.delete(resource)
    db.commit()
    return {"message": "Resource deleted successfully"}
