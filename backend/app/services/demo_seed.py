"""Dummy data seeding service for demo accounts"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.models.user import User, UserRole
from app.models.user_tenant_role import UserTenantRole
from app.models.task import Task, TaskGroup, POCTask, POCTaskGroup, TaskStatus
from app.models.poc import POC, POCStatus, POCParticipant
from app.models.success_criteria import SuccessCriteria, TaskSuccessCriteria
from app.models.product import Product
from app.auth import get_password_hash


def _create_demo_user(db, email, full_name, role, tenant_id):
    """Create a demo user with its corresponding UserTenantRole."""
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash("demo1234"),
        role=role,
        tenant_id=tenant_id,
        is_active=True,
        is_demo=True,
    )
    db.add(user)
    db.flush()

    utr = UserTenantRole(
        user_id=user.id,
        tenant_id=tenant_id,
        role=role,
        is_default=True,
        is_active=True,
    )
    db.add(utr)
    db.flush()

    return user


def seed_demo_account(db: Session, tenant_id: int, tenant_admin_user_id: int):
    """Seed dummy data for a demo account"""

    # Create additional users
    users = []

    # Tenant Admin (already exists, just get reference)
    tenant_admin = (
        db.query(User).filter(User.id == tenant_admin_user_id).first()
    )
    users.append(tenant_admin)

    # Ensure tenant admin has a UserTenantRole (may not exist if created before multi-tenant)
    existing_utr = (
        db.query(UserTenantRole)
        .filter(
            UserTenantRole.user_id == tenant_admin_user_id,
            UserTenantRole.tenant_id == tenant_id,
        )
        .first()
    )
    if not existing_utr:
        utr = UserTenantRole(
            user_id=tenant_admin_user_id,
            tenant_id=tenant_id,
            role=tenant_admin.role,
            is_default=True,
            is_active=True,
        )
        db.add(utr)
        db.flush()

    # Create Administrator
    admin = _create_demo_user(
        db,
        f"admin.demo{tenant_id}@example.com",
        "Sarah Administrator",
        UserRole.ADMINISTRATOR,
        tenant_id,
    )
    users.append(admin)

    # Create Sales Engineers
    se1 = _create_demo_user(
        db,
        f"sales1.demo{tenant_id}@example.com",
        "John Sales Engineer",
        UserRole.SALES_ENGINEER,
        tenant_id,
    )
    users.append(se1)

    se2 = _create_demo_user(
        db,
        f"sales2.demo{tenant_id}@example.com",
        "Maria Sales Engineer",
        UserRole.SALES_ENGINEER,
        tenant_id,
    )
    users.append(se2)

    # Create Customer users
    customer1 = _create_demo_user(
        db,
        f"customer1.demo{tenant_id}@example.com",
        "Alice Customer",
        UserRole.CUSTOMER,
        tenant_id,
    )
    users.append(customer1)

    customer2 = _create_demo_user(
        db,
        f"customer2.demo{tenant_id}@example.com",
        "Bob Customer",
        UserRole.CUSTOMER,
        tenant_id,
    )
    users.append(customer2)

    # Create 5 task templates
    tasks = []
    task_data = [
        {
            "title": "Initial Requirements Gathering",
            "description": "Schedule and conduct kickoff meeting to understand customer needs, pain points, and success criteria.",
        },
        {
            "title": "Environment Setup",
            "description": "Configure development/staging environment with necessary access, credentials, and initial data.",
        },
        {
            "title": "Product Demo",
            "description": "Conduct live demonstration of key product features aligned with customer requirements.",
        },
        {
            "title": "Integration Testing",
            "description": "Test integration points with customer systems, APIs, and data sources.",
        },
        {
            "title": "Final Presentation",
            "description": "Present POC results, findings, and recommendations to stakeholders.",
        },
    ]

    for task_info in task_data:
        task = Task(
            title=task_info["title"],
            description=task_info["description"],
            tenant_id=tenant_id,
            created_by=admin.id,
            is_template=True,
        )
        db.add(task)
        db.flush()
        tasks.append(task)

    # Create 2 task group templates
    task_groups = []

    tg1 = TaskGroup(
        title="Discovery & Planning Phase",
        description="Initial phase to understand requirements and plan the POC approach.",
        tenant_id=tenant_id,
        created_by=admin.id,
        is_template=True,
    )
    db.add(tg1)
    db.flush()
    task_groups.append(tg1)

    tg2 = TaskGroup(
        title="Technical Implementation",
        description="Core implementation and testing of the solution.",
        tenant_id=tenant_id,
        created_by=admin.id,
        is_template=True,
    )
    db.add(tg2)
    db.flush()
    task_groups.append(tg2)

    # Create Products
    products = []
    product1 = Product(
        name="API Integration Platform",
        tenant_id=tenant_id,
    )
    db.add(product1)
    products.append(product1)

    product2 = Product(
        name="Analytics Dashboard Suite",
        tenant_id=tenant_id,
    )
    db.add(product2)
    products.append(product2)

    product3 = Product(
        name="Real-Time Data Sync",
        tenant_id=tenant_id,
    )
    db.add(product3)
    products.append(product3)

    db.flush()

    # Create 2 POCs with success criteria
    pocs = []

    # POC 1 - Active
    poc1 = POC(
        title="E-Commerce Platform Integration",
        description="Proof of concept to integrate our API with customer's e-commerce platform for real-time inventory sync.",
        customer_company_name="Retail Corp",
        start_date=datetime.now(timezone.utc).date() - timedelta(days=7),
        end_date=datetime.now(timezone.utc).date() + timedelta(days=23),
        tenant_id=tenant_id,
        created_by=se1.id,
        status=POCStatus.ACTIVE,
    )
    db.add(poc1)
    db.flush()
    # Associate products with POC1
    poc1.products.extend(
        [product1, product3]
    )  # API Integration + Real-Time Data Sync
    pocs.append(poc1)

    # Add participants to POC1
    poc1_participants = [
        POCParticipant(poc_id=poc1.id, user_id=se1.id, is_sales_engineer=True),
        POCParticipant(
            poc_id=poc1.id, user_id=customer1.id, is_sales_engineer=False
        ),
    ]
    for participant in poc1_participants:
        db.add(participant)

    # Add tasks to POC1 (with start_date / due_date)
    poc1_start = poc1.start_date
    poc1_end = poc1.end_date
    poc1_tasks = [
        POCTask(
            poc_id=poc1.id,
            task_id=tasks[0].id,
            title=tasks[0].title,
            description=tasks[0].description,
            status=TaskStatus.COMPLETED,
            success_level=95,
            sort_order=1,
            start_date=poc1_start,
            due_date=poc1_start + timedelta(days=5),
        ),
        POCTask(
            poc_id=poc1.id,
            task_id=tasks[1].id,
            title=tasks[1].title,
            description=tasks[1].description,
            status=TaskStatus.COMPLETED,
            success_level=100,
            sort_order=2,
            start_date=poc1_start + timedelta(days=3),
            due_date=poc1_start + timedelta(days=10),
        ),
        POCTask(
            poc_id=poc1.id,
            task_id=tasks[2].id,
            title=tasks[2].title,
            description=tasks[2].description,
            status=TaskStatus.IN_PROGRESS,
            success_level=60,
            sort_order=3,
            start_date=poc1_start + timedelta(days=8),
            due_date=poc1_start + timedelta(days=20),
        ),
        POCTask(
            poc_id=poc1.id,
            task_id=tasks[3].id,
            title=tasks[3].title,
            description=tasks[3].description,
            status=TaskStatus.NOT_STARTED,
            sort_order=4,
            start_date=poc1_start + timedelta(days=18),
            due_date=poc1_end,
        ),
    ]
    for task in poc1_tasks:
        db.add(task)
    db.flush()

    # Add task group to POC1
    poc1_task_group = POCTaskGroup(
        poc_id=poc1.id,
        task_group_id=task_groups[0].id,
        title=task_groups[0].title,
        description=task_groups[0].description,
        status=TaskStatus.IN_PROGRESS,
        success_level=75,
        sort_order=0,
        start_date=poc1_start + timedelta(days=2),
        due_date=poc1.end_date,
    )
    db.add(poc1_task_group)

    # Success criteria for POC1
    poc1_criteria = [
        SuccessCriteria(
            poc_id=poc1.id,
            title="Real-time inventory sync",
            description="Successfully sync inventory data within 2 seconds of updates",
            is_met=False,
            importance_level=5,
            sort_order=1,
        ),
        SuccessCriteria(
            poc_id=poc1.id,
            title="Handle 1000+ products",
            description="System can process and sync 1000+ products without performance degradation",
            is_met=True,
            importance_level=4,
            sort_order=2,
        ),
        SuccessCriteria(
            poc_id=poc1.id,
            title="Error handling and retry logic",
            description="Gracefully handle API failures with automatic retry mechanism",
            is_met=False,
            importance_level=4,
            sort_order=3,
        ),
    ]
    for criteria in poc1_criteria:
        db.add(criteria)
    db.flush()

    # Link POC1 tasks to success criteria
    poc1_task_criteria = [
        # "Initial Requirements Gathering" → "Real-time inventory sync"
        TaskSuccessCriteria(
            success_criteria_id=poc1_criteria[0].id,
            poc_task_id=poc1_tasks[0].id,
        ),
        # "Environment Setup" → "Handle 1000+ products"
        TaskSuccessCriteria(
            success_criteria_id=poc1_criteria[1].id,
            poc_task_id=poc1_tasks[1].id,
        ),
        # "Product Demo" → "Real-time inventory sync" + "Error handling"
        TaskSuccessCriteria(
            success_criteria_id=poc1_criteria[0].id,
            poc_task_id=poc1_tasks[2].id,
        ),
        TaskSuccessCriteria(
            success_criteria_id=poc1_criteria[2].id,
            poc_task_id=poc1_tasks[2].id,
        ),
        # "Integration Testing" → "Handle 1000+ products" + "Error handling"
        TaskSuccessCriteria(
            success_criteria_id=poc1_criteria[1].id,
            poc_task_id=poc1_tasks[3].id,
        ),
        TaskSuccessCriteria(
            success_criteria_id=poc1_criteria[2].id,
            poc_task_id=poc1_tasks[3].id,
        ),
    ]
    for link in poc1_task_criteria:
        db.add(link)

    # POC 2 - Completed
    poc2 = POC(
        title="Customer Analytics Dashboard",
        description="POC for implementing custom analytics dashboard with real-time customer behavior tracking.",
        customer_company_name="Analytics Inc",
        start_date=datetime.now(timezone.utc).date() - timedelta(days=45),
        end_date=datetime.now(timezone.utc).date() - timedelta(days=5),
        tenant_id=tenant_id,
        created_by=se2.id,
        status=POCStatus.COMPLETED,
    )
    db.add(poc2)
    db.flush()
    # Associate products with POC2
    poc2.products.append(product2)  # Analytics Dashboard Suite
    pocs.append(poc2)

    # Add participants to POC2
    poc2_participants = [
        POCParticipant(poc_id=poc2.id, user_id=se2.id, is_sales_engineer=True),
        POCParticipant(
            poc_id=poc2.id, user_id=customer2.id, is_sales_engineer=False
        ),
    ]
    for participant in poc2_participants:
        db.add(participant)

    # Add tasks to POC2 (all completed, with start_date / due_date)
    poc2_start = poc2.start_date
    poc2_end = poc2.end_date
    poc2_tasks = [
        POCTask(
            poc_id=poc2.id,
            task_id=tasks[0].id,
            title=tasks[0].title,
            description=tasks[0].description,
            status=TaskStatus.COMPLETED,
            success_level=100,
            sort_order=1,
            start_date=poc2_start,
            due_date=poc2_start + timedelta(days=7),
        ),
        POCTask(
            poc_id=poc2.id,
            task_id=tasks[1].id,
            title=tasks[1].title,
            description=tasks[1].description,
            status=TaskStatus.COMPLETED,
            success_level=100,
            sort_order=2,
            start_date=poc2_start + timedelta(days=5),
            due_date=poc2_start + timedelta(days=14),
        ),
        POCTask(
            poc_id=poc2.id,
            task_id=tasks[2].id,
            title=tasks[2].title,
            description=tasks[2].description,
            status=TaskStatus.COMPLETED,
            success_level=95,
            sort_order=3,
            start_date=poc2_start + timedelta(days=12),
            due_date=poc2_start + timedelta(days=28),
        ),
        POCTask(
            poc_id=poc2.id,
            task_id=tasks[4].id,
            title=tasks[4].title,
            description=tasks[4].description,
            status=TaskStatus.COMPLETED,
            success_level=100,
            sort_order=4,
            start_date=poc2_start + timedelta(days=30),
            due_date=poc2_end,
        ),
    ]
    for task in poc2_tasks:
        db.add(task)
    db.flush()

    # Add task groups to POC2 (both completed)
    poc2_task_group1 = POCTaskGroup(
        poc_id=poc2.id,
        task_group_id=task_groups[0].id,
        title=task_groups[0].title,
        description=task_groups[0].description,
        status=TaskStatus.COMPLETED,
        success_level=100,
        sort_order=0,
        start_date=poc2_start,
        due_date=poc2_start + timedelta(days=20),
    )
    db.add(poc2_task_group1)

    poc2_task_group2 = POCTaskGroup(
        poc_id=poc2.id,
        task_group_id=task_groups[1].id,
        title=task_groups[1].title,
        description=task_groups[1].description,
        status=TaskStatus.COMPLETED,
        success_level=98,
        sort_order=1,
        start_date=poc2_start + timedelta(days=10),
        due_date=poc2.end_date,
    )
    db.add(poc2_task_group2)

    # Success criteria for POC2 (all completed)
    poc2_criteria = [
        SuccessCriteria(
            poc_id=poc2.id,
            title="Custom dashboard widgets",
            description="Implement 5+ customizable dashboard widgets for different metrics",
            is_met=True,
            importance_level=5,
            sort_order=1,
        ),
        SuccessCriteria(
            poc_id=poc2.id,
            title="Real-time data updates",
            description="Dashboard updates in real-time as customer events occur",
            is_met=True,
            importance_level=5,
            sort_order=2,
        ),
        SuccessCriteria(
            poc_id=poc2.id,
            title="Export functionality",
            description="Allow users to export dashboard data to CSV and PDF formats",
            is_met=True,
            importance_level=3,
            sort_order=3,
        ),
    ]
    for criteria in poc2_criteria:
        db.add(criteria)
    db.flush()

    # Link POC2 tasks to success criteria
    poc2_task_criteria = [
        # "Initial Requirements Gathering" → "Custom dashboard widgets"
        TaskSuccessCriteria(
            success_criteria_id=poc2_criteria[0].id,
            poc_task_id=poc2_tasks[0].id,
        ),
        # "Environment Setup" → "Real-time data updates"
        TaskSuccessCriteria(
            success_criteria_id=poc2_criteria[1].id,
            poc_task_id=poc2_tasks[1].id,
        ),
        # "Product Demo" → "Custom dashboard widgets" + "Real-time data updates"
        TaskSuccessCriteria(
            success_criteria_id=poc2_criteria[0].id,
            poc_task_id=poc2_tasks[2].id,
        ),
        TaskSuccessCriteria(
            success_criteria_id=poc2_criteria[1].id,
            poc_task_id=poc2_tasks[2].id,
        ),
        # "Final Presentation" → all three criteria
        TaskSuccessCriteria(
            success_criteria_id=poc2_criteria[0].id,
            poc_task_id=poc2_tasks[3].id,
        ),
        TaskSuccessCriteria(
            success_criteria_id=poc2_criteria[1].id,
            poc_task_id=poc2_tasks[3].id,
        ),
        TaskSuccessCriteria(
            success_criteria_id=poc2_criteria[2].id,
            poc_task_id=poc2_tasks[3].id,
        ),
    ]
    for link in poc2_task_criteria:
        db.add(link)

    db.commit()

    return {
        "users_created": len(users),
        "tasks_created": len(tasks),
        "task_groups_created": len(task_groups),
        "pocs_created": len(pocs),
        "message": "Demo account seeded successfully",
    }
