"""Encrypted field management using SQLAlchemy event listeners"""

import base64
import logging
from typing import Optional, Set, Dict, Tuple, Any
from sqlalchemy import event
from sqlalchemy.orm import Session, Mapper
from sqlalchemy.inspection import inspect
from app.utils.encryption import EncryptionManager

logger = logging.getLogger(__name__)

# Registry of encrypted fields: {ModelClass: {field_name: encryption_marker}}
ENCRYPTED_FIELDS_REGISTRY: Dict[Any, Set[str]] = {}


def is_encrypted_value(value: str) -> bool:
    """
    Check whether a string is an encrypted payload produced by EncryptionManager.

    Encrypted values are base64-encoded wrappers around the ``ENC_V<n>`` prefix.
    Plaintext will never decode to something that starts with this prefix.
    """
    if not value or not isinstance(value, str):
        return False
    try:
        decoded = base64.urlsafe_b64decode(value.encode())
        return decoded.startswith(EncryptionManager.ENCRYPTED_PREFIX)
    except Exception:
        return False


def register_encrypted_field(model_class: Any, field_name: str) -> None:
    """
    Register a model field as encrypted.

    Args:
        model_class: SQLAlchemy model class
        field_name: Name of the field to encrypt
    """
    if model_class not in ENCRYPTED_FIELDS_REGISTRY:
        ENCRYPTED_FIELDS_REGISTRY[model_class] = set()
    ENCRYPTED_FIELDS_REGISTRY[model_class].add(field_name)


def is_field_encrypted(model_class: Any, field_name: str) -> bool:
    """Check if a field is registered as encrypted"""
    return (
        model_class in ENCRYPTED_FIELDS_REGISTRY
        and field_name in ENCRYPTED_FIELDS_REGISTRY[model_class]
    )


def get_encryption_manager():
    """
    Get the global encryption manager instance.
    This must be called after the app is initialized with config.
    """
    # Import here to avoid circular imports
    try:
        from app.config import settings

        if not hasattr(settings, "_encryption_manager"):
            settings._encryption_manager = settings.get_encryption_manager()
        return settings._encryption_manager
    except Exception as e:
        logger.error(f"Failed to get encryption manager: {e}")
        return None


def setup_encryption_listeners() -> None:
    """
    Setup SQLAlchemy event listeners for automatic encryption/decryption.
    Call this during app initialization.
    """

    @event.listens_for(Session, "before_flush")
    def encrypt_before_insert_update(session, flush_context, instances):
        """Encrypt fields before INSERT/UPDATE"""
        encryption_manager = get_encryption_manager()
        if not encryption_manager:
            return

        for obj in session.new.union(session.dirty):
            model_class = type(obj)
            if model_class not in ENCRYPTED_FIELDS_REGISTRY:
                continue

            for field_name in ENCRYPTED_FIELDS_REGISTRY[model_class]:
                value = getattr(obj, field_name, None)
                if (
                    value
                    and isinstance(value, str)
                    and not is_encrypted_value(value)
                ):
                    try:
                        encrypted_value = encryption_manager.encrypt(value)
                        setattr(obj, field_name, encrypted_value)
                        logger.debug(
                            f"Encrypted {model_class.__name__}.{field_name}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to encrypt {model_class.__name__}.{field_name}: {e}"
                        )

    # Use mapper events for insert/update operations
    @event.listens_for(Mapper, "after_insert", propagate=True)
    @event.listens_for(Mapper, "after_update", propagate=True)
    def decrypt_after_db_operation(mapper, connection, target):
        """Decrypt objects after INSERT/UPDATE"""
        encryption_manager = get_encryption_manager()
        if not encryption_manager:
            return

        model_class = type(target)
        if model_class not in ENCRYPTED_FIELDS_REGISTRY:
            return

        for field_name in ENCRYPTED_FIELDS_REGISTRY[model_class]:
            value = getattr(target, field_name, None)
            if value and isinstance(value, str) and is_encrypted_value(value):
                try:
                    decrypted_value = encryption_manager.decrypt(value)
                    object.__setattr__(target, field_name, decrypted_value)
                    logger.debug(
                        f"Decrypted {model_class.__name__}.{field_name}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to decrypt {model_class.__name__}.{field_name}: {e}"
                    )


def decrypt_value(value: str) -> str:
    """
    Utility function to decrypt a value outside of ORM context.

    Args:
        value: Encrypted value to decrypt

    Returns:
        Decrypted value
    """
    if not value or not isinstance(value, str):
        return value

    if not is_encrypted_value(value):
        return value

    encryption_manager = get_encryption_manager()
    if not encryption_manager:
        return value

    try:
        return encryption_manager.decrypt(value)
    except Exception as e:
        logger.error(f"Failed to decrypt value: {e}")
        return value


def encrypt_value(value: str) -> str:
    """
    Utility function to encrypt a value outside of ORM context.

    Args:
        value: Plain text value to encrypt

    Returns:
        Encrypted value
    """
    if not value or not isinstance(value, str):
        return value

    encryption_manager = get_encryption_manager()
    if not encryption_manager:
        return value

    try:
        return encryption_manager.encrypt(value)
    except Exception as e:
        logger.error(f"Failed to encrypt value: {e}")
        return value
