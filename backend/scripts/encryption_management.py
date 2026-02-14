#!/usr/bin/env python
"""
CLI tool for managing encryption keys and performing key rotation.

Usage:
    python backend/scripts/encryption_management.py generate-key
    python backend/scripts/encryption_management.py rotate --reason "scheduled maintenance"
    python backend/scripts/encryption_management.py verify
    python backend/scripts/encryption_management.py re-encrypt
    python backend/scripts/encryption_management.py status
"""

import sys
import argparse
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.services.encryption_service import EncryptionKeyService
from app.services.key_rotation_service import KeyRotationService
from app.utils.encryption import EncryptionManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def generate_key(args):
    """Generate a new encryption key"""
    key = EncryptionManager.generate_key()
    print("\n" + "=" * 80)
    print("NEW ENCRYPTION KEY GENERATED")
    print("=" * 80)
    print(f"\nKey:\n{key}\n")
    print("Copy this key to your .env file as ENCRYPTION_KEY")
    print("If rotating, add the old key to ENCRYPTION_LEGACY_KEYS")
    print("=" * 80 + "\n")


def rotate_key(args):
    """Rotate to a new encryption key"""
    db = SessionLocal()
    try:
        reason = args.reason or "scheduled maintenance"

        print(f"\n{'='*80}")
        print("ROTATING ENCRYPTION KEY")
        print(f"{'='*80}")

        service = EncryptionKeyService(db)

        # Generate new key
        new_key_value = EncryptionManager.generate_key()
        print(f"\nGenerated new key...")

        # Rotate
        new_key = service.rotate_key(
            new_key_value=new_key_value, reason=reason, re_encrypt_count=0
        )

        print(f"\nRotation successful!")
        print(f"New key version: {new_key.version}")
        print(f"Previous version: {new_key.version - 1}")
        print(f"Reason: {reason}")

        print(f"\n{'='*80}")
        print("NEXT STEPS:")
        print(f"{'='*80}")
        print(f"1. Update environment variable:")
        print(f"   ENCRYPTION_KEY={new_key_value}")
        print(f"\n2. Update legacy keys to include previous primary:")
        print(f"   ENCRYPTION_LEGACY_KEYS=<previous-primary-key>")
        print(f"\n3. Restart the application")
        print(f"\n4. Re-encrypt existing data:")
        print(f"   python backend/scripts/encryption_management.py re-encrypt")
        print(f"\n5. Verify encryption system:")
        print(f"   python backend/scripts/encryption_management.py verify")
        print(f"{'='*80}\n")

    finally:
        db.close()


def re_encrypt(args):
    """Re-encrypt all data with new key"""
    db = SessionLocal()
    try:
        print(f"\n{'='*80}")
        print("RE-ENCRYPTING DATA WITH NEW KEY")
        print(f"{'='*80}\n")

        service = KeyRotationService(db)
        stats = service.re_encrypt_all()

        print(f"Re-encryption complete!")
        print(
            f"\nTenant fields updated: {stats['tenants']['updated_tenants']}"
        )
        print(f"  Total tenants: {stats['tenants']['total_tenants']}")
        print(f"  Fields: {stats['tenants']['fields_updated']}")
        print(f"  Errors: {stats['tenants']['errors']}")

        print(
            f"\nIntegration configs updated: {stats['integrations']['updated_integrations']}"
        )
        print(
            f"  Total integrations: {stats['integrations']['total_integrations']}"
        )
        print(f"  Fields: {stats['integrations']['fields_updated']}")
        print(f"  Errors: {stats['integrations']['errors']}")

        print(f"\nTotal fields updated: {stats['total_fields_updated']}")
        print(f"Total errors: {stats['total_errors']}")
        print(f"Timestamp: {stats['timestamp']}")
        print(f"{'='*80}\n")

    finally:
        db.close()


def verify(args):
    """Verify encryption system integrity"""
    db = SessionLocal()
    try:
        print(f"\n{'='*80}")
        print("VERIFYING ENCRYPTION SYSTEM")
        print(f"{'='*80}\n")

        service = KeyRotationService(db)
        results = service.verify_encryption_data()

        print(f"Total encrypted fields: {results['total_encrypted_fields']}")
        print(f"Successfully decrypted: {results['successfully_decrypted']}")
        print(f"Decryption failures: {results['decryption_failures']}")

        if results["problematic_fields"]:
            print(f"\n⚠️  PROBLEMATIC FIELDS FOUND:")
            for field in results["problematic_fields"]:
                print(f"\n  Model: {field['model']}")
                print(f"  ID: {field['id']}")
                print(f"  Field: {field['field']}")
                print(f"  Error: {field['error']}")
        else:
            print(f"\n✓ All encrypted fields verified successfully!")

        print(f"{'='*80}\n")

    finally:
        db.close()


def status(args):
    """Show encryption system status"""
    db = SessionLocal()
    try:
        print(f"\n{'='*80}")
        print("ENCRYPTION SYSTEM STATUS")
        print(f"{'='*80}\n")

        service = EncryptionKeyService(db)
        stats = service.get_key_statistics()

        print(f"Total keys: {stats['total_keys']}")
        print(f"Active keys: {stats['active_keys']}")
        print(f"Primary key version: {stats['primary_version']}")
        print(f"Created: {stats['created_at']}")

        print(f"\nAll keys:")
        keys = service.get_active_keys()
        for key in keys:
            status_str = "🔐 PRIMARY" if key.is_primary else "   LEGACY "
            active_str = "✓ ACTIVE" if key.is_active else "✗ INACTIVE"
            print(
                f"  v{key.version}: {status_str} {active_str} "
                f"(fields: {key.encrypted_fields_count})"
            )

        print(f"{'='*80}\n")

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Encryption key management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a new key
  python backend/scripts/encryption_management.py generate-key
  
  # Rotate to new key
  python backend/scripts/encryption_management.py rotate --reason "scheduled maintenance"
  
  # Re-encrypt data with new key
  python backend/scripts/encryption_management.py re-encrypt
  
  # Verify encryption integrity
  python backend/scripts/encryption_management.py verify
  
  # Show encryption status
  python backend/scripts/encryption_management.py status
        """,
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Command to execute"
    )

    # generate-key command
    subparsers.add_parser("generate-key", help="Generate a new encryption key")

    # rotate command
    rotate_parser = subparsers.add_parser(
        "rotate", help="Rotate to a new encryption key"
    )
    rotate_parser.add_argument(
        "--reason",
        help="Reason for key rotation",
        default="scheduled maintenance",
    )

    # re-encrypt command
    subparsers.add_parser(
        "re-encrypt", help="Re-encrypt all data with new key"
    )

    # verify command
    subparsers.add_parser("verify", help="Verify encryption system integrity")

    # status command
    subparsers.add_parser("status", help="Show encryption system status")

    args = parser.parse_args()

    if args.command == "generate-key":
        generate_key(args)
    elif args.command == "rotate":
        rotate_key(args)
    elif args.command == "re-encrypt":
        re_encrypt(args)
    elif args.command == "verify":
        verify(args)
    elif args.command == "status":
        status(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
