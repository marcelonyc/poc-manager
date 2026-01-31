"""Database seeding script"""
import sys
sys.path.append('.')

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.models.task import Task, TaskGroup
from app.auth import get_password_hash

def seed_data():
    """Seed the database with sample data"""
    db = SessionLocal()
    
    try:
        print("🌱 Seeding database...")
        
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
        
        # Create tenant admin
        tenant_admin = User(
            email="admin@acme.com",
            full_name="Acme Admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.TENANT_ADMIN,
            tenant_id=tenant.id,
            is_active=True,
        )
        db.add(tenant_admin)
        
        # Create administrator
        administrator = User(
            email="manager@acme.com",
            full_name="POC Manager",
            hashed_password=get_password_hash("manager123"),
            role=UserRole.ADMINISTRATOR,
            tenant_id=tenant.id,
            is_active=True,
        )
        db.add(administrator)
        
        # Create sales engineer
        sales_engineer = User(
            email="sales@acme.com",
            full_name="Sales Engineer",
            hashed_password=get_password_hash("sales123"),
            role=UserRole.SALES_ENGINEER,
            tenant_id=tenant.id,
            is_active=True,
        )
        db.add(sales_engineer)
        db.flush()
        
        print("✅ Created users: Tenant Admin, Administrator, Sales Engineer")
        
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
