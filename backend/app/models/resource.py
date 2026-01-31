"""Resource model"""
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


class Resource(Base):
    """Resource model for POCs, tasks, and task groups"""
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    poc_id = Column(Integer, ForeignKey("pocs.id"), nullable=True)
    poc_task_id = Column(Integer, ForeignKey("poc_tasks.id"), nullable=True)
    poc_task_group_id = Column(Integer, ForeignKey("poc_task_groups.id"), nullable=True)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    resource_type = Column(SQLEnum(ResourceType), nullable=False)
    
    # Content varies by type
    # For LINK: URL
    # For CODE: code snippet
    # For TEXT: formatted text
    # For FILE: file path/URL
    content = Column(Text, nullable=False)
    
    # Optional link to success criteria
    success_criteria_id = Column(Integer, ForeignKey("success_criteria.id"), nullable=True)
    
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    poc = relationship("POC", back_populates="resources")
    poc_task = relationship("POCTask", back_populates="resources")
    poc_task_group = relationship("POCTaskGroup", back_populates="resources")
    success_criteria = relationship("SuccessCriteria", back_populates="resources")
    
    def __repr__(self):
        return f"<Resource {self.title}>"
