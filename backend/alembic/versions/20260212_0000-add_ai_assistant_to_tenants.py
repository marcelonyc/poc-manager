"""Add AI assistant fields to tenants

Revision ID: a1b2c3d4e5f6
Revises: c3d4e5f6g7h8
Create Date: 2026-02-12 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d4e5f6g7h8i9"
down_revision = "make_comments_task_specific"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tenants",
        sa.Column(
            "ai_assistant_enabled",
            sa.Boolean(),
            nullable=True,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "tenants",
        sa.Column("ollama_api_key", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tenants", "ollama_api_key")
    op.drop_column("tenants", "ai_assistant_enabled")
