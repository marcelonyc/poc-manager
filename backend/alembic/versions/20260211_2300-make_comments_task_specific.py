"""Make comments task/task-group specific instead of POC-level

Revision ID: make_comments_task_specific
Revises: c3d4e5f6g7h8_add_guest_comments
Create Date: 2026-02-11 23:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "make_comments_task_specific"
down_revision = "c3d4e5f6g7h8_add_guest_comments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Delete any existing comments that don't have a task_id or task_group_id
    # These are POC-level comments that are no longer supported
    op.execute(
        """
        DELETE FROM comments 
        WHERE poc_task_id IS NULL AND poc_task_group_id IS NULL;
    """
    )

    # Make poc_id nullable
    op.alter_column(
        "comments", "poc_id", existing_type=sa.Integer(), nullable=True
    )

    # Add constraint to ensure either poc_task_id or poc_task_group_id is set
    op.execute(
        """
        ALTER TABLE comments
        ADD CONSTRAINT check_comment_has_task_or_taskgroup
        CHECK (poc_task_id IS NOT NULL OR poc_task_group_id IS NOT NULL);
    """
    )


def downgrade() -> None:
    # Remove the constraint
    op.execute(
        """
        ALTER TABLE comments
        DROP CONSTRAINT check_comment_has_task_or_taskgroup;
    """
    )

    # Restore poc_id as NOT NULL
    op.alter_column(
        "comments", "poc_id", existing_type=sa.Integer(), nullable=False
    )
