"""Task Group Resource model"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.task_template_resource import ResourceType


class TaskGroupResource(Base):
    """Resource model for task group templates"""
    __tablename__ = "task_group_resources"

    id = Column(Integer, primary_key=True, index=True)
    task_group_id = Column(Integer, ForeignKey("task_groups.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    resource_type = Column(SQLEnum(ResourceType), nullable=False)
    
    # Content varies by type
    # For LINK: URL
    # For CODE: code snippet
    # For TEXT: formatted text
    # For FILE: file path/URL
    content = Column(Text, nullable=False)
    
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    task_group = relationship("TaskGroup", back_populates="resources")
    
    def __repr__(self):
        return f"<TaskGroupResource {self.title}>"
