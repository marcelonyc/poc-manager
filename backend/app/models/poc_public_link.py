"""POC Public Link model - for sharing POCs without authentication"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import secrets


class POCPublicLink(Base):
    """POC Public Link model - allows unauthenticated access to a specific POC"""

    __tablename__ = "poc_public_links"

    id = Column(Integer, primary_key=True, index=True)
    poc_id = Column(
        Integer, ForeignKey("pocs.id", ondelete="CASCADE"), nullable=False
    )
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Unique access token
    access_token = Column(String, unique=True, nullable=False, index=True)

    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    poc = relationship("POC", back_populates="public_links")
    tenant = relationship("Tenant", back_populates="poc_public_links")
    created_by_user = relationship(
        "User", back_populates="created_public_links"
    )

    def __repr__(self):
        return f"<POCPublicLink POC:{self.poc_id} Token:{self.access_token[:8]}...>"

    @staticmethod
    def generate_token():
        """Generate a unique access token"""
        return secrets.token_urlsafe(32)
