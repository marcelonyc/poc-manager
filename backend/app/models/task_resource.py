"""Task Resource junction model"""
from sqlalchemy import Column, Integer, ForeignKey, Table
from app.database import Base

# Many-to-many relationship between tasks and resources
task_resources = Table(
    'task_resources',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('resource_id', Integer, ForeignKey('task_template_resources.id', ondelete='CASCADE'), primary_key=True)
)
