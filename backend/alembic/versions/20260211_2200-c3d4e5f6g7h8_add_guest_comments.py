"""add_guest_comments

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-02-11 22:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6g7h8"
down_revision: Union[str, None] = "b2c3d4e5f6g7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make user_id nullable to support guest comments
    op.alter_column(
        "comments", "user_id", existing_type=sa.Integer(), nullable=True
    )

    # Add guest comment fields
    op.add_column(
        "comments", sa.Column("guest_name", sa.String(), nullable=True)
    )
    op.add_column(
        "comments", sa.Column("guest_email", sa.String(), nullable=True)
    )


def downgrade() -> None:
    # Remove guest fields
    op.drop_column("comments", "guest_email")
    op.drop_column("comments", "guest_name")

    # Make user_id non-nullable again
    op.alter_column(
        "comments", "user_id", existing_type=sa.Integer(), nullable=False
    )
