"""add_poc_fields_and_diagram_support

Revision ID: 7d69c593693f
Revises: 0b30068ce592
Create Date: 2026-01-30 22:36:35.350547

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d69c593693f'
down_revision: Union[str, None] = '0b30068ce592'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new fields to pocs table
    op.add_column('pocs', sa.Column('executive_summary', sa.Text(), nullable=True))
    op.add_column('pocs', sa.Column('objectives', sa.Text(), nullable=True))
    
    # Add importance_level to success_criteria table
    op.add_column('success_criteria', sa.Column('importance_level', sa.Integer(), nullable=True, server_default='3'))
    
    # Create poc_diagrams table for file uploads
    op.create_table(
        'poc_diagrams',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('poc_id', sa.Integer(), sa.ForeignKey('pocs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_type', sa.String(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    op.create_index('ix_poc_diagrams_poc_id', 'poc_diagrams', ['poc_id'])


def downgrade() -> None:
    # Drop poc_diagrams table
    op.drop_index('ix_poc_diagrams_poc_id', 'poc_diagrams')
    op.drop_table('poc_diagrams')
    
    # Remove columns from success_criteria
    op.drop_column('success_criteria', 'importance_level')
    
    # Remove columns from pocs
    op.drop_column('pocs', 'objectives')
    op.drop_column('pocs', 'executive_summary')
