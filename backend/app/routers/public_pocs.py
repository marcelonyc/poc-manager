"""Public POC router - for unauthenticated access via public links"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.models.poc import POC
from app.models.poc_public_link import POCPublicLink
from app.models.task import POCTask, POCTaskGroup, TaskGroup
from app.models.success_criteria import SuccessCriteria, TaskSuccessCriteria
from app.models.comment import Comment
from app.models.resource import Resource
from app.schemas.poc import POCDetail
from app.schemas.task import (
    POCTask as POCTaskSchema,
    POCTaskGroup as POCTaskGroupSchema,
)
from app.schemas.success_criteria import (
    SuccessCriteria as SuccessCriteriaSchema,
)


class GuestCommentCreate(BaseModel):
    """Schema for guest comment creation"""

    subject: str
    content: str
    guest_name: str
    guest_email: str
    poc_task_id: int = None
    poc_task_group_id: int = None

    def validate_task_or_taskgroup(self):
        """Validate that at least one task or task group is set"""
        if not self.poc_task_id and not self.poc_task_group_id:
            raise ValueError(
                "Comment must be associated with either a task (poc_task_id) or task group (poc_task_group_id)"
            )
        if self.poc_task_id and self.poc_task_group_id:
            raise ValueError(
                "Comment must be associated with either a task or task group, not both"
            )


router = APIRouter(prefix="/public/pocs", tags=["Public POCs"])


def get_public_poc_by_token(access_token: str, db: Session = Depends(get_db)):
    """Verify public link token and return the associated POC"""
    public_link = (
        db.query(POCPublicLink)
        .filter(
            POCPublicLink.access_token == access_token,
            POCPublicLink.is_deleted == False,
        )
        .first()
    )

    if not public_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired public link",
        )

    poc = db.query(POC).filter(POC.id == public_link.poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POC not found",
        )

    return poc


@router.get("/{access_token}", response_model=POCDetail)
def get_public_poc(
    access_token: str,
    poc: POC = Depends(get_public_poc_by_token),
    db: Session = Depends(get_db),
):
    """
    Get POC details via public sharing link.

    Public endpoint (no authentication required). Returns the full POC
    details for external stakeholders using the shared access token.

    Route: GET /public/pocs/{access_token}

    Path parameters:
        access_token (str): The public access token from the sharing URL.

    Returns:
        POC detail object containing:
            - id (int): Unique POC identifier.
            - title (str): POC title.
            - description (str | null): POC description.
            - tenant_id (int): Owning tenant.
            - customer_company_name (str | null): Customer organization.
            - status (str): Current POC status.
            - start_date (date | null): Planned start date.
            - end_date (date | null): Planned end date.
            - overall_success_score (float | null): Aggregate success metric.
            - participants (list): Participant summaries.
            - success_criteria_count (int): Number of success criteria.
            - tasks_count (int): Number of tasks.
            - task_groups_count (int): Number of task groups.

    Errors:
        404 Not Found: Invalid or expired access token.
    """
    # Participants (if any)
    participant_list = [
        {
            "id": p.id,
            "poc_id": p.poc_id,
            "user_id": p.user_id,
            "is_sales_engineer": p.is_sales_engineer,
            "is_customer": p.is_customer,
        }
        for p in (poc.participants or [])
    ]

    return POCDetail(
        id=poc.id,
        title=poc.title,
        description=poc.description,
        tenant_id=poc.tenant_id,
        created_by=poc.created_by,
        customer_company_name=poc.customer_company_name,
        customer_logo_url=poc.customer_logo_url,
        executive_summary=poc.executive_summary,
        objectives=poc.objectives,
        start_date=poc.start_date,
        end_date=poc.end_date,
        status=poc.status,
        overall_success_score=poc.overall_success_score,
        created_at=poc.created_at,
        updated_at=poc.updated_at,
        participants=participant_list,
        products=[],  # Products will be fetched separately if needed
        success_criteria_count=len(poc.success_criteria or []),
        tasks_count=len(poc.poc_tasks or []),
        task_groups_count=len(poc.poc_task_groups or []),
    )


@router.get("/{access_token}/tasks", response_model=List[POCTaskSchema])
def get_public_poc_tasks(
    access_token: str,
    poc: POC = Depends(get_public_poc_by_token),
    db: Session = Depends(get_db),
):
    """
    Get POC tasks via public sharing link.

    Public endpoint (no authentication required). Returns all tasks for
    the POC including assignee details and linked success criteria IDs.

    Route: GET /public/pocs/{access_token}/tasks

    Path parameters:
        access_token (str): The public access token from the sharing URL.

    Returns:
        List of POC task objects, each containing:
            - id (int): Unique POC task identifier.
            - poc_id (int): Parent POC identifier.
            - task_id (int | null): Source template reference.
            - title (str): Task name.
            - description (str | null): Task description.
            - status (str): One of "not_started", "in_progress", "completed", "blocked".
            - success_level (int | null): Numeric success rating.
            - sort_order (int): Display order.
            - created_at (datetime): Creation timestamp.
            - completed_at (datetime | null): Completion timestamp.
            - assignees (list): Assigned participants with id, name, email.
            - success_criteria_ids (list[int]): Linked success criteria IDs.

    Errors:
        404 Not Found: Invalid or expired access token.
    """
    # Get all tasks for this POC
    pocTasks = db.query(POCTask).filter(POCTask.poc_id == poc.id).all()

    # Populate success_criteria_ids for each task
    tasks_with_criteria = []
    for task in pocTasks:
        # Get success criteria IDs for this task
        task_criteria = (
            db.query(TaskSuccessCriteria)
            .filter(TaskSuccessCriteria.poc_task_id == task.id)
            .all()
        )

        success_criteria_ids = [tc.success_criteria_id for tc in task_criteria]

        # Construct response
        task_dict = {
            "id": task.id,
            "poc_id": task.poc_id,
            "title": task.title,
            "description": task.description,
            "task_id": task.task_id,
            "status": task.status,
            "sort_order": task.sort_order,
            "success_level": task.success_level,
            "created_at": task.created_at,
            "completed_at": task.completed_at,
            "success_criteria_ids": success_criteria_ids,
            "assignees": [
                {
                    "id": a.id,
                    "participant_id": a.participant_id,
                    "participant_email": a.participant_email,
                    "participant_name": a.participant_name,
                }
                for a in (task.assignees or [])
            ],
        }
        tasks_with_criteria.append(POCTaskSchema(**task_dict))

    return tasks_with_criteria


@router.get(
    "/{access_token}/task-groups", response_model=List[POCTaskGroupSchema]
)
def get_public_poc_task_groups(
    access_token: str,
    poc: POC = Depends(get_public_poc_by_token),
    db: Session = Depends(get_db),
):
    """
    Get POC task groups via public sharing link.

    Public endpoint (no authentication required). Returns all task groups
    for the POC including nested tasks, assignees, and linked success criteria.

    Route: GET /public/pocs/{access_token}/task-groups

    Path parameters:
        access_token (str): The public access token from the sharing URL.

    Returns:
        List of POC task group objects, each containing:
            - id (int): Unique group identifier.
            - poc_id (int): Parent POC identifier.
            - task_group_id (int | null): Source template reference.
            - title (str): Group name.
            - description (str | null): Group description.
            - status (str): One of "not_started", "in_progress", "completed", "blocked".
            - success_level (int | null): Numeric success rating.
            - sort_order (int): Display order.
            - created_at (datetime): Creation timestamp.
            - completed_at (datetime | null): Completion timestamp.
            - success_criteria_ids (list[int]): Linked success criteria IDs.
            - tasks (list): Nested POC tasks with full details.

    Errors:
        404 Not Found: Invalid or expired access token.
    """
    # Get all task groups for this POC
    pocTaskGroups = (
        db.query(POCTaskGroup).filter(POCTaskGroup.poc_id == poc.id).all()
    )

    groups_with_data = []
    for group in pocTaskGroups:
        # Get success criteria IDs for the group
        group_criteria = (
            db.query(TaskSuccessCriteria)
            .filter(TaskSuccessCriteria.poc_task_group_id == group.id)
            .all()
        )
        group_success_criteria_ids = [
            gc.success_criteria_id for gc in group_criteria
        ]

        # Get tasks for this group (through the template if it exists)
        tasks_with_criteria = []
        if group.task_group_id:
            # Get the template task group
            task_group = (
                db.query(TaskGroup)
                .filter(TaskGroup.id == group.task_group_id)
                .first()
            )
            if task_group and task_group.tasks:
                template_task_ids = [t.id for t in task_group.tasks]
                # Find POC tasks that correspond to these template tasks
                tasks = (
                    db.query(POCTask)
                    .filter(
                        POCTask.poc_id == poc.id,
                        POCTask.task_id.in_(template_task_ids),
                    )
                    .order_by(POCTask.sort_order)
                    .all()
                )

                for task in tasks:
                    task_criteria = (
                        db.query(TaskSuccessCriteria)
                        .filter(TaskSuccessCriteria.poc_task_id == task.id)
                        .all()
                    )
                    success_criteria_ids = [
                        tc.success_criteria_id for tc in task_criteria
                    ]

                    task_dict = {
                        "id": task.id,
                        "poc_id": task.poc_id,
                        "title": task.title,
                        "description": task.description,
                        "task_id": task.task_id,
                        "status": task.status,
                        "sort_order": task.sort_order,
                        "success_level": task.success_level,
                        "created_at": task.created_at,
                        "completed_at": task.completed_at,
                        "success_criteria_ids": success_criteria_ids,
                        "assignees": [
                            {
                                "id": a.id,
                                "participant_id": a.participant_id,
                                "participant_email": a.participant_email,
                                "participant_name": a.participant_name,
                            }
                            for a in (task.assignees or [])
                        ],
                    }
                    tasks_with_criteria.append(POCTaskSchema(**task_dict))

        group_dict = {
            "id": group.id,
            "poc_id": group.poc_id,
            "title": group.title,
            "description": group.description,
            "task_group_id": group.task_group_id,
            "status": group.status,
            "sort_order": group.sort_order,
            "success_level": group.success_level,
            "created_at": group.created_at,
            "completed_at": group.completed_at,
            "success_criteria_ids": group_success_criteria_ids,
            "tasks": tasks_with_criteria,
        }
        groups_with_data.append(POCTaskGroupSchema(**group_dict))

    return groups_with_data


@router.get("/{access_token}/success-criteria")
def get_public_poc_success_criteria(
    access_token: str,
    poc: POC = Depends(get_public_poc_by_token),
    db: Session = Depends(get_db),
):
    """
    Get POC success criteria via public sharing link.

    Public endpoint (no authentication required). Returns all success criteria
    for the POC, sorted by sort_order.

    Route: GET /public/pocs/{access_token}/success-criteria

    Path parameters:
        access_token (str): The public access token from the sharing URL.

    Returns:
        List of success criteria objects, each containing:
            - id (int): Unique criteria identifier.
            - poc_id (int): Parent POC identifier.
            - title (str): Criteria name.
            - description (str | null): Criteria description.
            - target_value (str | null): Expected target or threshold.
            - sort_order (int): Display order.
            - created_at (datetime): Creation timestamp.
            - updated_at (datetime | null): Last update timestamp.

    Errors:
        404 Not Found: Invalid or expired access token.
    """
    criteria = (
        db.query(SuccessCriteria)
        .filter(SuccessCriteria.poc_id == poc.id)
        .order_by(SuccessCriteria.sort_order)
        .all()
    )
    return [
        {
            "id": c.id,
            "poc_id": c.poc_id,
            "title": c.title,
            "description": c.description,
            "target_value": c.target_value,
            "sort_order": c.sort_order,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        }
        for c in criteria
    ]


@router.get("/{access_token}/comments")
def get_public_poc_comments(
    access_token: str,
    poc_task_id: int = None,
    poc_task_group_id: int = None,
    poc: POC = Depends(get_public_poc_by_token),
    db: Session = Depends(get_db),
):
    """
    Get POC comments via public sharing link (excludes internal comments).

    Public endpoint (no authentication required). Returns non-internal
    comments filtered by either task or task group. Exactly one filter
    must be provided.

    Route: GET /public/pocs/{access_token}/comments?poc_task_id=&poc_task_group_id=

    Path parameters:
        access_token (str): The public access token from the sharing URL.

    Query parameters:
        poc_task_id (int, optional): Filter by task ID. Mutually exclusive with poc_task_group_id.
        poc_task_group_id (int, optional): Filter by task group ID. Mutually exclusive with poc_task_id.

    Returns:
        List of comment objects, each containing:
            - id (int): Unique comment identifier.
            - subject (str): Comment subject.
            - content (str): Comment body text.
            - user_id (int | null): Author user ID (null for guests).
            - poc_id (int): Parent POC identifier.
            - poc_task_id (int | null): Associated task ID.
            - poc_task_group_id (int | null): Associated task group ID.
            - is_internal (bool): Always false for public access.
            - created_at (datetime): Creation timestamp.
            - updated_at (datetime | null): Last edit timestamp.
            - guest_name (str | null): Guest commenter name.
            - guest_email (str | null): Guest commenter email.
            - user (object): Author info with id, email, full_name.

    Errors:
        400 Bad Request: Neither or both filter parameters provided.
        404 Not Found: Invalid token, or task/group not found in this POC.
    """
    # Validate that at least one filter is specified
    if not poc_task_id and not poc_task_group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comments must be filtered by either poc_task_id or poc_task_group_id",
        )

    if poc_task_id and poc_task_group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filter by either a task or task group, not both",
        )

    query = db.query(Comment).filter(
        Comment.poc_id == poc.id,
        Comment.is_internal
        == False,  # Hide internal comments from public access
    )

    if poc_task_id:
        # Verify task exists and belongs to this POC
        task = (
            db.query(POCTask)
            .filter(POCTask.id == poc_task_id, POCTask.poc_id == poc.id)
            .first()
        )
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found in this POC",
            )
        query = query.filter(Comment.poc_task_id == poc_task_id)
    else:  # poc_task_group_id
        # Verify task group exists and belongs to this POC
        task_group = (
            db.query(POCTaskGroup)
            .filter(
                POCTaskGroup.id == poc_task_group_id,
                POCTaskGroup.poc_id == poc.id,
            )
            .first()
        )
        if not task_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task group not found in this POC",
            )
        query = query.filter(Comment.poc_task_group_id == poc_task_group_id)

    comments = query.order_by(Comment.created_at.desc()).all()

    result = []
    for comment in comments:
        comment_dict = {
            "id": comment.id,
            "subject": comment.subject,
            "content": comment.content,
            "user_id": comment.user_id,
            "poc_id": comment.poc_id,
            "poc_task_id": comment.poc_task_id,
            "poc_task_group_id": comment.poc_task_group_id,
            "is_internal": comment.is_internal,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
            "guest_name": comment.guest_name,
            "guest_email": comment.guest_email,
        }

        # Add user info if comment is from authenticated user
        if comment.user:
            comment_dict["user"] = {
                "id": comment.user.id,
                "email": comment.user.email,
                "full_name": comment.user.full_name,
            }
        else:
            # Guest comment
            comment_dict["user"] = {
                "id": None,
                "email": comment.guest_email,
                "full_name": comment.guest_name,
            }

        result.append(comment_dict)

    return result


@router.post("/{access_token}/comments", status_code=status.HTTP_201_CREATED)
def create_public_comment(
    access_token: str,
    comment_data: GuestCommentCreate,
    poc: POC = Depends(get_public_poc_by_token),
    db: Session = Depends(get_db),
):
    """Create a guest comment on a public POC task or task group"""
    # Validate that at least one task or task group is specified
    if not comment_data.poc_task_id and not comment_data.poc_task_group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment must be associated with either a task (poc_task_id) or task group (poc_task_group_id)",
        )

    if comment_data.poc_task_id and comment_data.poc_task_group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment must be associated with either a task or task group, not both",
        )

    # Validate input
    if not comment_data.subject.strip() or not comment_data.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subject and content are required",
        )

    if len(comment_data.content) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content must be 1000 characters or less",
        )

    # Validate task or task group exists and belongs to this POC
    if comment_data.poc_task_id:
        task = (
            db.query(POCTask)
            .filter(
                POCTask.id == comment_data.poc_task_id,
                POCTask.poc_id == poc.id,
            )
            .first()
        )
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found in this POC",
            )
    elif comment_data.poc_task_group_id:
        task_group = (
            db.query(POCTaskGroup)
            .filter(
                POCTaskGroup.id == comment_data.poc_task_group_id,
                POCTaskGroup.poc_id == poc.id,
            )
            .first()
        )
        if not task_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task group not found in this POC",
            )

    comment = Comment(
        subject=comment_data.subject,
        content=comment_data.content,
        poc_id=poc.id,
        poc_task_id=comment_data.poc_task_id,
        poc_task_group_id=comment_data.poc_task_group_id,
        is_internal=False,  # Public comments are never internal
        guest_name=comment_data.guest_name,
        guest_email=comment_data.guest_email,
        user_id=None,  # No authenticated user for public comments
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {
        "id": comment.id,
        "subject": comment.subject,
        "content": comment.content,
        "user_id": comment.user_id,
        "poc_id": comment.poc_id,
        "poc_task_id": comment.poc_task_id,
        "poc_task_group_id": comment.poc_task_group_id,
        "is_internal": comment.is_internal,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at,
        "guest_name": comment.guest_name,
        "guest_email": comment.guest_email,
        "user": {
            "id": None,
            "email": comment.guest_email,
            "full_name": comment.guest_name,
        },
    }


@router.get("/{access_token}/tasks/{task_id}/resources")
def get_public_task_resources(
    access_token: str,
    task_id: int,
    poc: POC = Depends(get_public_poc_by_token),
    db: Session = Depends(get_db),
):
    """
    Get resources for a POC task via public sharing link.

    Public endpoint (no authentication required). Returns all resources
    attached to a specific task, sorted by sort_order.

    Route: GET /public/pocs/{access_token}/tasks/{task_id}/resources

    Path parameters:
        access_token (str): The public access token from the sharing URL.
        task_id (int): The unique identifier of the POC task.

    Returns:
        List of resource objects, each containing:
            - id (int): Unique resource identifier.
            - title (str): Resource name.
            - description (str | null): Resource description.
            - resource_type (str): Type — one of "link", "code", "text", "file".
            - content (str): Resource content.
            - sort_order (int): Display order.
            - created_at (datetime): Creation timestamp.
            - updated_at (datetime | null): Last update timestamp.

    Errors:
        404 Not Found: Invalid token or task not found in this POC.
    """
    # Verify task exists and belongs to this POC
    task = (
        db.query(POCTask)
        .filter(POCTask.id == task_id, POCTask.poc_id == poc.id)
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in this POC",
        )

    resources = (
        db.query(Resource)
        .filter(Resource.poc_task_id == task_id)
        .order_by(Resource.sort_order)
        .all()
    )

    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "resource_type": r.resource_type.value,
            "content": r.content,
            "sort_order": r.sort_order,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }
        for r in resources
    ]


@router.get("/{access_token}/task-groups/{group_id}/resources")
def get_public_task_group_resources(
    access_token: str,
    group_id: int,
    poc: POC = Depends(get_public_poc_by_token),
    db: Session = Depends(get_db),
):
    """
    Get resources for a POC task group via public sharing link.

    Public endpoint (no authentication required). Returns all resources
    attached to a specific task group, sorted by sort_order.

    Route: GET /public/pocs/{access_token}/task-groups/{group_id}/resources

    Path parameters:
        access_token (str): The public access token from the sharing URL.
        group_id (int): The unique identifier of the POC task group.

    Returns:
        List of resource objects, each containing:
            - id (int): Unique resource identifier.
            - title (str): Resource name.
            - description (str | null): Resource description.
            - resource_type (str): Type — one of "link", "code", "text", "file".
            - content (str): Resource content.
            - sort_order (int): Display order.
            - created_at (datetime): Creation timestamp.
            - updated_at (datetime | null): Last update timestamp.

    Errors:
        404 Not Found: Invalid token or task group not found in this POC.
    """
    # Verify task group exists and belongs to this POC
    task_group = (
        db.query(POCTaskGroup)
        .filter(POCTaskGroup.id == group_id, POCTaskGroup.poc_id == poc.id)
        .first()
    )
    if not task_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task group not found in this POC",
        )

    resources = (
        db.query(Resource)
        .filter(Resource.poc_task_group_id == group_id)
        .order_by(Resource.sort_order)
        .all()
    )

    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "resource_type": r.resource_type.value,
            "content": r.content,
            "sort_order": r.sort_order,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }
        for r in resources
    ]
