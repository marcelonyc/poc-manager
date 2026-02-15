"""Add start_date and due_date columns to poc_task_groups table

Revision ID: add_tg_dates
Revises: add_task_dates
Create Date: 2026-02-15

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "add_tg_dates"
down_revision = "add_task_dates"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "poc_task_groups", sa.Column("start_date", sa.Date(), nullable=True)
    )
    op.add_column(
        "poc_task_groups", sa.Column("due_date", sa.Date(), nullable=True)
    )


def downgrade():
    op.drop_column("poc_task_groups", "due_date")
    op.drop_column("poc_task_groups", "start_date")
