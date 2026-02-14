"""add_encryption_key_tracking_table

Revision ID: add_enc_keys
Revises: d4e5f6g7h8i9
Create Date: 2026-02-12 08:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_enc_keys"
down_revision = "d4e5f6g7h8i9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create encryption_keys table for key rotation tracking"""
    op.create_table(
        "encryption_keys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("key_hash", sa.String(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("encrypted_fields_count", sa.Integer(), nullable=False),
        sa.Column(
            "last_rotation_date", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column("rotation_reason", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_encryption_keys_version"),
        "encryption_keys",
        ["version"],
        unique=False,
    )
    op.create_index(
        op.f("ix_encryption_keys_key_hash"),
        "encryption_keys",
        ["key_hash"],
        unique=False,
    )
    op.create_index(
        op.f("ix_encryption_keys_is_primary"),
        "encryption_keys",
        ["is_primary"],
        unique=False,
    )
    op.create_index(
        op.f("ix_encryption_keys_is_active"),
        "encryption_keys",
        ["is_active"],
        unique=False,
    )


def downgrade() -> None:
    """Drop encryption_keys table"""
    op.drop_index(
        op.f("ix_encryption_keys_is_active"), table_name="encryption_keys"
    )
    op.drop_index(
        op.f("ix_encryption_keys_is_primary"), table_name="encryption_keys"
    )
    op.drop_index(
        op.f("ix_encryption_keys_key_hash"), table_name="encryption_keys"
    )
    op.drop_index(
        op.f("ix_encryption_keys_version"), table_name="encryption_keys"
    )
    op.drop_table("encryption_keys")
