"""API Keys router"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.auth import get_current_user
from app.schemas.api_key import (
    APIKeyCreate,
    APIKeyExtend,
    APIKeyResponse,
    APIKeyCreated,
)
from app.services.api_key_service import (
    create_api_key,
    list_api_keys,
    delete_api_key,
    extend_api_key,
)

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.get("/", response_model=List[APIKeyResponse])
def get_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all API keys for the current user."""
    keys = list_api_keys(db, current_user.id)
    return keys


@router.post(
    "/", response_model=APIKeyCreated, status_code=status.HTTP_201_CREATED
)
def create_key(
    data: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new API key.

    The raw key is returned **only once** in the response.
    It cannot be retrieved again — prompt the user to store it safely.
    """
    api_key, raw_key = create_api_key(
        db=db,
        user=current_user,
        name=data.name,
        expiration=data.expiration,
    )
    return APIKeyCreated(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        api_key=raw_key,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at,
    )


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an API key."""
    delete_api_key(db, current_user.id, key_id)


@router.post("/{key_id}/extend", response_model=APIKeyResponse)
def extend_key(
    key_id: int,
    data: APIKeyExtend,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Extend the expiration of an existing API key."""
    return extend_api_key(db, current_user.id, key_id, data.expiration)
