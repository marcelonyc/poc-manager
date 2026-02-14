"""Add account_executive role and tenant limit

Revision ID: add_acct_exec
Revises: add_enc_keys
Create Date: 2026-02-14 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_acct_exec"
down_revision = "add_enc_keys"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add ACCOUNT_EXECUTIVE to the userrole enum
    op.execute(
        "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'ACCOUNT_EXECUTIVE'"
    )

    # Add account_executive_limit column to tenants
    op.add_column(
        "tenants",
        sa.Column(
            "account_executive_limit",
            sa.Integer(),
            nullable=True,
            server_default=sa.text("50"),
        ),
    )


def downgrade() -> None:
    op.drop_column("tenants", "account_executive_limit")
    # Note: PostgreSQL does not support removing values from an enum type.
    # The ACCOUNT_EXECUTIVE value will remain in the enum after downgrade.
