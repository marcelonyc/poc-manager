"""add_task_group_resources

Revision ID: 8046ac03eb3b
Revises: 0babdd710f96
Create Date: 2026-01-30 21:47:53.153220

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8046ac03eb3b'
down_revision: Union[str, None] = '0babdd710f96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create task_group_resources table (reuse existing resourcetype enum)
    op.create_table(
        'task_group_resources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_group_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('resource_type', postgresql.ENUM('LINK', 'CODE', 'TEXT', 'FILE', name='resourcetype', create_type=False), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['task_group_id'], ['task_groups.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_group_resources_id'), 'task_group_resources', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_task_group_resources_id'), table_name='task_group_resources')
    op.drop_table('task_group_resources')
