"""add_task_satisfaction_statuses

Revision ID: a1b2c3d4e5f6
Revises: f0f89f3591ee
Create Date: 2026-02-11 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f0f89f3591ee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new values to the taskstatus enum type in PostgreSQL
    op.execute("ALTER TYPE taskstatus ADD VALUE IF NOT EXISTS 'SATISFIED'")
    op.execute(
        "ALTER TYPE taskstatus ADD VALUE IF NOT EXISTS 'PARTIALLY_SATISFIED'"
    )
    op.execute("ALTER TYPE taskstatus ADD VALUE IF NOT EXISTS 'NOT_SATISFIED'")


def downgrade() -> None:
    # PostgreSQL does not support removing values from an enum type directly.
    # A full recreation of the enum would be required for a proper downgrade.
    pass
