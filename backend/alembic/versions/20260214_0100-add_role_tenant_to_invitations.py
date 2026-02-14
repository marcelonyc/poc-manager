"""Add role and tenant_id columns to invitations table

Revision ID: a1b2c3d4e5f6
Revises: 20260214_0000
Create Date: 2026-02-14

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "add_inv_role"
down_revision = "add_acct_exec"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("invitations", sa.Column("role", sa.String(), nullable=True))
    op.add_column(
        "invitations",
        sa.Column(
            "tenant_id",
            sa.Integer(),
            sa.ForeignKey("tenants.id"),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("invitations", "tenant_id")
    op.drop_column("invitations", "role")
