"""add_is_active_to_user_tenant_roles

Revision ID: f0f89f3591ee
Revises: 07c5d647b3cd
Create Date: 2026-02-07 21:24:09.244778

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f0f89f3591ee"
down_revision: Union[str, None] = "07c5d647b3cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add is_active field to user_tenant_roles table.
    This allows users to be deactivated per tenant without affecting their platform access.
    """
    # Add is_active column with default True
    op.add_column(
        "user_tenant_roles",
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default="true"
        ),
    )

    # Create index for performance
    op.create_index(
        "ix_user_tenant_roles_is_active", "user_tenant_roles", ["is_active"]
    )


def downgrade() -> None:
    """
    Remove is_active field from user_tenant_roles table.
    """
    op.drop_index(
        "ix_user_tenant_roles_is_active", table_name="user_tenant_roles"
    )
    op.drop_column("user_tenant_roles", "is_active")
