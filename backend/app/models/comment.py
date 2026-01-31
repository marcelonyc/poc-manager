"""Comment model"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Comment(Base):
    """Comment model for POCs, tasks, and task groups"""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    poc_id = Column(Integer, ForeignKey("pocs.id"), nullable=False)
    
    # Comments can be on POC, specific task, or task group
    poc_task_id = Column(Integer, ForeignKey("poc_tasks.id"), nullable=True)
    poc_task_group_id = Column(Integer, ForeignKey("poc_task_groups.id"), nullable=True)
    
    # Internal comments (only visible to sales engineers and admins)
    is_internal = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="comments")
    poc = relationship("POC", back_populates="comments")
    poc_task = relationship("POCTask", back_populates="comments")
    poc_task_group = relationship("POCTaskGroup", back_populates="comments")
    
    def __repr__(self):
        return f"<Comment by User:{self.user_id} on POC:{self.poc_id}>"
