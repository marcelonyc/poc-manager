"""Invitation model for Platform Admin invites"""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.sql import func
from app.database import Base
import enum


class InvitationStatus(str, enum.Enum):
    """Invitation status enumeration"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class Invitation(Base):
    """Invitation model for Platform Admin invitations"""
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    status = Column(SQLEnum(InvitationStatus, values_callable=lambda x: [e.value for e in x]), default=InvitationStatus.PENDING, nullable=False)
    invited_by_email = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Invitation {self.email} - {self.status}>"
