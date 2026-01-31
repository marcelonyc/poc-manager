"""add_task_group_tasks_association

Revision ID: 0babdd710f96
Revises: 6fe79fa706ee
Create Date: 2026-01-30 21:26:01.338020

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0babdd710f96'
down_revision: Union[str, None] = '6fe79fa706ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create task_group_tasks association table
    op.create_table(
        'task_group_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_group_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['task_group_id'], ['task_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_group_id', 'task_id', name='uq_task_group_task')
    )
    op.create_index('ix_task_group_tasks_task_group_id', 'task_group_tasks', ['task_group_id'])
    op.create_index('ix_task_group_tasks_task_id', 'task_group_tasks', ['task_id'])


def downgrade() -> None:
    op.drop_index('ix_task_group_tasks_task_id')
    op.drop_index('ix_task_group_tasks_task_group_id')
    op.drop_table('task_group_tasks')
