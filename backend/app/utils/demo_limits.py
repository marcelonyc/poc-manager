"""Demo account limit utilities"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.poc import POC
from app.models.task import Task, TaskGroup
from app.models.resource import Resource


class DemoLimitException(HTTPException):
    """Exception raised when demo account hits a limit"""
    def __init__(self, limit_type: str, limit: int):
        detail = f"Demo account limit reached: Maximum {limit} {limit_type} allowed. " \
                 f"Upgrade to a full account to remove limits."
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


def check_demo_poc_limit(db: Session, tenant_id: int, tenant):
    """Check if demo account can create more POCs"""
    if not tenant or not tenant.is_demo:
        return
    
    poc_count = db.query(POC).filter(POC.tenant_id == tenant_id).count()
    if poc_count >= 2:
        raise DemoLimitException("POCs", 2)


def check_demo_task_limit(db: Session, tenant_id: int, tenant):
    """Check if demo account can create more tasks"""
    if not tenant or not tenant.is_demo:
        return
    
    task_count = db.query(Task).filter(Task.tenant_id == tenant_id).count()
    if task_count >= 20:
        raise DemoLimitException("tasks", 20)


def check_demo_task_group_limit(db: Session, tenant_id: int, tenant):
    """Check if demo account can create more task groups"""
    if not tenant or not tenant.is_demo:
        return
    
    task_group_count = db.query(TaskGroup).filter(TaskGroup.tenant_id == tenant_id).count()
    if task_group_count >= 20:
        raise DemoLimitException("task groups", 20)


def check_demo_resource_limit(db: Session, tenant_id: int, tenant):
    """Check if demo account can upload more resources"""
    if not tenant or not tenant.is_demo:
        return
    
    # Count resources through their parent POCs (since resources don't have tenant_id directly)
    resource_count = db.query(Resource).join(
        POC, Resource.poc_id == POC.id
    ).filter(POC.tenant_id == tenant_id).count()
    if resource_count >= 10:
        raise DemoLimitException("resources/uploads", 10)


def get_demo_limits_info(db: Session, tenant_id: int, tenant) -> dict:
    """Get current usage and limits for demo account"""
    if not tenant or not tenant.is_demo:
        return {
            "is_demo": False,
            "limits": None
        }
    
    poc_count = db.query(POC).filter(POC.tenant_id == tenant_id).count()
    task_count = db.query(Task).filter(Task.tenant_id == tenant_id).count()
    task_group_count = db.query(TaskGroup).filter(TaskGroup.tenant_id == tenant_id).count()
    
    # Count resources through their parent POCs (since resources don't have tenant_id directly)
    resource_count = db.query(Resource).join(
        POC, Resource.poc_id == POC.id
    ).filter(POC.tenant_id == tenant_id).count()
    
    return {
        "is_demo": True,
        "limits": {
            "pocs": {"used": poc_count, "max": 2, "remaining": max(0, 2 - poc_count)},
            "tasks": {"used": task_count, "max": 20, "remaining": max(0, 20 - task_count)},
            "task_groups": {"used": task_group_count, "max": 20, "remaining": max(0, 20 - task_group_count)},
            "resources": {"used": resource_count, "max": 10, "remaining": max(0, 10 - resource_count)},
        }
    }
