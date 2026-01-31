"""POC Invitation model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class POCInvitationStatus(str, enum.Enum):
    """POC invitation status enumeration"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    FAILED = "failed"
    REVOKED = "revoked"


class POCInvitation(Base):
    """POC invitation model for inviting users to participate in a POC"""
    __tablename__ = "poc_invitations"

    id = Column(Integer, primary_key=True, index=True)
    poc_id = Column(Integer, ForeignKey("pocs.id", ondelete="CASCADE"), nullable=False)
    email = Column(String, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    status = Column(SQLEnum(POCInvitationStatus), default=POCInvitationStatus.PENDING, nullable=False)
    
    # Invitation details
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_customer = Column(Boolean, default=True)  # True for customers, False for internal team
    personal_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Email delivery tracking
    email_sent = Column(Boolean, default=False)
    email_error = Column(Text, nullable=True)
    resend_count = Column(Integer, default=0)
    last_resent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    poc = relationship("POC", backref="invitations")
    inviter = relationship("User", foreign_keys=[invited_by])
    
    def __repr__(self):
        return f"<POCInvitation {self.email} to POC:{self.poc_id}>"
