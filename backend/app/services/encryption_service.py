"""Encryption key rotation and management service"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.encryption_key import EncryptionKey
from app.utils.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class EncryptionKeyService:
    """Service for managing encryption keys and rotations"""

    def __init__(self, db: Session):
        self.db = db

    def create_encryption_key(
        self,
        key_value: str,
        version: int,
        is_primary: bool = False,
        description: Optional[str] = None,
    ) -> EncryptionKey:
        """
        Create a new encryption key record.

        Args:
            key_value: The actual encryption key
            version: Version number for tracking
            is_primary: Whether this is the primary key
            description: Optional description

        Returns:
            Created EncryptionKey instance
        """
        # Generate hash of the key for verification
        key_hash = hashlib.sha256(key_value.encode()).hexdigest()

        # If setting as primary, unset current primary
        if is_primary:
            current_primary = (
                self.db.query(EncryptionKey)
                .filter(EncryptionKey.is_primary == True)
                .first()
            )
            if current_primary:
                current_primary.is_primary = False
                self.db.add(current_primary)

        encryption_key = EncryptionKey(
            version=version,
            key_hash=key_hash,
            is_primary=is_primary,
            is_active=True,
            description=description,
        )

        self.db.add(encryption_key)
        self.db.commit()
        self.db.refresh(encryption_key)

        logger.info(
            f"Created encryption key v{version} (primary={is_primary})"
        )
        return encryption_key

    def get_primary_key(self) -> Optional[EncryptionKey]:
        """Get the current primary encryption key"""
        return (
            self.db.query(EncryptionKey)
            .filter(EncryptionKey.is_primary == True)
            .first()
        )

    def get_active_keys(self) -> list[EncryptionKey]:
        """Get all active keys (for decryption during rotation)"""
        return (
            self.db.query(EncryptionKey)
            .filter(EncryptionKey.is_active == True)
            .order_by(EncryptionKey.version.desc())
            .all()
        )

    def rotate_key(
        self,
        new_key_value: str,
        reason: Optional[str] = None,
        re_encrypt_count: int = 0,
    ) -> EncryptionKey:
        """
        Rotate to a new primary encryption key.

        Args:
            new_key_value: The new encryption key
            reason: Reason for rotation (periodic, compromise, etc.)
            re_encrypt_count: Number of fields re-encrypted

        Returns:
            New primary EncryptionKey
        """
        # Get current version
        max_version = (
            self.db.query(EncryptionKey)
            .order_by(EncryptionKey.version.desc())
            .first()
        )
        new_version = (max_version.version if max_version else 0) + 1

        # Create new primary key
        new_key = self.create_encryption_key(
            key_value=new_key_value,
            version=new_version,
            is_primary=True,
            description=f"Rotated key (reason: {reason or 'maintenance'})",
        )

        # Update previous primary key
        old_primary = (
            self.db.query(EncryptionKey)
            .filter(
                EncryptionKey.is_primary == False,
                EncryptionKey.version == new_version - 1,
            )
            .first()
        )
        if old_primary:
            old_primary.is_primary = False
            old_primary.last_rotation_date = datetime.now(timezone.utc)
            old_primary.rotation_reason = reason
            old_primary.encrypted_fields_count = re_encrypt_count
            self.db.add(old_primary)
            self.db.commit()

        logger.info(
            f"Key rotation completed: v{new_version} (reason: {reason or 'maintenance'})"
        )
        return new_key

    def deactivate_key(self, version: int) -> Optional[EncryptionKey]:
        """
        Deactivate an old key (prevent decryption with it).

        Args:
            version: Version of key to deactivate

        Returns:
            Deactivated EncryptionKey or None
        """
        key = (
            self.db.query(EncryptionKey)
            .filter(EncryptionKey.version == version)
            .first()
        )

        if key and not key.is_primary:
            key.is_active = False
            self.db.add(key)
            self.db.commit()
            logger.info(f"Deactivated encryption key v{version}")
            return key

        return None

    def verify_key(self, key_value: str, version: int) -> bool:
        """
        Verify that a key matches the stored hash for a version.

        Args:
            key_value: The key to verify
            version: Version to check against

        Returns:
            True if key hash matches
        """
        key_hash = hashlib.sha256(key_value.encode()).hexdigest()
        stored_key = (
            self.db.query(EncryptionKey)
            .filter(EncryptionKey.version == version)
            .first()
        )

        if stored_key:
            return stored_key.key_hash == key_hash
        return False

    def get_key_statistics(self) -> dict:
        """Get encryption key statistics"""
        total_keys = self.db.query(EncryptionKey).count()
        active_keys = (
            self.db.query(EncryptionKey)
            .filter(EncryptionKey.is_active == True)
            .count()
        )
        primary_key = self.get_primary_key()

        return {
            "total_keys": total_keys,
            "active_keys": active_keys,
            "primary_version": primary_key.version if primary_key else None,
            "created_at": primary_key.created_at if primary_key else None,
        }
