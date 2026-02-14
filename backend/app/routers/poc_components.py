"""Success criteria, comments, and resources router"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime, timezone
from app.database import get_db
from app.models.user import User, UserRole
from app.models.poc import POC
from app.models.task import POCTask, POCTaskGroup
from app.models.poc_invitation import POCInvitation, POCInvitationStatus
from app.models.success_criteria import SuccessCriteria
from app.models.comment import Comment
from app.models.resource import Resource
from app.utils.demo_limits import check_demo_resource_limit
from app.schemas.success_criteria import (
    SuccessCriteriaCreate,
    SuccessCriteriaUpdate,
    SuccessCriteria as SuccessCriteriaSchema,
)
from app.schemas.other import (
    CommentCreate,
    CommentUpdate,
    Comment as CommentSchema,
    ResourceCreate,
    ResourceUpdate,
    Resource as ResourceSchema,
)
from app.auth import (
    require_sales_engineer,
    get_current_user,
    check_tenant_access,
    get_current_tenant_id,
)


router = APIRouter(tags=["POC Components"])


# Success Criteria
@router.post(
    "/pocs/{poc_id}/success-criteria",
    response_model=SuccessCriteriaSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_success_criteria(
    poc_id: int,
    criteria_data: SuccessCriteriaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """Create success criteria for a POC"""
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="POC not found"
        )

    if not check_tenant_access(current_user, poc.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    criteria = SuccessCriteria(
        poc_id=poc_id,
        title=criteria_data.title,
        description=criteria_data.description,
        target_value=criteria_data.target_value,
        sort_order=criteria_data.sort_order,
    )
    db.add(criteria)
    db.commit()
    db.refresh(criteria)
    return criteria


@router.get(
    "/pocs/{poc_id}/success-criteria",
    response_model=List[SuccessCriteriaSchema],
)
def list_success_criteria(
    poc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all success criteria for a POC.

    Returns the defined success criteria for a POC, sorted by sort_order.
    Success criteria define the measurable goals that determine POC success.

    Route: GET /pocs/{poc_id}/success-criteria

    Path parameters:
        poc_id (int): The unique identifier of the POC.

    Returns:
        List of success criteria objects, each containing:
            - id (int): Unique criteria identifier.
            - poc_id (int): Parent POC identifier.
            - title (str): Criteria name.
            - description (str | null): Detailed criteria description.
            - target_value (str | null): Expected target or threshold.
            - sort_order (int): Display order.
            - created_at (datetime): Creation timestamp.
            - updated_at (datetime | null): Last update timestamp.

    Errors:
        401 Unauthorized: Missing or invalid authentication token.
    """
    criteria = (
        db.query(SuccessCriteria)
        .filter(SuccessCriteria.poc_id == poc_id)
        .order_by(SuccessCriteria.sort_order)
        .all()
    )
    return criteria


@router.put(
    "/pocs/{poc_id}/success-criteria/{criteria_id}",
    response_model=SuccessCriteriaSchema,
)
def update_success_criteria(
    poc_id: int,
    criteria_id: int,
    criteria_data: SuccessCriteriaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update success criteria"""
    criteria = (
        db.query(SuccessCriteria)
        .filter(
            SuccessCriteria.id == criteria_id, SuccessCriteria.poc_id == poc_id
        )
        .first()
    )
    if not criteria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Success criteria not found",
        )

    update_data = criteria_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(criteria, field, value)

    db.commit()
    db.refresh(criteria)
    return criteria


@router.delete("/pocs/{poc_id}/success-criteria/{criteria_id}")
def delete_success_criteria(
    poc_id: int,
    criteria_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """Delete success criteria"""
    criteria = (
        db.query(SuccessCriteria)
        .filter(
            SuccessCriteria.id == criteria_id, SuccessCriteria.poc_id == poc_id
        )
        .first()
    )
    if not criteria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Success criteria not found",
        )

    db.delete(criteria)
    db.commit()
    return {"message": "Success criteria deleted successfully"}


# Comments
@router.post(
    "/pocs/{poc_id}/comments",
    response_model=CommentSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    poc_id: int,
    comment_data: CommentCreate,
    task_id: int = None,
    task_group_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a comment on a POC task or task group"""
    # Validate that at least one task or task group is specified
    if not task_id and not task_group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment must be associated with either a task (task_id) or task group (task_group_id)",
        )

    if task_id and task_group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment must be associated with either a task or task group, not both",
        )

    # Verify POC exists
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="POC not found"
        )

    # Validate task or task group exists and belongs to this POC
    if task_id:
        task = (
            db.query(POCTask)
            .filter(POCTask.id == task_id, POCTask.poc_id == poc_id)
            .first()
        )
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found in this POC",
            )
    elif task_group_id:
        task_group = (
            db.query(POCTaskGroup)
            .filter(
                POCTaskGroup.id == task_group_id, POCTaskGroup.poc_id == poc_id
            )
            .first()
        )
        if not task_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task group not found in this POC",
            )

    # Customers cannot create internal comments
    if current_user.role == UserRole.CUSTOMER and comment_data.is_internal:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customers cannot create internal comments",
        )

    comment = Comment(
        subject=comment_data.subject,
        content=comment_data.content,
        user_id=current_user.id,
        poc_id=poc_id,
        poc_task_id=task_id,
        poc_task_group_id=task_group_id,
        is_internal=comment_data.is_internal,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Add user info to response
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
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
        },
    }
    return comment_dict


@router.get("/pocs/{poc_id}/comments", response_model=List[CommentSchema])
def list_comments(
    poc_id: int,
    task_id: int = None,
    task_group_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List comments for a POC task or task group.

    Returns comments filtered by either task_id or task_group_id (exactly one
    must be provided). Internal comments are automatically hidden from customer
    users. Results are sorted by creation date (newest first) and include
    author details.

    Route: GET /pocs/{poc_id}/comments?task_id=&task_group_id=

    Path parameters:
        poc_id (int): The unique identifier of the POC.

    Query parameters:
        task_id (int, optional): Filter by POC task ID. Mutually exclusive with task_group_id.
        task_group_id (int, optional): Filter by POC task group ID. Mutually exclusive with task_id.

    Returns:
        List of comment objects, each containing:
            - id (int): Unique comment identifier.
            - subject (str): Comment subject line.
            - content (str): Comment body text.
            - user_id (int | null): Author user ID (null for guest comments).
            - poc_id (int): Parent POC identifier.
            - poc_task_id (int | null): Associated task ID.
            - poc_task_group_id (int | null): Associated task group ID.
            - is_internal (bool): Whether this is a vendor-only internal comment.
            - created_at (datetime): Creation timestamp.
            - updated_at (datetime | null): Last edit timestamp.
            - guest_name (str | null): Guest commenter name.
            - guest_email (str | null): Guest commenter email.
            - user (object): Author info with id, email, and full_name.

    Errors:
        400 Bad Request: Neither or both task_id and task_group_id provided.
        404 Not Found: POC, task, or task group not found.
        401 Unauthorized: Missing or invalid authentication token.
    """
    # Validate that at least one task or task group is specified
    if not task_id and not task_group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comments must be filtered by either task_id or task_group_id",
        )

    if task_id and task_group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filter by either a task or task group, not both",
        )

    # Verify POC exists
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="POC not found"
        )

    # Build query for comments
    query = db.query(Comment).filter(Comment.poc_id == poc_id)

    if task_id:
        # Verify task exists and belongs to this POC
        task = (
            db.query(POCTask)
            .filter(POCTask.id == task_id, POCTask.poc_id == poc_id)
            .first()
        )
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found in this POC",
            )
        query = query.filter(Comment.poc_task_id == task_id)
    else:  # task_group_id
        # Verify task group exists and belongs to this POC
        task_group = (
            db.query(POCTaskGroup)
            .filter(
                POCTaskGroup.id == task_group_id, POCTaskGroup.poc_id == poc_id
            )
            .first()
        )
        if not task_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task group not found in this POC",
            )
        query = query.filter(Comment.poc_task_group_id == task_group_id)

    # Hide internal comments from customers
    if current_user.role == UserRole.CUSTOMER:
        query = query.filter(Comment.is_internal == False)

    comments = query.order_by(Comment.created_at.desc()).all()

    # Add user info to each comment
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


@router.put(
    "/pocs/{poc_id}/comments/{comment_id}", response_model=CommentSchema
)
def update_comment(
    poc_id: int,
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a comment"""
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.poc_id == poc_id)
        .first()
    )
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    # Only comment author can update
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    update_data = comment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comment, field, value)

    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/pocs/{poc_id}/comments/{comment_id}")
def delete_comment(
    poc_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a comment"""
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.poc_id == poc_id)
        .first()
    )
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    # Only comment author can delete
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully"}


# Resources
@router.post(
    "/pocs/{poc_id}/resources",
    response_model=ResourceSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_resource(
    poc_id: int,
    resource_data: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Create a resource for a POC"""
    # Check demo resource limit
    check_demo_resource_limit(db, tenant_id, current_user.tenant)

    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="POC not found"
        )

    if not check_tenant_access(current_user, poc.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    resource = Resource(
        poc_id=poc_id,
        title=resource_data.title,
        description=resource_data.description,
        resource_type=resource_data.resource_type,
        content=resource_data.content,
        success_criteria_id=resource_data.success_criteria_id,
        sort_order=resource_data.sort_order,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.get("/pocs/{poc_id}/resources", response_model=List[ResourceSchema])
def list_resources(
    poc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all resources attached to a POC.

    Returns POC-level resources (links, code snippets, text blocks, or files)
    sorted by sort_order. These are resources associated with the POC itself,
    not with individual tasks or task groups.

    Route: GET /pocs/{poc_id}/resources

    Path parameters:
        poc_id (int): The unique identifier of the POC.

    Returns:
        List of resource objects, each containing:
            - id (int): Unique resource identifier.
            - poc_id (int): Parent POC identifier.
            - title (str): Resource name.
            - description (str | null): Resource description.
            - resource_type (str): Type — one of "link", "code", "text", "file".
            - content (str): Resource content (URL, snippet, text, or file path).
            - success_criteria_id (int | null): Linked success criteria, if any.
            - sort_order (int): Display order.
            - created_at (datetime): Creation timestamp.
            - updated_at (datetime | null): Last update timestamp.

    Errors:
        401 Unauthorized: Missing or invalid authentication token.
    """
    resources = (
        db.query(Resource)
        .filter(Resource.poc_id == poc_id)
        .order_by(Resource.sort_order)
        .all()
    )
    return resources


@router.put(
    "/pocs/{poc_id}/resources/{resource_id}", response_model=ResourceSchema
)
def update_resource(
    poc_id: int,
    resource_id: int,
    resource_data: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """Update a resource"""
    resource = (
        db.query(Resource)
        .filter(Resource.id == resource_id, Resource.poc_id == poc_id)
        .first()
    )
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    update_data = resource_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)

    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/pocs/{poc_id}/resources/{resource_id}")
def delete_resource(
    poc_id: int,
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """Delete a resource"""
    resource = (
        db.query(Resource)
        .filter(Resource.id == resource_id, Resource.poc_id == poc_id)
        .first()
    )
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    db.delete(resource)
    db.commit()
    return {"message": "Resource deleted successfully"}


# Task Resources
@router.post(
    "/pocs/{poc_id}/tasks/{task_id}/resources",
    response_model=ResourceSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_task_resource(
    poc_id: int,
    task_id: int,
    resource_data: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Create a resource for a POC task"""
    # Check demo resource limit
    check_demo_resource_limit(db, tenant_id, current_user.tenant)

    task = (
        db.query(POCTask)
        .filter(POCTask.id == task_id, POCTask.poc_id == poc_id)
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    # Verify tenant access via POC
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not check_tenant_access(current_user, poc.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    resource = Resource(
        poc_task_id=task_id,
        title=resource_data.title,
        description=resource_data.description,
        resource_type=resource_data.resource_type,
        content=resource_data.content,
        success_criteria_id=resource_data.success_criteria_id,
        sort_order=resource_data.sort_order,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.get(
    "/pocs/{poc_id}/tasks/{task_id}/resources",
    response_model=List[ResourceSchema],
)
def list_task_resources(
    poc_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List resources attached to a specific POC task.

    Returns resources (links, code, text, files) associated with a particular
    task within a POC, sorted by sort_order.

    Route: GET /pocs/{poc_id}/tasks/{task_id}/resources

    Path parameters:
        poc_id (int): The unique identifier of the POC.
        task_id (int): The unique identifier of the POC task.

    Returns:
        List of resource objects, each containing:
            - id (int): Unique resource identifier.
            - poc_task_id (int): Parent task identifier.
            - title (str): Resource name.
            - description (str | null): Resource description.
            - resource_type (str): Type — one of "link", "code", "text", "file".
            - content (str): Resource content.
            - success_criteria_id (int | null): Linked success criteria, if any.
            - sort_order (int): Display order.
            - created_at (datetime): Creation timestamp.
            - updated_at (datetime | null): Last update timestamp.

    Errors:
        401 Unauthorized: Missing or invalid authentication token.
    """
    resources = (
        db.query(Resource)
        .filter(Resource.poc_task_id == task_id)
        .order_by(Resource.sort_order)
        .all()
    )
    return resources


@router.put(
    "/pocs/{poc_id}/tasks/{task_id}/resources/{resource_id}",
    response_model=ResourceSchema,
)
def update_task_resource(
    poc_id: int,
    task_id: int,
    resource_id: int,
    resource_data: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """Update a task resource"""
    resource = (
        db.query(Resource)
        .filter(Resource.id == resource_id, Resource.poc_task_id == task_id)
        .first()
    )
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    update_data = resource_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)

    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/pocs/{poc_id}/tasks/{task_id}/resources/{resource_id}")
def delete_task_resource(
    poc_id: int,
    task_id: int,
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """Delete a task resource"""
    resource = (
        db.query(Resource)
        .filter(Resource.id == resource_id, Resource.poc_task_id == task_id)
        .first()
    )
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    db.delete(resource)
    db.commit()
    return {"message": "Resource deleted successfully"}


# Task Group Resources
@router.post(
    "/pocs/{poc_id}/task-groups/{group_id}/resources",
    response_model=ResourceSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_task_group_resource(
    poc_id: int,
    group_id: int,
    resource_data: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Create a resource for a POC task group"""
    # Check demo resource limit
    check_demo_resource_limit(db, tenant_id, current_user.tenant)

    task_group = (
        db.query(POCTaskGroup)
        .filter(POCTaskGroup.id == group_id, POCTaskGroup.poc_id == poc_id)
        .first()
    )
    if not task_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task group not found",
        )

    # Verify tenant access via POC
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not check_tenant_access(current_user, poc.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    resource = Resource(
        poc_task_group_id=group_id,
        title=resource_data.title,
        description=resource_data.description,
        resource_type=resource_data.resource_type,
        content=resource_data.content,
        success_criteria_id=resource_data.success_criteria_id,
        sort_order=resource_data.sort_order,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.get(
    "/pocs/{poc_id}/task-groups/{group_id}/resources",
    response_model=List[ResourceSchema],
)
def list_task_group_resources(
    poc_id: int,
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List resources attached to a specific POC task group.

    Returns resources (links, code, text, files) associated with a particular
    task group within a POC, sorted by sort_order.

    Route: GET /pocs/{poc_id}/task-groups/{group_id}/resources

    Path parameters:
        poc_id (int): The unique identifier of the POC.
        group_id (int): The unique identifier of the POC task group.

    Returns:
        List of resource objects, each containing:
            - id (int): Unique resource identifier.
            - poc_task_group_id (int): Parent task group identifier.
            - title (str): Resource name.
            - description (str | null): Resource description.
            - resource_type (str): Type — one of "link", "code", "text", "file".
            - content (str): Resource content.
            - success_criteria_id (int | null): Linked success criteria, if any.
            - sort_order (int): Display order.
            - created_at (datetime): Creation timestamp.
            - updated_at (datetime | null): Last update timestamp.

    Errors:
        401 Unauthorized: Missing or invalid authentication token.
    """
    resources = (
        db.query(Resource)
        .filter(Resource.poc_task_group_id == group_id)
        .order_by(Resource.sort_order)
        .all()
    )
    return resources


@router.put(
    "/pocs/{poc_id}/task-groups/{group_id}/resources/{resource_id}",
    response_model=ResourceSchema,
)
def update_task_group_resource(
    poc_id: int,
    group_id: int,
    resource_id: int,
    resource_data: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """Update a task group resource"""
    resource = (
        db.query(Resource)
        .filter(
            Resource.id == resource_id, Resource.poc_task_group_id == group_id
        )
        .first()
    )
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    update_data = resource_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)

    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/pocs/{poc_id}/task-groups/{group_id}/resources/{resource_id}")
def delete_task_group_resource(
    poc_id: int,
    group_id: int,
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """Delete a task group resource"""
    resource = (
        db.query(Resource)
        .filter(
            Resource.id == resource_id, Resource.poc_task_group_id == group_id
        )
        .first()
    )
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    db.delete(resource)
    db.commit()
    return {"message": "Resource deleted successfully"}


# Participants
@router.get("/pocs/{poc_id}/participants")
def list_participants(
    poc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all participants and pending invitations for a POC.

    Returns both accepted participants and outstanding invitations (pending,
    expired, failed) in a single list. This gives a unified view of everyone
    involved or invited to the POC engagement.

    Route: GET /pocs/{poc_id}/participants

    Path parameters:
        poc_id (int): The unique identifier of the POC.

    Returns:
        List of participant/invitation objects, each containing:
            - id (int | null): Participant record ID (null for pending invitations).
            - user_id (int | null): User ID (null for pending invitations).
            - email (str): Participant or invitee email.
            - full_name (str): Participant or invitee name.
            - is_sales_engineer (bool): Whether participant is a sales engineer.
            - is_customer (bool): Whether participant is a customer.
            - joined_at (datetime | null): When the participant joined (null for invitations).
            - status (str): One of "accepted", "pending", "expired", "failed".
            - invitation_id (int | null): Invitation ID for pending invitations.
            - invited_at (datetime, optional): When the invitation was sent.
            - expires_at (datetime, optional): Invitation expiration time.
            - resend_count (int, optional): Number of times invitation was resent.

    Errors:
        401 Unauthorized: Missing or invalid authentication token.
    """
    from app.models.poc import POCParticipant

    # Get existing participants
    participants = (
        db.query(POCParticipant).filter(POCParticipant.poc_id == poc_id).all()
    )

    # Get pending/expired invitations
    invitations = (
        db.query(POCInvitation)
        .filter(
            POCInvitation.poc_id == poc_id,
            POCInvitation.status.in_(
                [
                    POCInvitationStatus.PENDING,
                    POCInvitationStatus.EXPIRED,
                    POCInvitationStatus.FAILED,
                ]
            ),
        )
        .all()
    )

    # Format participants
    result = []
    for p in participants:
        result.append(
            {
                "id": p.id,
                "user_id": p.user_id,
                "email": p.user.email,
                "full_name": p.user.full_name,
                "is_sales_engineer": p.is_sales_engineer,
                "is_customer": p.is_customer,
                "joined_at": p.joined_at,
                "status": "accepted",
                "invitation_id": None,
            }
        )

    # Format pending invitations
    for inv in invitations:
        # Check if invitation is expired
        is_expired = (
            inv.expires_at < datetime.now(timezone.utc)
            if inv.status == POCInvitationStatus.PENDING
            else inv.status == POCInvitationStatus.EXPIRED
        )

        result.append(
            {
                "id": None,
                "user_id": None,
                "email": inv.email,
                "full_name": inv.full_name,
                "is_sales_engineer": not inv.is_customer,
                "is_customer": inv.is_customer,
                "joined_at": None,
                "status": "expired" if is_expired else inv.status.value,
                "invitation_id": inv.id,
                "invited_at": inv.created_at,
                "expires_at": inv.expires_at,
                "resend_count": inv.resend_count,
            }
        )

    return result
