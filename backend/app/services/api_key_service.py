"""API Key service — generation, validation, lifecycle management"""

import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.auth import pwd_context
from app.models.api_key import APIKey
from app.models.user import User
from app.schemas.api_key import APIKeyExpiration

logger = logging.getLogger(__name__)

MAX_KEYS_PER_USER = 3

EXPIRATION_DELTAS = {
    APIKeyExpiration.SIX_MONTHS: timedelta(days=182),
    APIKeyExpiration.ONE_YEAR: timedelta(days=365),
    APIKeyExpiration.TWO_YEARS: timedelta(days=730),
}


def _generate_raw_key() -> str:
    """Generate a cryptographically-secure random API key (48 bytes, url-safe)."""
    return f"pocm_{secrets.token_urlsafe(48)}"


def _hash_key(raw_key: str) -> str:
    """Hash an API key using bcrypt (same hasher used for passwords)."""
    return pwd_context.hash(raw_key)


def _verify_key(raw_key: str, hashed: str) -> bool:
    """Verify a raw API key against its bcrypt hash."""
    return pwd_context.verify(raw_key, hashed)


def create_api_key(
    db: Session,
    user: User,
    name: str,
    expiration: APIKeyExpiration,
) -> tuple[APIKey, str]:
    """
    Create a new API key for a user.

    Returns:
        Tuple of (APIKey model instance, raw_key string).
        The raw key is only available at creation time.
    """
    # Enforce max keys limit
    active_count = (
        db.query(APIKey)
        .filter(APIKey.user_id == user.id, APIKey.is_active == True)
        .count()
    )
    if active_count >= MAX_KEYS_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum of {MAX_KEYS_PER_USER} active API keys allowed. Delete an existing key first.",
        )

    raw_key = _generate_raw_key()
    key_hash = _hash_key(raw_key)
    key_prefix = raw_key[:8]
    expires_at = datetime.now(timezone.utc) + EXPIRATION_DELTAS[expiration]

    api_key = APIKey(
        user_id=user.id,
        name=name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        expires_at=expires_at,
        is_active=True,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    logger.info(f"API key created for user {user.id} (prefix={key_prefix})")
    return api_key, raw_key


def list_api_keys(db: Session, user_id: int) -> list[APIKey]:
    """List all API keys for a user (active and inactive)."""
    return (
        db.query(APIKey)
        .filter(APIKey.user_id == user_id)
        .order_by(APIKey.created_at.desc())
        .all()
    )


def delete_api_key(db: Session, user_id: int, key_id: int) -> None:
    """Delete (deactivate) an API key."""
    api_key = (
        db.query(APIKey)
        .filter(APIKey.id == key_id, APIKey.user_id == user_id)
        .first()
    )
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    db.delete(api_key)
    db.commit()
    logger.info(f"API key {key_id} deleted for user {user_id}")


def extend_api_key(
    db: Session,
    user_id: int,
    key_id: int,
    expiration: APIKeyExpiration,
) -> APIKey:
    """Extend the expiration of an existing API key."""
    api_key = (
        db.query(APIKey)
        .filter(
            APIKey.id == key_id,
            APIKey.user_id == user_id,
            APIKey.is_active == True,
        )
        .first()
    )
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active API key not found",
        )

    # Extend from current expiration or from now, whichever is later
    base = max(api_key.expires_at, datetime.now(timezone.utc))
    api_key.expires_at = base + EXPIRATION_DELTAS[expiration]
    db.commit()
    db.refresh(api_key)

    logger.info(
        f"API key {key_id} extended for user {user_id}, new expiry: {api_key.expires_at}"
    )
    return api_key


def authenticate_api_key(db: Session, raw_key: str) -> Optional[User]:
    """
    Authenticate a request using an API key.

    Returns the User if the key is valid and not expired, otherwise None.
    """
    if not raw_key:
        return None

    prefix = raw_key[:8]

    # Look up candidate keys by prefix (efficient narrowing)
    candidates = (
        db.query(APIKey)
        .filter(APIKey.key_prefix == prefix, APIKey.is_active == True)
        .all()
    )

    now = datetime.now(timezone.utc)
    for candidate in candidates:
        if candidate.expires_at < now:
            continue
        if _verify_key(raw_key, candidate.key_hash):
            # Update last_used_at
            candidate.last_used_at = now
            db.commit()

            # Load the user
            user = db.query(User).filter(User.id == candidate.user_id).first()
            return user

    return None
