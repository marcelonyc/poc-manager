"""Add start_date and due_date columns to poc_tasks table

Revision ID: add_task_dates
Revises: add_inv_role
Create Date: 2026-02-15

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "add_task_dates"
down_revision = "add_inv_role"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "poc_tasks", sa.Column("start_date", sa.Date(), nullable=True)
    )
    op.add_column("poc_tasks", sa.Column("due_date", sa.Date(), nullable=True))


def downgrade():
    op.drop_column("poc_tasks", "due_date")
    op.drop_column("poc_tasks", "start_date")
