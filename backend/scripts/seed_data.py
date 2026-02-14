"""Database seeding script"""

import sys

sys.path.append(".")

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.user_tenant_role import UserTenantRole
from app.models.tenant import Tenant
from app.models.task import Task, TaskGroup
from app.auth import get_password_hash


def _create_user_with_tenant_role(
    db, email, full_name, password, role, tenant
):
    """Create a user and its corresponding user_tenant_role entry."""
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        role=role,
        tenant_id=tenant.id if tenant else None,
        is_active=True,
    )
    db.add(user)
    db.flush()

    if tenant:
        utr = UserTenantRole(
            user_id=user.id,
            tenant_id=tenant.id,
            role=role,
            is_default=True,
            is_active=True,
        )
        db.add(utr)
        db.flush()

    return user


def seed_data():
    """Seed the database with sample data"""
    db = SessionLocal()

    try:
        print("🌱 Seeding database...")

        # Create Platform Admin (no tenant association)
        platform_admin = User(
            email="platform@pocmanager.com",
            full_name="Platform Admin",
            hashed_password=get_password_hash("platform123"),
            role=UserRole.PLATFORM_ADMIN,
            tenant_id=None,
            is_active=True,
        )
        db.add(platform_admin)
        db.flush()
        print(f"✅ Created Platform Admin: {platform_admin.email}")

        # Create sample tenant
        tenant = Tenant(
            name="Acme Corporation",
            slug="acme",
            primary_color="#0066cc",
            contact_email="contact@acme.com",
        )
        db.add(tenant)
        db.flush()

        print(f"✅ Created tenant: {tenant.name}")

        # Create tenant users with user_tenant_roles
        tenant_admin = _create_user_with_tenant_role(
            db,
            "admin@acme.com",
            "Acme Admin",
            "admin123",
            UserRole.TENANT_ADMIN,
            tenant,
        )
        administrator = _create_user_with_tenant_role(
            db,
            "manager@acme.com",
            "POC Manager",
            "manager123",
            UserRole.ADMINISTRATOR,
            tenant,
        )
        sales_engineer = _create_user_with_tenant_role(
            db,
            "sales@acme.com",
            "Sales Engineer",
            "sales123",
            UserRole.SALES_ENGINEER,
            tenant,
        )

        print(
            "✅ Created users: Platform Admin, Tenant Admin, Administrator, Sales Engineer"
        )
        print("   (with user_tenant_roles for tenant-scoped users)")

        # Create sample task templates
        tasks = [
            Task(
                title="Environment Setup",
                description="Set up development and testing environment",
                tenant_id=tenant.id,
                created_by=administrator.id,
                is_template=True,
            ),
            Task(
                title="Data Integration",
                description="Integrate customer data sources",
                tenant_id=tenant.id,
                created_by=administrator.id,
                is_template=True,
            ),
            Task(
                title="API Testing",
                description="Test API endpoints and performance",
                tenant_id=tenant.id,
                created_by=administrator.id,
                is_template=True,
            ),
            Task(
                title="Security Review",
                description="Conduct security assessment and review",
                tenant_id=tenant.id,
                created_by=administrator.id,
                is_template=True,
            ),
        ]
        db.add_all(tasks)

        # Create sample task group templates
        task_groups = [
            TaskGroup(
                title="Initial Setup",
                description="All tasks required for initial POC setup",
                tenant_id=tenant.id,
                created_by=administrator.id,
                is_template=True,
            ),
            TaskGroup(
                title="Core Features",
                description="Implementation of core product features",
                tenant_id=tenant.id,
                created_by=administrator.id,
                is_template=True,
            ),
            TaskGroup(
                title="Final Review",
                description="Final review and sign-off tasks",
                tenant_id=tenant.id,
                created_by=administrator.id,
                is_template=True,
            ),
        ]
        db.add_all(task_groups)

        print(f"✅ Created {len(tasks)} task templates")
        print(f"✅ Created {len(task_groups)} task group templates")

        db.commit()
        print("✨ Database seeding complete!")
        print("\n📝 Sample credentials:")
        print("   Platform Admin: platform@pocmanager.com / platform123")
        print("   Tenant Admin: admin@acme.com / admin123")
        print("   Administrator: manager@acme.com / manager123")
        print("   Sales Engineer: sales@acme.com / sales123")

    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
