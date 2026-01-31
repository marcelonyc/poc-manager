"""Add task template resources

Revision ID: 089771b86f98
Revises: 8bbda67bbd34
Create Date: 2026-01-29 19:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '089771b86f98'
down_revision: Union[str, None] = '8bbda67bbd34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create table using raw SQL to reference existing enum type
    op.execute("""
        CREATE TABLE task_template_resources (
            id SERIAL PRIMARY KEY,
            task_id INTEGER NOT NULL,
            title VARCHAR NOT NULL,
            description TEXT,
            resource_type resourcetype NOT NULL,
            content TEXT NOT NULL,
            sort_order INTEGER,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX ix_task_template_resources_id ON task_template_resources (id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_task_template_resources_id")
    op.execute("DROP TABLE IF EXISTS task_template_resources")
