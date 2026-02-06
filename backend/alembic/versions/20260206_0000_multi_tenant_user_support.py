"""Multi-tenant user support with user_tenant_roles

Revision ID: 20260206_0000
Revises: 20260202_1430
Create Date: 2026-02-06 00:00:00.000000

This migration introduces multi-tenant support for users, allowing a single user
to be associated with multiple tenants, each with a potentially different role.

Changes:
1. Create user_tenant_roles association table
2. Migrate existing user tenant_id and role data to user_tenant_roles
3. Keep original columns temporarily for backward compatibility during transition
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5a6'
down_revision = '9f8e7d6c5b4a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Upgrade schema to support multi-tenant users.
    
    Migration strategy:
    1. Create new user_tenant_roles table
    2. Populate user_tenant_roles from existing users data
    3. Keep tenant_id and role columns in users table (for now) for backward compatibility
    4. A future migration will remove the old columns after all code is updated
    """
    
    # Create user_tenant_roles table
    op.create_table(
        'user_tenant_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('role', sa.Enum(
            'PLATFORM_ADMIN', 'TENANT_ADMIN', 'ADMINISTRATOR', 
            'SALES_ENGINEER', 'CUSTOMER', 
            name='userrole'
        ), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'tenant_id', name='uq_user_tenant')
    )
    
    # Create indexes for performance
    op.create_index('ix_user_tenant_roles_id', 'user_tenant_roles', ['id'])
    op.create_index('ix_user_tenant_roles_user_id', 'user_tenant_roles', ['user_id'])
    op.create_index('ix_user_tenant_roles_tenant_id', 'user_tenant_roles', ['tenant_id'])
    op.create_index('ix_user_tenant_roles_role', 'user_tenant_roles', ['role'])
    
    # Migrate existing data from users table to user_tenant_roles
    # This SQL statement will:
    # 1. Insert a row in user_tenant_roles for each user
    # 2. Use their existing tenant_id and role
    # 3. Mark it as their default tenant (is_default=true)
    # 4. Handle platform_admin users (who may have tenant_id=NULL)
    
    op.execute("""
        INSERT INTO user_tenant_roles (user_id, tenant_id, role, is_default, created_at)
        SELECT 
            id as user_id,
            tenant_id,
            role,
            true as is_default,
            created_at
        FROM users
        WHERE is_active = true
    """)
    
    print("✓ Migrated existing user-tenant-role associations")


def downgrade() -> None:
    """
    Downgrade by removing the user_tenant_roles table.
    
    WARNING: This will lose any multi-tenant associations that were added
    after the migration. The original tenant_id and role in users table
    should still contain the original associations.
    """
    
    # Drop indexes
    op.drop_index('ix_user_tenant_roles_role', table_name='user_tenant_roles')
    op.drop_index('ix_user_tenant_roles_tenant_id', table_name='user_tenant_roles')
    op.drop_index('ix_user_tenant_roles_user_id', table_name='user_tenant_roles')
    op.drop_index('ix_user_tenant_roles_id', table_name='user_tenant_roles')
    
    # Drop table
    op.drop_table('user_tenant_roles')
    
    print("✓ Removed user_tenant_roles table")
