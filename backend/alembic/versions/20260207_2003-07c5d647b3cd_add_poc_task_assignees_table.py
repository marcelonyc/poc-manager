"""add_poc_task_assignees_table

Revision ID: 07c5d647b3cd
Revises: c2d3e4f5g6h7
Create Date: 2026-02-07 20:03:02.155996

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "07c5d647b3cd"
down_revision: Union[str, None] = "c2d3e4f5g6h7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create poc_task_assignees table
    op.create_table(
        "poc_task_assignees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("poc_task_id", sa.Integer(), nullable=False),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("assigned_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["poc_task_id"], ["poc_tasks.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["participant_id"], ["poc_participants.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["assigned_by"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "poc_task_id", "participant_id", name="uq_task_participant"
        ),
    )
    op.create_index(
        "ix_poc_task_assignees_poc_task_id",
        "poc_task_assignees",
        ["poc_task_id"],
    )
    op.create_index(
        "ix_poc_task_assignees_participant_id",
        "poc_task_assignees",
        ["participant_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_poc_task_assignees_participant_id", table_name="poc_task_assignees"
    )
    op.drop_index(
        "ix_poc_task_assignees_poc_task_id", table_name="poc_task_assignees"
    )
    op.drop_table("poc_task_assignees")
