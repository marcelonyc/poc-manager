"""Task router"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from app.database import get_db
from app.models.user import User
from app.models.task import (
    Task,
    TaskGroup,
    POCTask,
    POCTaskGroup,
    TaskStatus,
    POCTaskAssignee,
)
from app.models.success_criteria import TaskSuccessCriteria
from app.models.poc import POC, POCParticipant
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
    POCTaskAssignRequest,
    POCTaskAssignee as POCTaskAssigneeSchema,
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
    """
    Create a reusable task template.

    Purpose: Define a task template that can be reused across multiple POCs.
    Templates enable standardization and faster POC setup.

    Args:
        task_data: TaskCreate with title and description

    Returns:
        TaskSchema marking task as template

    Requires: Administrator role

    Raises:
        403 Forbidden: Insufficient permissions
    """
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
    """
    List all reusable task templates for the current tenant.

    Returns the catalog of task templates that can be added to POCs.
    Templates are tenant-scoped; only templates belonging to the caller's tenant are returned.
    Use this to discover available tasks before adding them to a POC.

    Route: GET /tasks/templates?skip=0&limit=100

    Query parameters:
        skip (int, default 0): Number of records to skip for pagination.
        limit (int, default 100): Maximum number of records to return (max 100).

    Returns:
        List of task template objects, each containing:
            - id (int): Unique task template identifier.
            - title (str): Template name.
            - description (str | null): Detailed template description.
            - tenant_id (int): Owning tenant ID.
            - created_by (int): User ID of the creator.
            - is_template (bool): Always true for templates.
            - created_at (datetime): Creation timestamp.

    Errors:
        401 Unauthorized: Missing or invalid authentication token.
    """
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
    """
    Update a task template.

    Purpose: Modify task template details (title, description).

    Args:
        task_id (int): Task template ID
        task_data: TaskUpdate with fields to modify

    Returns:
        Updated TaskSchema

    Requires: Administrator role

    Raises:
        404 Not Found: Template not found
        403 Forbidden: Insufficient permissions
    """
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

    update_data = task_data.model_dump(exclude_unset=True)
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
    """
    Create a reusable task group template.

    Purpose: Define a task group template containing multiple related tasks.
    Groups enable organizing related tasks and can be used together in POCs.

    Args:
        group_data: TaskGroupCreate with title and description

    Returns:
        TaskGroupSchema marking group as template

    Requires: Administrator role

    Raises:
        403 Forbidden: Insufficient permissions
    """
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
    """
    List all reusable task group templates for the current tenant.

    Returns the catalog of task group templates that bundle related tasks together.
    Groups are tenant-scoped; only groups belonging to the caller's tenant are returned.
    Use this to discover available task groups before adding them to a POC.

    Route: GET /tasks/groups/templates?skip=0&limit=100

    Query parameters:
        skip (int, default 0): Number of records to skip for pagination.
        limit (int, default 100): Maximum number of records to return (max 100).

    Returns:
        List of task group template objects, each containing:
            - id (int): Unique task group template identifier.
            - title (str): Group template name.
            - description (str | null): Detailed group description.
            - tenant_id (int): Owning tenant ID.
            - created_by (int): User ID of the creator.
            - is_template (bool): Always true for templates.
            - created_at (datetime): Creation timestamp.
            - tasks (list): List of task templates belonging to this group.

    Errors:
        401 Unauthorized: Missing or invalid authentication token.
    """
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
    """
    Update a task group template.

    Purpose: Modify task group template details.

    Args:
        group_id (int): Task group template ID
        group_data: TaskGroupUpdate with fields to modify

    Returns:
        Updated TaskGroupSchema

    Requires: Administrator role

    Raises:
        404 Not Found: Template not found
        403 Forbidden: Insufficient permissions
    """
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

    update_data = group_data.model_dump(exclude_unset=True)
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
    """
    List all task templates that belong to a specific task group template.

    Returns the individual task templates associated with the given group.
    Use this to inspect which tasks are bundled in a group before adding the group to a POC.

    Route: GET /tasks/groups/{group_id}/tasks

    Path parameters:
        group_id (int): The unique identifier of the task group template.

    Returns:
        List of task template objects, each containing:
            - id (int): Unique task template identifier.
            - title (str): Task name.
            - description (str | null): Task description.
            - tenant_id (int): Owning tenant ID.
            - created_by (int): User ID of the creator.
            - is_template (bool): Always true.
            - created_at (datetime): Creation timestamp.

    Errors:
        404 Not Found: Task group template with the given group_id does not exist in the caller's tenant.
        401 Unauthorized: Missing or invalid authentication token.
    """
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

    # Validate and default task dates against POC timeline
    start_date = task_data.start_date
    due_date = task_data.due_date

    # Default due_date to POC end_date if not provided
    if due_date is None and poc.end_date:
        due_date = poc.end_date

    # Validate due_date is within POC timeline
    if due_date is not None:
        if poc.start_date and due_date < poc.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task due date cannot be before the POC start date",
            )
        if poc.end_date and due_date > poc.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task due date cannot be after the POC end date",
            )

    # Validate start_date is within POC timeline
    if start_date is not None:
        if poc.start_date and start_date < poc.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task start date cannot be before the POC start date",
            )
        if poc.end_date and start_date > poc.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task start date cannot be after the POC end date",
            )

    # Validate start_date <= due_date
    if start_date is not None and due_date is not None:
        if start_date > due_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task start date cannot be after the task due date",
            )

    # Create POC task
    poc_task = POCTask(
        poc_id=poc_id,
        task_id=task_data.task_id,
        title=task_data.title,
        description=task_data.description,
        sort_order=task_data.sort_order,
        start_date=start_date,
        due_date=due_date,
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
    """
    List all tasks for a specific POC, including assignees and linked success criteria.

    Returns every task currently added to the POC, sorted by sort_order.
    Each task includes the list of participants assigned to it and the IDs of
    success criteria it is linked to. Use this to get a complete view of POC
    task progress and responsibility assignments.

    Route: GET /tasks/pocs/{poc_id}/tasks

    Path parameters:
        poc_id (int): The unique identifier of the POC.

    Returns:
        List of POC task objects, each containing:
            - id (int): Unique POC task identifier.
            - poc_id (int): Parent POC identifier.
            - task_id (int | null): Reference to the source task template, if any.
            - title (str): Task name.
            - description (str | null): Task description.
            - status (str): Current status — one of "not_started", "in_progress", "completed", "blocked".
            - success_level (int | null): Numeric success rating (set after completion).
            - sort_order (int): Display/execution order within the POC.
            - created_at (datetime): Creation timestamp.
            - completed_at (datetime | null): Completion timestamp, if completed.
            - assignees (list): People assigned to this task, each with:
                - id (int): Assignee record identifier.
                - participant_id (int): POC participant identifier.
                - participant_name (str): Full name of the assigned person.
                - participant_email (str): Email address of the assigned person.
                - assigned_at (datetime): When the assignment was made.
            - success_criteria_ids (list[int]): IDs of success criteria linked to this task.

    Errors:
        404 Not Found: POC with the given poc_id does not exist.
        401 Unauthorized: Missing or invalid authentication token.
    """
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

    # Include assignees in the response
    result = []
    for task in tasks:
        task_dict = POCTaskSchema.model_validate(task).model_dump()

        # Get assignees for this task
        assignees = (
            db.query(POCTaskAssignee)
            .filter(POCTaskAssignee.poc_task_id == task.id)
            .all()
        )

        task_dict["assignees"] = [
            POCTaskAssigneeSchema(
                id=a.id,
                participant_id=a.participant_id,
                participant_name=a.participant.user.full_name,
                participant_email=a.participant.user.email,
                assigned_at=a.assigned_at,
            )
            for a in assignees
        ]

        # Get success criteria IDs for this task
        criteria_links = (
            db.query(TaskSuccessCriteria)
            .filter(TaskSuccessCriteria.poc_task_id == task.id)
            .all()
        )
        task_dict["success_criteria_ids"] = [
            link.success_criteria_id for link in criteria_links
        ]

        result.append(task_dict)

    return result


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

    update_data = task_data.model_dump(exclude_unset=True)

    # Validate task dates against POC timeline
    poc = db.query(POC).filter(POC.id == poc_id).first()
    new_start = update_data.get("start_date", poc_task.start_date)
    new_due = update_data.get("due_date", poc_task.due_date)

    if new_due is not None and poc:
        if poc.start_date and new_due < poc.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task due date cannot be before the POC start date",
            )
        if poc.end_date and new_due > poc.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task due date cannot be after the POC end date",
            )

    if new_start is not None and poc:
        if poc.start_date and new_start < poc.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task start date cannot be before the POC start date",
            )
        if poc.end_date and new_start > poc.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task start date cannot be after the POC end date",
            )

    if new_start is not None and new_due is not None:
        if new_start > new_due:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task start date cannot be after the task due date",
            )

    # Handle success_criteria_ids separately (junction table)
    if "success_criteria_ids" in update_data:
        criteria_ids = update_data.pop("success_criteria_ids")
        # Remove existing links
        db.query(TaskSuccessCriteria).filter(
            TaskSuccessCriteria.poc_task_id == task_id
        ).delete()
        # Add new links
        if criteria_ids:
            for criteria_id in criteria_ids:
                link = TaskSuccessCriteria(
                    success_criteria_id=criteria_id,
                    poc_task_id=task_id,
                )
                db.add(link)

    for field, value in update_data.items():
        setattr(poc_task, field, value)

    # Mark completed_at if status changed to completed
    if task_data.status == TaskStatus.COMPLETED and not poc_task.completed_at:
        poc_task.completed_at = datetime.now(timezone.utc)

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


# Task Assignment Endpoints
@router.post(
    "/pocs/{poc_id}/tasks/{task_id}/assign",
    response_model=List[POCTaskAssigneeSchema],
)
def assign_task_to_participants(
    poc_id: int,
    task_id: int,
    assign_data: POCTaskAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """Assign a POC task to one or more participants"""
    # Verify task exists and belongs to POC
    poc_task = (
        db.query(POCTask)
        .filter(POCTask.id == task_id, POCTask.poc_id == poc_id)
        .first()
    )
    if not poc_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    # Verify POC exists and user has access
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="POC not found"
        )

    if not check_tenant_access(current_user, poc.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Get all valid participants for this POC
    valid_participant_ids = [
        p.id
        for p in db.query(POCParticipant)
        .filter(POCParticipant.poc_id == poc_id)
        .all()
    ]

    # Validate that all requested participant IDs are valid
    invalid_ids = [
        pid
        for pid in assign_data.participant_ids
        if pid not in valid_participant_ids
    ]
    if invalid_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid participant IDs: {invalid_ids}",
        )

    # Remove existing assignments
    db.query(POCTaskAssignee).filter(
        POCTaskAssignee.poc_task_id == task_id
    ).delete()

    # Create new assignments
    new_assignees = []
    for participant_id in assign_data.participant_ids:
        assignee = POCTaskAssignee(
            poc_task_id=task_id,
            participant_id=participant_id,
            assigned_by=current_user.id,
        )
        db.add(assignee)
        new_assignees.append(assignee)

    db.commit()

    # Refresh and return with participant details
    result = []
    for assignee in new_assignees:
        db.refresh(assignee)
        participant = assignee.participant
        result.append(
            POCTaskAssigneeSchema(
                id=assignee.id,
                participant_id=assignee.participant_id,
                participant_name=participant.user.full_name,
                participant_email=participant.user.email,
                assigned_at=assignee.assigned_at,
            )
        )

    return result


@router.get(
    "/pocs/{poc_id}/tasks/{task_id}/assignees",
    response_model=List[POCTaskAssigneeSchema],
)
def get_task_assignees(
    poc_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all participants assigned to a specific POC task.

    Returns the people responsible for completing this task within the POC.
    Use this to check who is working on a particular task.

    Route: GET /tasks/pocs/{poc_id}/tasks/{task_id}/assignees

    Path parameters:
        poc_id (int): The unique identifier of the POC.
        task_id (int): The unique identifier of the POC task.

    Returns:
        List of assignee objects, each containing:
            - id (int): Assignee record identifier.
            - participant_id (int): POC participant identifier.
            - participant_name (str): Full name of the assigned person.
            - participant_email (str): Email address of the assigned person.
            - assigned_at (datetime): When the assignment was made.

    Errors:
        404 Not Found: POC task with the given task_id does not exist in the specified POC.
        401 Unauthorized: Missing or invalid authentication token.
    """
    # Verify task exists
    poc_task = (
        db.query(POCTask)
        .filter(POCTask.id == task_id, POCTask.poc_id == poc_id)
        .first()
    )
    if not poc_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    # Get assignees with participant details
    assignees = (
        db.query(POCTaskAssignee)
        .filter(POCTaskAssignee.poc_task_id == task_id)
        .all()
    )

    result = []
    for assignee in assignees:
        participant = assignee.participant
        result.append(
            POCTaskAssigneeSchema(
                id=assignee.id,
                participant_id=assignee.participant_id,
                participant_name=participant.user.full_name,
                participant_email=participant.user.email,
                assigned_at=assignee.assigned_at,
            )
        )

    return result


@router.delete("/pocs/{poc_id}/tasks/{task_id}/assign")
def unassign_all_participants(
    poc_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """Remove all assignees from a task"""
    # Verify task exists
    poc_task = (
        db.query(POCTask)
        .filter(POCTask.id == task_id, POCTask.poc_id == poc_id)
        .first()
    )
    if not poc_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    # Delete all assignments
    deleted_count = (
        db.query(POCTaskAssignee)
        .filter(POCTaskAssignee.poc_task_id == task_id)
        .delete()
    )

    db.commit()

    return {"message": f"Removed {deleted_count} assignee(s) from task"}


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

    # Validate and default task group dates against POC timeline
    start_date = group_data.start_date
    due_date = group_data.due_date

    if due_date is None and poc.end_date:
        due_date = poc.end_date

    if due_date is not None:
        if poc.start_date and due_date < poc.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task group due date cannot be before the POC start date",
            )
        if poc.end_date and due_date > poc.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task group due date cannot be after the POC end date",
            )

    if start_date is not None:
        if poc.start_date and start_date < poc.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task group start date cannot be before the POC start date",
            )
        if poc.end_date and start_date > poc.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task group start date cannot be after the POC end date",
            )

    if start_date is not None and due_date is not None:
        if start_date > due_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task group start date cannot be after the task group due date",
            )

    poc_task_group.start_date = start_date
    poc_task_group.due_date = due_date

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
    """
    List all task groups for a specific POC, including their tasks, assignees, and success criteria.

    Returns every task group currently added to the POC, sorted by sort_order.
    Each group includes its nested tasks (with assignees) and linked success criteria IDs.
    Use this to get a hierarchical view of POC work organized by groups.

    Route: GET /tasks/pocs/{poc_id}/task-groups

    Path parameters:
        poc_id (int): The unique identifier of the POC.

    Returns:
        List of POC task group objects, each containing:
            - id (int): Unique POC task group identifier.
            - poc_id (int): Parent POC identifier.
            - task_group_id (int | null): Reference to the source task group template, if any.
            - title (str): Group name.
            - description (str | null): Group description.
            - status (str): Current status — one of "not_started", "in_progress", "completed", "blocked".
            - success_level (int | null): Numeric success rating (set after completion).
            - sort_order (int): Display order within the POC.
            - created_at (datetime): Creation timestamp.
            - completed_at (datetime | null): Completion timestamp, if completed.
            - success_criteria_ids (list[int]): IDs of success criteria linked to this group.
            - tasks (list): POC tasks within this group, each with full task fields
              (id, title, description, status, assignees, success_criteria_ids, etc.).

    Errors:
        401 Unauthorized: Missing or invalid authentication token.
    """
    groups = (
        db.query(POCTaskGroup)
        .filter(POCTaskGroup.poc_id == poc_id)
        .order_by(POCTaskGroup.sort_order)
        .all()
    )

    result = []
    for group in groups:
        group_dict = POCTaskGroupSchema.model_validate(group).model_dump()

        # Get success criteria IDs for this group
        criteria_links = (
            db.query(TaskSuccessCriteria)
            .filter(TaskSuccessCriteria.poc_task_group_id == group.id)
            .all()
        )
        group_dict["success_criteria_ids"] = [
            link.success_criteria_id for link in criteria_links
        ]

        # Get tasks for this group (if it has a template)
        group_tasks = []
        if group.task_group_id:
            task_group = (
                db.query(TaskGroup)
                .filter(TaskGroup.id == group.task_group_id)
                .first()
            )
            if task_group and task_group.tasks:
                template_task_ids = [t.id for t in task_group.tasks]
                poc_tasks = (
                    db.query(POCTask)
                    .filter(
                        POCTask.poc_id == poc_id,
                        POCTask.task_id.in_(template_task_ids),
                    )
                    .order_by(POCTask.sort_order)
                    .all()
                )
                for task in poc_tasks:
                    task_dict = POCTaskSchema.model_validate(task).model_dump()
                    # Get assignees
                    assignees = (
                        db.query(POCTaskAssignee)
                        .filter(POCTaskAssignee.poc_task_id == task.id)
                        .all()
                    )
                    task_dict["assignees"] = [
                        POCTaskAssigneeSchema(
                            id=a.id,
                            participant_id=a.participant_id,
                            participant_name=a.participant.user.full_name
                            or a.participant.user.email,
                            participant_email=a.participant.user.email,
                            assigned_at=a.assigned_at,
                        ).model_dump()
                        for a in assignees
                    ]
                    # Get success criteria IDs for this task
                    task_criteria_links = (
                        db.query(TaskSuccessCriteria)
                        .filter(TaskSuccessCriteria.poc_task_id == task.id)
                        .all()
                    )
                    task_dict["success_criteria_ids"] = [
                        link.success_criteria_id
                        for link in task_criteria_links
                    ]
                    group_tasks.append(task_dict)

        group_dict["tasks"] = group_tasks
        result.append(group_dict)

    return result


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

    update_data = group_data.model_dump(exclude_unset=True)

    # Validate task group dates against POC timeline
    poc = db.query(POC).filter(POC.id == poc_id).first()
    new_start = update_data.get("start_date", poc_group.start_date)
    new_due = update_data.get("due_date", poc_group.due_date)

    if new_due is not None and poc:
        if poc.start_date and new_due < poc.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task group due date cannot be before the POC start date",
            )
        if poc.end_date and new_due > poc.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task group due date cannot be after the POC end date",
            )

    if new_start is not None and poc:
        if poc.start_date and new_start < poc.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task group start date cannot be before the POC start date",
            )
        if poc.end_date and new_start > poc.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task group start date cannot be after the POC end date",
            )

    if new_start is not None and new_due is not None:
        if new_start > new_due:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task group start date cannot be after the task group due date",
            )

    for field, value in update_data.items():
        setattr(poc_group, field, value)

    if (
        group_data.status == TaskStatus.COMPLETED
        and not poc_group.completed_at
    ):
        poc_group.completed_at = datetime.now(timezone.utc)

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
    """
    List all tasks within a specific task group in a POC.

    Returns the POC tasks that belong to the given group, based on the group's
    template task membership. Each task includes its assignees and linked success
    criteria. Returns an empty list if the group has no template or no matching tasks.

    Route: GET /tasks/pocs/{poc_id}/task-groups/{group_id}/tasks

    Path parameters:
        poc_id (int): The unique identifier of the POC.
        group_id (int): The unique identifier of the POC task group.

    Returns:
        List of POC task objects, each containing:
            - id (int): Unique POC task identifier.
            - poc_id (int): Parent POC identifier.
            - task_id (int | null): Reference to the source task template.
            - title (str): Task name.
            - description (str | null): Task description.
            - status (str): Current status — one of "not_started", "in_progress", "completed", "blocked".
            - success_level (int | null): Numeric success rating.
            - sort_order (int): Display order.
            - created_at (datetime): Creation timestamp.
            - completed_at (datetime | null): Completion timestamp.
            - assignees (list): People assigned to this task, each with:
                - id (int): Assignee record identifier.
                - participant_id (int): POC participant identifier.
                - participant_name (str): Full name.
                - participant_email (str): Email address.
                - assigned_at (datetime): Assignment timestamp.
            - success_criteria_ids (list[int]): IDs of linked success criteria.

    Errors:
        404 Not Found: Task group with the given group_id does not exist in the specified POC.
        401 Unauthorized: Missing or invalid authentication token.
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

            # Populate assignees for each task
            from app.schemas.task import (
                POCTaskAssignee as POCTaskAssigneeSchema,
            )

            result = []
            for task in poc_tasks:
                # Use POCTaskSchema to properly serialize the task
                task_dict = POCTaskSchema.model_validate(task).model_dump()

                # Get assignees for this task
                assignees = (
                    db.query(POCTaskAssignee)
                    .filter(POCTaskAssignee.poc_task_id == task.id)
                    .all()
                )

                task_dict["assignees"] = [
                    POCTaskAssigneeSchema(
                        id=a.id,
                        participant_id=a.participant_id,
                        participant_name=a.participant.user.full_name
                        or a.participant.user.email,
                        participant_email=a.participant.user.email,
                        assigned_at=a.assigned_at,
                    ).model_dump()
                    for a in assignees
                ]

                # Get success criteria IDs for this task
                criteria_links = (
                    db.query(TaskSuccessCriteria)
                    .filter(TaskSuccessCriteria.poc_task_id == task.id)
                    .all()
                )
                task_dict["success_criteria_ids"] = [
                    link.success_criteria_id for link in criteria_links
                ]

                result.append(task_dict)

            return result

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
    """
    List all resources attached to a specific task template.

    Returns links, code snippets, text blocks, or file references associated with
    the task template. Resources are sorted by sort_order. Use this to see what
    reference materials are available for a task template.

    Route: GET /tasks/templates/{task_id}/resources

    Path parameters:
        task_id (int): The unique identifier of the task template.

    Returns:
        List of task resource objects, each containing:
            - id (int): Unique resource identifier.
            - task_id (int): Parent task template identifier.
            - title (str): Resource name.
            - description (str | null): Resource description.
            - resource_type (str): Type of resource — one of "link", "code", "text", "file".
            - content (str): Resource content (URL, code snippet, text, or file path).
            - sort_order (int): Display order.
            - created_at (datetime): Creation timestamp.
            - updated_at (datetime | null): Last update timestamp.

    Errors:
        404 Not Found: Task template with the given task_id does not exist.
        403 Forbidden: Caller does not have access to this task's tenant.
        401 Unauthorized: Missing or invalid authentication token.
    """
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

    update_data = resource_data.model_dump(exclude_unset=True)
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
    """
    List all resources attached to a specific task group template.

    Returns links, code snippets, text blocks, or file references associated with
    the task group template. Resources are sorted by sort_order. Use this to see
    what reference materials are available for a task group.

    Route: GET /tasks/groups/templates/{group_id}/resources

    Path parameters:
        group_id (int): The unique identifier of the task group template.

    Returns:
        List of task group resource objects, each containing:
            - id (int): Unique resource identifier.
            - task_group_id (int): Parent task group template identifier.
            - title (str): Resource name.
            - description (str | null): Resource description.
            - resource_type (str): Type of resource — one of "link", "code", "text", "file".
            - content (str): Resource content (URL, code snippet, text, or file path).
            - sort_order (int): Display order.
            - created_at (datetime): Creation timestamp.
            - updated_at (datetime | null): Last update timestamp.

    Errors:
        404 Not Found: Task group template with the given group_id does not exist.
        403 Forbidden: Caller does not have access to this group's tenant.
        401 Unauthorized: Missing or invalid authentication token.
    """
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

    update_data = resource_data.model_dump(exclude_unset=True)
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
