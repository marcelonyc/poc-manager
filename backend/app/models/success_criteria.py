"""Success criteria model"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class SuccessCriteria(Base):
    """Success criteria for a POC"""
    __tablename__ = "success_criteria"

    id = Column(Integer, primary_key=True, index=True)
    poc_id = Column(Integer, ForeignKey("pocs.id"), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Measurement
    target_value = Column(String, nullable=True)
    achieved_value = Column(String, nullable=True)
    is_met = Column(Boolean, default=False)
    
    # Importance level (1-5, where 5 is most important)
    importance_level = Column(Integer, default=3)
    
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    poc = relationship("POC", back_populates="success_criteria")
    task_criteria = relationship("TaskSuccessCriteria", back_populates="success_criteria")
    resources = relationship("Resource", back_populates="success_criteria")
    
    def __repr__(self):
        return f"<SuccessCriteria {self.title}>"


class TaskSuccessCriteria(Base):
    """Junction table linking tasks/task groups to success criteria"""
    __tablename__ = "task_success_criteria"

    id = Column(Integer, primary_key=True, index=True)
    success_criteria_id = Column(Integer, ForeignKey("success_criteria.id"), nullable=False)
    
    # Either task or task group, not both
    poc_task_id = Column(Integer, ForeignKey("poc_tasks.id"), nullable=True)
    poc_task_group_id = Column(Integer, ForeignKey("poc_task_groups.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    success_criteria = relationship("SuccessCriteria", back_populates="task_criteria")
    poc_task = relationship("POCTask", back_populates="task_criteria")
    poc_task_group = relationship("POCTaskGroup", back_populates="group_criteria")
    
    def __repr__(self):
        return f"<TaskSuccessCriteria Criteria:{self.success_criteria_id}>"
