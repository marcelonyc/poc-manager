"""Tenant model"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Tenant(Base):
    """Tenant model"""

    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)

    # Branding
    logo_url = Column(String, nullable=True)
    primary_color = Column(String, default="#0066cc")
    secondary_color = Column(String, default="#333333")

    # Contact
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)

    # Custom email configuration (optional, falls back to platform defaults)
    custom_mail_server = Column(String, nullable=True)
    custom_mail_port = Column(Integer, nullable=True)
    custom_mail_username = Column(String, nullable=True)
    custom_mail_password = Column(String, nullable=True)
    custom_mail_from = Column(String, nullable=True)
    custom_mail_tls = Column(Boolean, default=True)

    # User limits
    tenant_admin_limit = Column(Integer, default=5)
    administrator_limit = Column(Integer, default=10)
    sales_engineer_limit = Column(Integer, default=50)
    customer_limit = Column(Integer, default=500)

    # Demo account fields
    is_demo = Column(Boolean, default=False)
    sales_engineers_count = Column(Integer, nullable=True)
    pocs_per_quarter = Column(Integer, nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship(
        "User", back_populates="tenant"
    )  # Deprecated, kept for migration
    user_roles = relationship(
        "UserTenantRole", back_populates="tenant", cascade="all, delete-orphan"
    )
    pocs = relationship("POC", back_populates="tenant")
    tasks = relationship("Task", back_populates="tenant")
    task_groups = relationship("TaskGroup", back_populates="tenant")
    integrations = relationship("TenantIntegration", back_populates="tenant")
    products = relationship("Product", back_populates="tenant")
    poc_public_links = relationship(
        "POCPublicLink", back_populates="tenant", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Tenant {self.name}>"
