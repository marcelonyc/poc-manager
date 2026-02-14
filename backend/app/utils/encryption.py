"""Encryption utilities for sensitive data with key rotation support"""

import base64
import json
import logging
from datetime import datetime
from typing import Optional, Any
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Manages encryption and decryption with support for key rotation"""

    # Magic bytes to identify encrypted data format and key version
    ENCRYPTED_PREFIX = b"ENC_V"  # ENC_V1, ENC_V2, etc.

    def __init__(
        self, primary_key: str, legacy_keys: Optional[list[str]] = None
    ):
        """
        Initialize the encryption manager.

        Args:
            primary_key: The primary encryption key (base64 encoded or raw)
            legacy_keys: List of legacy keys for decryption during key rotation
        """
        self.primary_key = self._ensure_fernet_key(primary_key)
        self.legacy_keys = [
            self._ensure_fernet_key(key) for key in (legacy_keys or [])
        ]
        self.primary_cipher = Fernet(self.primary_key)
        self.legacy_ciphers = [Fernet(key) for key in self.legacy_keys]

    @staticmethod
    def _ensure_fernet_key(key: str) -> bytes:
        """
        Ensure the key is in valid Fernet format (base64 encoded 32 bytes).

        Args:
            key: Raw key string or base64 encoded key

        Returns:
            Valid Fernet key as bytes
        """
        key_bytes = key.encode() if isinstance(key, str) else key

        # If already base64 encoded (valid Fernet key)
        try:
            decoded = base64.urlsafe_b64decode(key_bytes)
            if len(decoded) == 32:
                return key_bytes
        except Exception:
            pass

        # Generate Fernet key from raw string using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"poc-manager-salt",  # Fixed salt for consistency
            iterations=100000,
            backend=default_backend(),
        )
        key_material = kdf.derive(key_bytes)
        return base64.urlsafe_b64encode(key_material)

    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key.

        Returns:
            Base64 encoded Fernet key
        """
        return Fernet.generate_key().decode()

    def encrypt(self, plaintext: str, key_version: int = 1) -> str:
        """
        Encrypt plaintext and include key version in the result.

        Args:
            plaintext: Data to encrypt
            key_version: Version of the key used (1 = primary, 2+ = legacy)

        Returns:
            Encrypted data with version marker as base64 string
        """
        if not plaintext:
            return ""

        try:
            # Encrypt with primary key
            encrypted = self.primary_cipher.encrypt(plaintext.encode())

            # Add version prefix: ENC_V1<encrypted_data>
            versioned = (
                self.ENCRYPTED_PREFIX + str(key_version).encode() + encrypted
            )

            return base64.urlsafe_b64encode(versioned).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise ValueError(f"Failed to encrypt data: {e}")

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data, automatically handling multiple key versions.

        Args:
            encrypted_data: Base64 encoded encrypted data with version marker

        Returns:
            Decrypted plaintext
        """
        if not encrypted_data:
            return ""

        try:
            # Decode from base64
            versioned = base64.urlsafe_b64decode(encrypted_data.encode())

            # Extract version marker
            if not versioned.startswith(self.ENCRYPTED_PREFIX):
                raise ValueError("Invalid encrypted data format")

            # Extract key version (single digit after prefix)
            key_version = int(chr(versioned[len(self.ENCRYPTED_PREFIX)]))
            encrypted = versioned[len(self.ENCRYPTED_PREFIX) + 1 :]

            # Try with primary key first (version 1)
            if key_version == 1:
                try:
                    return self.primary_cipher.decrypt(encrypted).decode()
                except InvalidToken:
                    pass

            # Try with legacy keys
            for legacy_cipher in self.legacy_ciphers:
                try:
                    return legacy_cipher.decrypt(encrypted).decode()
                except InvalidToken:
                    continue

            raise ValueError("Decryption failed: no valid key found")

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError(f"Failed to decrypt data: {e}")

    def rotate_key(self, new_key: str, encrypted_value: str) -> str:
        """
        Re-encrypt data with a new key.

        Args:
            new_key: New encryption key
            encrypted_value: Currently encrypted value

        Returns:
            Value encrypted with new key
        """
        try:
            # Decrypt with current keys
            plaintext = self.decrypt(encrypted_value)

            # Update to new key
            self.primary_key = self._ensure_fernet_key(new_key)
            self.primary_cipher = Fernet(self.primary_key)

            # Re-encrypt with new key
            return self.encrypt(plaintext, key_version=1)
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            raise ValueError(f"Failed to rotate key: {e}")


class EncryptedField:
    """
    Descriptor for encrypting/decrypting field values automatically.
    Used as a mixin with SQLAlchemy models.
    """

    def __init__(self, field_name: str):
        self.field_name = field_name
        self.encrypted_field_name = f"_{field_name}_encrypted"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.encrypted_field_name, None)

    def __set__(self, obj, value):
        setattr(obj, self.encrypted_field_name, value)


def mask_sensitive_data(data: str, show_chars: int = 2) -> str:
    """
    Mask sensitive data for logging.

    Args:
        data: Sensitive data to mask
        show_chars: Number of characters to show at the end

    Returns:
        Masked string
    """
    if not data or len(data) <= show_chars:
        return "***"
    return "*" * (len(data) - show_chars) + data[-show_chars:]
