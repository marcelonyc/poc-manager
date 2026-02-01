"""add_platform_admin_invitations

Revision ID: 1db0f9f4d45c
Revises: 089771b86f98
Create Date: 2026-01-30 19:51:34.541682

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1db0f9f4d45c'
down_revision: Union[str, None] = '089771b86f98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create invitation status enum (if it doesn't exist)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'invitationstatus') THEN
                CREATE TYPE invitationstatus AS ENUM ('pending', 'accepted', 'expired', 'revoked');
            END IF;
        END
        $$;
    """)
    
    # Create invitations table using raw SQL to reference existing enum type
    op.execute("""
        CREATE TABLE IF NOT EXISTS invitations (
            id SERIAL PRIMARY KEY,
            email VARCHAR NOT NULL,
            full_name VARCHAR NOT NULL,
            token VARCHAR NOT NULL UNIQUE,
            status invitationstatus NOT NULL,
            invited_by_email VARCHAR NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            expires_at TIMESTAMPTZ NOT NULL,
            accepted_at TIMESTAMPTZ
        )
    """)
    
    # Create indexes
    op.create_index(op.f('ix_invitations_id'), 'invitations', ['id'], unique=False)
    op.create_index(op.f('ix_invitations_email'), 'invitations', ['email'], unique=False)
    op.create_index(op.f('ix_invitations_token'), 'invitations', ['token'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_invitations_token'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_email'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_id'), table_name='invitations')
    
    # Drop table
    op.drop_table('invitations')
    
    # Drop enum type
    op.execute("DROP TYPE invitationstatus")
