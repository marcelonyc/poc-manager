"""Task Template Resource model"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ResourceType(str, enum.Enum):
    """Resource type enumeration"""
    LINK = "link"
    CODE = "code"
    TEXT = "text"
    FILE = "file"


class TaskTemplateResource(Base):
    """Resource model for task templates"""
    __tablename__ = "task_template_resources"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    
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
    task = relationship("Task", back_populates="resources")
    
    def __repr__(self):
        return f"<TaskTemplateResource {self.title}>"
