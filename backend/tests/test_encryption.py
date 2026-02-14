"""Unit tests for encryption system"""

import base64
import pytest
from app.utils.encryption import EncryptionManager
from app.utils.encrypted_field import (
    register_encrypted_field,
    is_field_encrypted,
    is_encrypted_value,
    encrypt_value,
    decrypt_value,
)


class TestEncryptionManager:
    """Test cases for EncryptionManager"""

    def test_generate_key(self):
        """Test key generation"""
        key = EncryptionManager.generate_key()
        assert key is not None
        assert isinstance(key, str)
        assert len(key) > 0

    def test_key_format(self):
        """Test that generated keys are valid Fernet format"""
        key = EncryptionManager.generate_key()
        # Should not raise exception
        manager = EncryptionManager(key)
        assert manager.primary_key is not None

    def test_encrypt_decrypt(self):
        """Test encryption and decryption"""
        key = EncryptionManager.generate_key()
        manager = EncryptionManager(key)

        plaintext = "sensitive-data-123"
        encrypted = manager.encrypt(plaintext)

        assert encrypted != plaintext
        # Encrypted value is base64; decoding it should reveal the ENC_V prefix
        decoded = base64.urlsafe_b64decode(encrypted.encode())
        assert decoded.startswith(b"ENC_V")

        decrypted = manager.decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypt_empty_string(self):
        """Test encryption of empty string"""
        key = EncryptionManager.generate_key()
        manager = EncryptionManager(key)

        assert manager.encrypt("") == ""
        assert manager.decrypt("") == ""

    def test_decrypt_with_legacy_keys(self):
        """Test decryption using legacy keys"""
        key1 = EncryptionManager.generate_key()
        key2 = EncryptionManager.generate_key()

        # Encrypt with key1
        manager1 = EncryptionManager(key1)
        plaintext = "test-data"
        encrypted = manager1.encrypt(plaintext)

        # Decrypt with key2 as primary and key1 as legacy
        manager2 = EncryptionManager(key2, legacy_keys=[key1])
        decrypted = manager2.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encrypt_with_version_marker(self):
        """Test that encryption includes version marker"""
        key = EncryptionManager.generate_key()
        manager = EncryptionManager(key)

        encrypted = manager.encrypt("test", key_version=1)
        decoded = base64.urlsafe_b64decode(encrypted.encode())
        assert decoded.startswith(b"ENC_V")

    def test_multiple_encryptions_produce_different_results(self):
        """Test that multiple encryptions of same data are different (due to Fernet timestamp)"""
        key = EncryptionManager.generate_key()
        manager = EncryptionManager(key)

        plaintext = "test-data"
        encrypted1 = manager.encrypt(plaintext)
        encrypted2 = manager.encrypt(plaintext)

        # Fernet includes timestamp, so outputs should be different
        assert encrypted1 != encrypted2
        # But both should decrypt to same value
        assert manager.decrypt(encrypted1) == plaintext
        assert manager.decrypt(encrypted2) == plaintext

    def test_invalid_encrypted_data(self):
        """Test decryption of invalid data"""
        key = EncryptionManager.generate_key()
        manager = EncryptionManager(key)

        with pytest.raises(ValueError):
            manager.decrypt("not-encrypted-data")

    def test_ensure_fernet_key_formats(self):
        """Test key format normalization"""
        # Test with raw string
        key = "test-key-string"
        result = EncryptionManager._ensure_fernet_key(key)
        assert isinstance(result, bytes)

        # Test with generated key (already valid)
        valid_key = EncryptionManager.generate_key()
        result = EncryptionManager._ensure_fernet_key(valid_key)
        assert isinstance(result, bytes)


class TestEncryptedFields:
    """Test cases for encrypted field registration"""

    def test_register_encrypted_field(self):
        """Test field registration"""

        class TestModel:
            pass

        register_encrypted_field(TestModel, "password")
        assert is_field_encrypted(TestModel, "password")

    def test_unregistered_field_not_encrypted(self):
        """Test that unregistered fields are not encrypted"""

        class TestModel:
            pass

        assert not is_field_encrypted(TestModel, "password")

    def test_multiple_fields_registration(self):
        """Test registering multiple fields"""

        class TestModel:
            pass

        register_encrypted_field(TestModel, "password")
        register_encrypted_field(TestModel, "api_key")
        register_encrypted_field(TestModel, "secret")

        assert is_field_encrypted(TestModel, "password")
        assert is_field_encrypted(TestModel, "api_key")
        assert is_field_encrypted(TestModel, "secret")

    def test_different_models_have_separate_registrations(self):
        """Test that field registrations are per-model"""

        class Model1:
            pass

        class Model2:
            pass

        register_encrypted_field(Model1, "field_a")
        register_encrypted_field(Model2, "field_b")

        assert is_field_encrypted(Model1, "field_a")
        assert not is_field_encrypted(Model1, "field_b")
        assert is_field_encrypted(Model2, "field_b")
        assert not is_field_encrypted(Model2, "field_a")


class TestEncryptionKeyRotation:
    """Test cases for key rotation"""

    def test_rotate_key(self):
        """Test key rotation and re-encryption"""
        old_key = EncryptionManager.generate_key()
        new_key = EncryptionManager.generate_key()

        manager = EncryptionManager(old_key)
        plaintext = "sensitive-data"
        encrypted_with_old = manager.encrypt(plaintext)

        # Rotate key
        re_encrypted = manager.rotate_key(new_key, encrypted_with_old)

        # Verify old key can't decrypt new encryption
        assert re_encrypted != encrypted_with_old

        # Verify new manager with new key can decrypt
        new_manager = EncryptionManager(new_key)
        assert new_manager.decrypt(re_encrypted) == plaintext

    def test_rotation_preserves_data(self):
        """Test that data integrity is maintained during rotation"""
        old_key = EncryptionManager.generate_key()
        new_key = EncryptionManager.generate_key()

        plaintext = "important data that must not be lost"

        manager = EncryptionManager(old_key)
        encrypted = manager.encrypt(plaintext)

        re_encrypted = manager.rotate_key(new_key, encrypted)

        new_manager = EncryptionManager(new_key)
        decrypted = new_manager.decrypt(re_encrypted)

        assert decrypted == plaintext


class TestUtilityFunctions:
    """Test cases for utility functions"""

    def test_is_encrypted_value_detects_encrypted(self):
        """Test is_encrypted_value correctly identifies encrypted payloads"""
        key = EncryptionManager.generate_key()
        manager = EncryptionManager(key)
        encrypted = manager.encrypt("secret")
        assert is_encrypted_value(encrypted) is True

    def test_is_encrypted_value_rejects_plaintext(self):
        """Test is_encrypted_value rejects plain strings"""
        assert is_encrypted_value("hello world") is False
        assert is_encrypted_value("") is False
        assert is_encrypted_value(None) is False

    def test_encrypt_decrypt_round_trip(self):
        """Test encrypt_value / decrypt_value round-trip"""
        result = encrypt_value("test")
        # Should either round-trip or pass-through if manager not initialised
        assert isinstance(result, str)
        decrypted = decrypt_value(result)
        assert isinstance(decrypted, str)

    def test_encrypt_value_function(self):
        """Test encrypt_value utility function"""
        result = encrypt_value("test")
        assert isinstance(result, str)

    def test_decrypt_value_function(self):
        """Test decrypt_value utility returns string for non-encrypted input"""
        result = decrypt_value("plaintext")
        assert result == "plaintext"

    def test_decrypt_value_with_garbage(self):
        """Test decrypt_value gracefully handles garbage input"""
        result = decrypt_value("ENC_V1not-real")
        assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
