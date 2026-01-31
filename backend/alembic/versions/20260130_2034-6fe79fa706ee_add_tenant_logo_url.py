"""add_tenant_logo_url

Revision ID: 6fe79fa706ee
Revises: 1db0f9f4d45c
Create Date: 2026-01-30 20:34:54.201471

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6fe79fa706ee'
down_revision: Union[str, None] = '1db0f9f4d45c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add logo_url column to tenants table
    op.add_column('tenants', sa.Column('logo_url', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove logo_url column from tenants table
    op.drop_column('tenants', 'logo_url')
