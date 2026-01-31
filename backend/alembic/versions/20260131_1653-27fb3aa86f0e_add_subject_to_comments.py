"""add_subject_to_comments

Revision ID: 27fb3aa86f0e
Revises: 18d611cbe1a3
Create Date: 2026-01-31 16:53:31.643017

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27fb3aa86f0e'
down_revision: Union[str, None] = '18d611cbe1a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add subject column to comments table
    op.add_column('comments', sa.Column('subject', sa.String(), nullable=True))
    
    # Set default subject for existing comments
    op.execute("UPDATE comments SET subject = 'General Comment' WHERE subject IS NULL")
    
    # Make subject non-nullable
    op.alter_column('comments', 'subject', nullable=False)


def downgrade() -> None:
    # Remove subject column
    op.drop_column('comments', 'subject')
