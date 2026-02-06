"""Add tenant invitations table

Revision ID: 20260206_0001
Revises: 20260206_0000
Create Date: 2026-02-06 00:01:00.000000

This migration adds the tenant_invitations table for inviting existing users
to join additional tenants with specific roles.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c2d3e4f5g6h7'
down_revision = 'b1c2d3e4f5a6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create tenant_invitations table"""
    
    op.create_table(
        'tenant_invitations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum(
            'PLATFORM_ADMIN', 'TENANT_ADMIN', 'ADMINISTRATOR', 
            'SALES_ENGINEER', 'CUSTOMER', 
            name='userrole'
        ), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('status', sa.Enum(
            'PENDING', 'ACCEPTED', 'EXPIRED', 'REVOKED',
            name='tenantinvitationstatus'
        ), nullable=False, server_default='PENDING'),
        sa.Column('invited_by_user_id', sa.Integer(), nullable=False),
        sa.Column('invited_by_email', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_tenant_invitations_id', 'tenant_invitations', ['id'])
    op.create_index('ix_tenant_invitations_email', 'tenant_invitations', ['email'])
    op.create_index('ix_tenant_invitations_tenant_id', 'tenant_invitations', ['tenant_id'])
    op.create_index('ix_tenant_invitations_token', 'tenant_invitations', ['token'], unique=True)
    
    print("✓ Created tenant_invitations table")


def downgrade() -> None:
    """Drop tenant_invitations table"""
    
    # Drop indexes
    op.drop_index('ix_tenant_invitations_token', table_name='tenant_invitations')
    op.drop_index('ix_tenant_invitations_tenant_id', table_name='tenant_invitations')
    op.drop_index('ix_tenant_invitations_email', table_name='tenant_invitations')
    op.drop_index('ix_tenant_invitations_id', table_name='tenant_invitations')
    
    # Drop table
    op.drop_table('tenant_invitations')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS tenantinvitationstatus')
    
    print("✓ Dropped tenant_invitations table")
