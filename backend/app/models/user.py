"""User model"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""
    PLATFORM_ADMIN = "platform_admin"
    TENANT_ADMIN = "tenant_admin"
    ADMINISTRATOR = "administrator"
    SALES_ENGINEER = "sales_engineer"
    CUSTOMER = "customer"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    is_demo = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")  # Deprecated, kept for migration
    tenant_roles = relationship("UserTenantRole", back_populates="user", cascade="all, delete-orphan")
    poc_participations = relationship("POCParticipant", back_populates="user")
    created_pocs = relationship("POC", back_populates="created_by_user", foreign_keys="POC.created_by")
    comments = relationship("Comment", back_populates="user")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user")
    
    def get_role_for_tenant(self, tenant_id: int):
        """Get user's role for a specific tenant"""
        for tenant_role in self.tenant_roles:
            if tenant_role.tenant_id == tenant_id:
                return tenant_role.role
        return None
    
    def get_default_tenant_role(self):
        """Get user's default tenant role"""
        for tenant_role in self.tenant_roles:
            if tenant_role.is_default:
                return tenant_role
        # If no default set, return first one
        return self.tenant_roles[0] if self.tenant_roles else None
    
    def has_role(self, role: "UserRole", tenant_id: int = None) -> bool:
        """Check if user has a specific role in a tenant"""
        if tenant_id is None:
            # Check if user has role in any tenant
            return any(tr.role == role for tr in self.tenant_roles)
        return any(tr.role == role and tr.tenant_id == tenant_id for tr in self.tenant_roles)
    
    def __repr__(self):
        return f"<User {self.email}>"
