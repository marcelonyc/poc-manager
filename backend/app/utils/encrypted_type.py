"""SQLAlchemy custom column types for encrypted fields"""

from typing import Any
from sqlalchemy import String, TypeDecorator
from app.utils.encryption import EncryptionManager


class EncryptedString(TypeDecorator):
    """
    SQLAlchemy type for encrypted string columns.
    Automatically encrypts on save and decrypts on load.
    """

    impl = String
    cache_ok = True

    def __init__(self, encryption_manager: EncryptionManager):
        """
        Initialize encrypted string type.

        Args:
            encryption_manager: Instance of EncryptionManager for crypto operations
        """
        super().__init__()
        self.encryption_manager = encryption_manager

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        """Encrypt value before storing in database"""
        if value is None:
            return None
        if not isinstance(value, str):
            value = str(value)
        return self.encryption_manager.encrypt(value)

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        """Decrypt value when loading from database"""
        if value is None:
            return None
        try:
            return self.encryption_manager.decrypt(value)
        except Exception:
            # If decryption fails, return the raw value
            # This can happen during migration or key rotation issues
            return value
