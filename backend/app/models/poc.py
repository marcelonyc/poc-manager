"""POC model"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLEnum,
    Date,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class POCStatus(str, enum.Enum):
    """POC status enumeration"""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


# Association table for POC-Product many-to-many relationship
poc_products = Table(
    "poc_products",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "poc_id",
        Integer,
        ForeignKey("pocs.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "product_id",
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)


class POC(Base):
    """POC model"""

    __tablename__ = "pocs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Customer information
    customer_company_name = Column(String, nullable=False)
    customer_logo_url = Column(String, nullable=True)

    # POC Details
    executive_summary = Column(Text, nullable=True)
    objectives = Column(Text, nullable=True)

    # Timeline
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    status = Column(SQLEnum(POCStatus), default=POCStatus.DRAFT)

    # Success tracking
    overall_success_score = Column(Integer, nullable=True)  # 0-100

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="pocs")
    created_by_user = relationship(
        "User", back_populates="created_pocs", foreign_keys=[created_by]
    )
    participants = relationship("POCParticipant", back_populates="poc")
    success_criteria = relationship("SuccessCriteria", back_populates="poc")
    poc_tasks = relationship("POCTask", back_populates="poc")
    poc_task_groups = relationship("POCTaskGroup", back_populates="poc")
    comments = relationship("Comment", back_populates="poc")
    resources = relationship(
        "Resource", back_populates="poc", cascade="all, delete-orphan"
    )
    products = relationship(
        "Product", secondary=poc_products, back_populates="pocs"
    )
    public_links = relationship(
        "POCPublicLink", back_populates="poc", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<POC {self.title}>"


class POCParticipant(Base):
    """POC participant junction table"""

    __tablename__ = "poc_participants"

    id = Column(Integer, primary_key=True, index=True)
    poc_id = Column(Integer, ForeignKey("pocs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Participant type for easier filtering
    is_sales_engineer = Column(Boolean, default=False)
    is_customer = Column(Boolean, default=False)

    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    poc = relationship("POC", back_populates="participants")
    user = relationship("User", back_populates="poc_participations")

    def __repr__(self):
        return f"<POCParticipant POC:{self.poc_id} User:{self.user_id}>"
