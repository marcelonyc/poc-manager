"""remove_diagrams_add_task_resources

Revision ID: 9f8e7d6c5b4a
Revises: a2be3a706ac8
Create Date: 2026-02-02 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9f8e7d6c5b4a'
down_revision = 'a2be3a706ac8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the poc_diagrams table
    op.drop_table('poc_diagrams')
    
    # Make poc_id nullable in resources table
    op.alter_column('resources', 'poc_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    
    # Add poc_task_id column to resources
    op.add_column('resources', sa.Column('poc_task_id', sa.Integer(), nullable=True))
    op.create_foreign_key('resources_poc_task_id_fkey', 'resources', 'poc_tasks', ['poc_task_id'], ['id'])
    
    # Add poc_task_group_id column to resources
    op.add_column('resources', sa.Column('poc_task_group_id', sa.Integer(), nullable=True))
    op.create_foreign_key('resources_poc_task_group_id_fkey', 'resources', 'poc_task_groups', ['poc_task_group_id'], ['id'])


def downgrade() -> None:
    # Remove foreign keys and columns from resources
    op.drop_constraint('resources_poc_task_group_id_fkey', 'resources', type_='foreignkey')
    op.drop_column('resources', 'poc_task_group_id')
    
    op.drop_constraint('resources_poc_task_id_fkey', 'resources', type_='foreignkey')
    op.drop_column('resources', 'poc_task_id')
    
    # Make poc_id NOT nullable again
    op.alter_column('resources', 'poc_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    
    # Recreate poc_diagrams table
    op.create_table('poc_diagrams',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('poc_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('filename', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('file_path', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('file_type', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('uploaded_by', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['poc_id'], ['pocs.id'], name='poc_diagrams_poc_id_fkey', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], name='poc_diagrams_uploaded_by_fkey'),
        sa.PrimaryKeyConstraint('id', name='poc_diagrams_pkey')
    )
    op.create_index('ix_poc_diagrams_id', 'poc_diagrams', ['id'], unique=False)
