"""User-Tenant-Role association model"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.user import UserRole


class UserTenantRole(Base):
    """Association between users, tenants, and roles
    
    This model allows users to be associated with multiple tenants,
    each with a potentially different role.
    """
    __tablename__ = "user_tenant_roles"
    
    __table_args__ = (
        UniqueConstraint('user_id', 'tenant_id', name='uq_user_tenant'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True)
    role = Column(SQLEnum(UserRole), nullable=False, index=True)
    
    # Track if this is the user's primary/default tenant
    is_default = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tenant_roles")
    tenant = relationship("Tenant", back_populates="user_roles")
    
    def __repr__(self):
        return f"<UserTenantRole user_id={self.user_id} tenant_id={self.tenant_id} role={self.role}>"
