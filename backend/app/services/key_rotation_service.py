"""Service for re-encrypting data with new keys during key rotation"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.tenant import Tenant
from app.models.integration import TenantIntegration
from app.services.encryption_service import EncryptionKeyService
from app.utils.encrypted_field import (
    decrypt_value,
    encrypt_value,
    is_encrypted_value,
)

logger = logging.getLogger(__name__)


class KeyRotationService:
    """Service for handling key rotation and re-encryption of existing data"""

    def __init__(self, db: Session):
        self.db = db
        self.encryption_key_service = EncryptionKeyService(db)

    def re_encrypt_tenant_fields(self) -> dict:
        """
        Re-encrypt all tenant encrypted fields with the new primary key.

        Returns:
            Statistics about the re-encryption process
        """
        stats = {
            "total_tenants": 0,
            "updated_tenants": 0,
            "errors": 0,
            "fields_updated": 0,
        }

        try:
            tenants = self.db.query(Tenant).all()
            stats["total_tenants"] = len(tenants)

            for tenant in tenants:
                try:
                    updated = False

                    # Re-encrypt custom_mail_password
                    if tenant.custom_mail_password:
                        parsed = decrypt_value(tenant.custom_mail_password)
                        if parsed != tenant.custom_mail_password:
                            tenant.custom_mail_password = encrypt_value(parsed)
                            updated = True
                            stats["fields_updated"] += 1

                    # Re-encrypt custom_mail_username
                    if tenant.custom_mail_username:
                        parsed = decrypt_value(tenant.custom_mail_username)
                        if parsed != tenant.custom_mail_username:
                            tenant.custom_mail_username = encrypt_value(parsed)
                            updated = True
                            stats["fields_updated"] += 1

                    # Re-encrypt ollama_api_key
                    if tenant.ollama_api_key:
                        parsed = decrypt_value(tenant.ollama_api_key)
                        if parsed != tenant.ollama_api_key:
                            tenant.ollama_api_key = encrypt_value(parsed)
                            updated = True
                            stats["fields_updated"] += 1

                    if updated:
                        tenant.updated_at = datetime.utcnow()
                        self.db.add(tenant)
                        stats["updated_tenants"] += 1

                except Exception as e:
                    logger.error(
                        f"Failed to re-encrypt tenant {tenant.id}: {e}"
                    )
                    stats["errors"] += 1

            self.db.commit()
            logger.info(
                f"Tenant re-encryption complete: {stats['updated_tenants']} "
                f"tenants with {stats['fields_updated']} fields updated"
            )

        except Exception as e:
            logger.error(f"Tenant re-encryption failed: {e}")
            self.db.rollback()
            stats["errors"] += 1

        return stats

    def re_encrypt_integration_configs(self) -> dict:
        """
        Re-encrypt all integration config_data with the new primary key.

        Returns:
            Statistics about the re-encryption process
        """
        stats = {
            "total_integrations": 0,
            "updated_integrations": 0,
            "errors": 0,
            "fields_updated": 0,
        }

        try:
            integrations = self.db.query(TenantIntegration).all()
            stats["total_integrations"] = len(integrations)

            for integration in integrations:
                try:
                    if integration.config_data:
                        parsed = decrypt_value(integration.config_data)
                        if parsed != integration.config_data:
                            integration.config_data = encrypt_value(parsed)
                            integration.updated_at = datetime.utcnow()
                            self.db.add(integration)
                            stats["updated_integrations"] += 1
                            stats["fields_updated"] += 1

                except Exception as e:
                    logger.error(
                        f"Failed to re-encrypt integration {integration.id}: {e}"
                    )
                    stats["errors"] += 1

            self.db.commit()
            logger.info(
                f"Integration re-encryption complete: {stats['updated_integrations']} "
                f"integrations updated"
            )

        except Exception as e:
            logger.error(f"Integration re-encryption failed: {e}")
            self.db.rollback()
            stats["errors"] += 1

        return stats

    def re_encrypt_all(self) -> dict:
        """
        Re-encrypt all encrypted fields in the system.

        Returns:
            Combined statistics from all re-encryption operations
        """
        logger.info("Starting full system re-encryption for key rotation")

        tenant_stats = self.re_encrypt_tenant_fields()
        integration_stats = self.re_encrypt_integration_configs()

        combined_stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "tenants": tenant_stats,
            "integrations": integration_stats,
            "total_fields_updated": (
                tenant_stats["fields_updated"]
                + integration_stats["fields_updated"]
            ),
            "total_errors": tenant_stats["errors"]
            + integration_stats["errors"],
        }

        # Update encryption key statistics
        primary_key = self.encryption_key_service.get_primary_key()
        if primary_key:
            primary_key.encrypted_fields_count = combined_stats[
                "total_fields_updated"
            ]
            self.db.add(primary_key)
            self.db.commit()

        logger.info(
            f"Full re-encryption complete: {combined_stats['total_fields_updated']} "
            f"fields updated with {combined_stats['total_errors']} errors"
        )

        return combined_stats

    def verify_encryption_data(self) -> dict:
        """
        Verify that encrypted data can be decrypted (system health check).

        Returns:
            Verification results with any problematic fields
        """
        results = {
            "total_encrypted_fields": 0,
            "successfully_decrypted": 0,
            "decryption_failures": 0,
            "problematic_fields": [],
        }

        try:
            # Check tenant encrypted fields
            tenants = (
                self.db.query(Tenant)
                .filter(
                    and_(
                        (Tenant.custom_mail_password.isnot(None))
                        | (Tenant.custom_mail_username.isnot(None))
                        | (Tenant.ollama_api_key.isnot(None))
                    )
                )
                .all()
            )

            for tenant in tenants:
                for field_name in [
                    "custom_mail_password",
                    "custom_mail_username",
                    "ollama_api_key",
                ]:
                    value = getattr(tenant, field_name, None)
                    if (
                        value
                        and isinstance(value, str)
                        and is_encrypted_value(value)
                    ):
                        results["total_encrypted_fields"] += 1
                        try:
                            decrypt_value(value)
                            results["successfully_decrypted"] += 1
                        except Exception as e:
                            results["decryption_failures"] += 1
                            results["problematic_fields"].append(
                                {
                                    "model": "Tenant",
                                    "id": tenant.id,
                                    "field": field_name,
                                    "error": str(e),
                                }
                            )

            # Check integration encrypted fields
            integrations = (
                self.db.query(TenantIntegration)
                .filter(TenantIntegration.config_data.isnot(None))
                .all()
            )

            for integration in integrations:
                if integration.config_data and isinstance(
                    integration.config_data, str
                ):
                    if is_encrypted_value(integration.config_data):
                        results["total_encrypted_fields"] += 1
                        try:
                            decrypt_value(integration.config_data)
                            results["successfully_decrypted"] += 1
                        except Exception as e:
                            results["decryption_failures"] += 1
                            results["problematic_fields"].append(
                                {
                                    "model": "TenantIntegration",
                                    "id": integration.id,
                                    "field": "config_data",
                                    "error": str(e),
                                }
                            )

            logger.info(
                f"Encryption verification: {results['successfully_decrypted']}/{results['total_encrypted_fields']} "
                f"fields verified"
            )

        except Exception as e:
            logger.error(f"Encryption verification failed: {e}")

        return results
