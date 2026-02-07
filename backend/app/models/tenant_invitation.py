"""Tenant invitation model for inviting existing users to additional tenants"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.user import UserRole
import enum


class TenantInvitationStatus(str, enum.Enum):
    """Tenant invitation status enumeration"""

    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


class TenantInvitation(Base):
    """Invitation for existing users to join additional tenants"""

    __tablename__ = "tenant_invitations"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    tenant_id = Column(
        Integer,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(SQLEnum(UserRole), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    status = Column(
        SQLEnum(
            TenantInvitationStatus,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=TenantInvitationStatus.PENDING,
        nullable=False,
    )
    invited_by_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    invited_by_email = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", foreign_keys=[tenant_id])
    invited_by = relationship("User", foreign_keys=[invited_by_user_id])

    def __repr__(self):
        return f"<TenantInvitation {self.email} to tenant {self.tenant_id} as {self.role} - {self.status}>"
