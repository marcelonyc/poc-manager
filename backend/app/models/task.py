"""Task and TaskGroup models"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLEnum,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


# Association table for task groups and tasks
task_group_tasks = Table(
    "task_group_tasks",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "task_group_id",
        Integer,
        ForeignKey("task_groups.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "task_id",
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("sort_order", Integer, default=0),
    Column(
        "created_at",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    ),
    UniqueConstraint("task_group_id", "task_id", name="uq_task_group_task"),
)


class TaskStatus(str, enum.Enum):
    """Task status enumeration"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class Task(Base):
    """Reusable task template model"""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # For organization
    is_template = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="tasks")
    poc_tasks = relationship("POCTask", back_populates="task")
    resources = relationship(
        "TaskTemplateResource",
        back_populates="task",
        cascade="all, delete-orphan",
    )
    task_groups = relationship(
        "TaskGroup", secondary=task_group_tasks, back_populates="tasks"
    )

    def __repr__(self):
        return f"<Task {self.title}>"


class TaskGroup(Base):
    """Reusable task group template model"""

    __tablename__ = "task_groups"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    is_template = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="task_groups")
    poc_task_groups = relationship("POCTaskGroup", back_populates="task_group")
    tasks = relationship(
        "Task", secondary=task_group_tasks, back_populates="task_groups"
    )
    resources = relationship(
        "TaskGroupResource",
        back_populates="task_group",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<TaskGroup {self.title}>"


class POCTask(Base):
    """Task instance in a specific POC"""

    __tablename__ = "poc_tasks"

    id = Column(Integer, primary_key=True, index=True)
    poc_id = Column(Integer, ForeignKey("pocs.id"), nullable=False)
    task_id = Column(
        Integer, ForeignKey("tasks.id"), nullable=True
    )  # Can be custom

    # Task can be customized per POC
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    status = Column(SQLEnum(TaskStatus), default=TaskStatus.NOT_STARTED)
    success_level = Column(Integer, nullable=True)  # 0-100

    # Ordering
    sort_order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    poc = relationship("POC", back_populates="poc_tasks")
    task = relationship("Task", back_populates="poc_tasks")
    comments = relationship("Comment", back_populates="poc_task")
    task_criteria = relationship(
        "TaskSuccessCriteria", back_populates="poc_task"
    )
    resources = relationship(
        "Resource", back_populates="poc_task", cascade="all, delete-orphan"
    )
    assignees = relationship(
        "POCTaskAssignee",
        back_populates="poc_task",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<POCTask {self.title}>"


class POCTaskGroup(Base):
    """Task group instance in a specific POC"""

    __tablename__ = "poc_task_groups"

    id = Column(Integer, primary_key=True, index=True)
    poc_id = Column(Integer, ForeignKey("pocs.id"), nullable=False)
    task_group_id = Column(
        Integer, ForeignKey("task_groups.id"), nullable=True
    )

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    status = Column(SQLEnum(TaskStatus), default=TaskStatus.NOT_STARTED)
    success_level = Column(Integer, nullable=True)  # 0-100

    sort_order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    poc = relationship("POC", back_populates="poc_task_groups")
    task_group = relationship("TaskGroup", back_populates="poc_task_groups")
    comments = relationship("Comment", back_populates="poc_task_group")
    group_criteria = relationship(
        "TaskSuccessCriteria", back_populates="poc_task_group"
    )
    resources = relationship(
        "Resource",
        back_populates="poc_task_group",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<POCTaskGroup {self.title}>"


class POCTaskAssignee(Base):
    """Assignment of POC tasks to POC participants"""

    __tablename__ = "poc_task_assignees"

    id = Column(Integer, primary_key=True, index=True)
    poc_task_id = Column(
        Integer,
        ForeignKey("poc_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    participant_id = Column(
        Integer,
        ForeignKey("poc_participants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    assigned_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    poc_task = relationship("POCTask", back_populates="assignees")
    participant = relationship("POCParticipant")
    assigned_by_user = relationship("User")

    def __repr__(self):
        return f"<POCTaskAssignee Task:{self.poc_task_id} Participant:{self.participant_id}>"
