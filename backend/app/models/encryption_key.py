"""Encryption key management model"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base


class EncryptionKey(Base):
    """Track encryption keys for key rotation management"""

    __tablename__ = "encryption_keys"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(Integer, nullable=False, index=True)  # Key version number
    key_hash = Column(
        String, nullable=False, index=True
    )  # SHA256 hash for verification
    is_primary = Column(
        Boolean, default=False, index=True
    )  # Current primary key
    is_active = Column(Boolean, default=True)  # Can be used for decryption

    # Track usage
    encrypted_fields_count = Column(
        Integer, default=0
    )  # Fields using this key
    last_rotation_date = Column(DateTime(timezone=True), nullable=True)
    rotation_reason = Column(String, nullable=True)  # Why the key was rotated

    # Metadata
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<EncryptionKey v{self.version} (primary={self.is_primary})>"
