"""Encryption key management router"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.services.encryption_service import EncryptionKeyService
from app.utils.encryption import EncryptionManager
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/encryption", tags=["encryption"])


class EncryptionKeyResponse(BaseModel):
    """Response model for encryption key info"""

    version: int
    is_primary: bool
    is_active: bool
    encrypted_fields_count: int = 0
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class KeyRotationRequest(BaseModel):
    """Request to rotate encryption key"""

    reason: str = "maintenance"


class KeyRotationResponse(BaseModel):
    """Response after key rotation"""

    new_version: int
    message: str


@router.get("/keys", response_model=list[EncryptionKeyResponse])
async def get_encryption_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all encryption keys (Platform Admin only).

    Returns information about all encryption keys for auditing and key rotation.
    """
    # Verify user is platform admin
    if current_user.role != "Platform Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only platform admins can access encryption keys",
        )

    service = EncryptionKeyService(db)
    keys = service.get_active_keys()

    return [
        EncryptionKeyResponse(
            version=key.version,
            is_primary=key.is_primary,
            is_active=key.is_active,
            encrypted_fields_count=key.encrypted_fields_count,
            created_at=key.created_at.isoformat() if key.created_at else "",
        )
        for key in keys
    ]


@router.post("/rotate", response_model=KeyRotationResponse)
async def rotate_encryption_key(
    request: KeyRotationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Rotate the encryption key (Platform Admin only).

    This is a critical operation that:
    1. Generates a new encryption key
    2. Marks it as primary
    3. Keeps old keys for decryption during transition

    Important: After rotation, you should:
    - Update ENCRYPTION_KEY in environment variables
    - Keep old keys in ENCRYPTION_LEGACY_KEYS for continued access
    - Re-encrypt existing data with the new key (scheduled task)
    """
    # Verify user is platform admin
    if current_user.role != "Platform Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only platform admins can rotate encryption keys",
        )

    try:
        service = EncryptionKeyService(db)

        # Generate new key
        new_key_value = EncryptionManager.generate_key()

        # Rotate to new key
        new_key = service.rotate_key(
            new_key_value=new_key_value,
            reason=request.reason,
            re_encrypt_count=0,  # Will be updated by background task
        )

        logger.info(
            f"Key rotation initiated by {current_user.email}: "
            f"v{new_key.version} (reason: {request.reason})"
        )

        return KeyRotationResponse(
            new_version=new_key.version,
            message=(
                f"Key rotated successfully to version {new_key.version}. "
                "Update ENCRYPTION_KEY environment variable with the new key value: "
                f"{new_key_value}. "
                "Keep old key in ENCRYPTION_LEGACY_KEYS for gradual re-encryption."
            ),
        )

    except Exception as e:
        logger.error(f"Key rotation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Key rotation failed: {e}",
        )


@router.get("/status")
async def get_encryption_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get encryption system status (Platform Admin only).

    Returns statistics about encryption key usage and system health.
    """
    # Verify user is platform admin
    if current_user.role != "Platform Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only platform admins can view encryption status",
        )

    service = EncryptionKeyService(db)
    stats = service.get_key_statistics()

    return {
        "status": "active",
        "statistics": stats,
        "message": "Encryption system is operational",
    }
