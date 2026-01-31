"""add_demo_account_system

Revision ID: 7cbfa9b9ee3c
Revises: 867030615fdc
Create Date: 2026-01-31 17:52:08.472291

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cbfa9b9ee3c'
down_revision: Union[str, None] = '867030615fdc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add demo fields to tenants table
    op.add_column('tenants', sa.Column('is_demo', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('tenants', sa.Column('sales_engineers_count', sa.Integer(), nullable=True))
    op.add_column('tenants', sa.Column('pocs_per_quarter', sa.Integer(), nullable=True))
    
    # Create demo_requests table
    op.create_table(
        'demo_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('company_name', sa.String(), nullable=False),
        sa.Column('sales_engineers_count', sa.Integer(), nullable=False),
        sa.Column('pocs_per_quarter', sa.Integer(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    op.create_index(op.f('ix_demo_requests_id'), 'demo_requests', ['id'], unique=False)
    op.create_index(op.f('ix_demo_requests_email'), 'demo_requests', ['email'], unique=False)
    
    # Create email_verification_tokens table
    op.create_table(
        'email_verification_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('demo_request_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['demo_request_id'], ['demo_requests.id'], ),
    )
    op.create_index(op.f('ix_email_verification_tokens_id'), 'email_verification_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_email_verification_tokens_token'), 'email_verification_tokens', ['token'], unique=True)
    
    # Create demo_conversion_requests table
    op.create_table(
        'demo_conversion_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('requested_by_user_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('approved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('approved_by_user_id', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['requested_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['approved_by_user_id'], ['users.id'], ),
    )
    op.create_index(op.f('ix_demo_conversion_requests_id'), 'demo_conversion_requests', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_demo_conversion_requests_id'), table_name='demo_conversion_requests')
    op.drop_table('demo_conversion_requests')
    
    op.drop_index(op.f('ix_email_verification_tokens_token'), table_name='email_verification_tokens')
    op.drop_index(op.f('ix_email_verification_tokens_id'), table_name='email_verification_tokens')
    op.drop_table('email_verification_tokens')
    
    op.drop_index(op.f('ix_demo_requests_email'), table_name='demo_requests')
    op.drop_index(op.f('ix_demo_requests_id'), table_name='demo_requests')
    op.drop_table('demo_requests')
    
    op.drop_column('tenants', 'pocs_per_quarter')
    op.drop_column('tenants', 'sales_engineers_count')
    op.drop_column('tenants', 'is_demo')
