"""AI Assistant chat router"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionResponse,
    AIAssistantStatusResponse,
)
from app.auth import (
    get_current_user,
    get_current_tenant_id,
    security,
)
from app.services.ai_assistant import (
    get_or_create_session,
    chat_with_assistant,
    close_session,
    reset_session,
    is_mcp_configured,
)
from app.utils import decrypt_value
from datetime import datetime

router = APIRouter(prefix="/ai-assistant", tags=["AI Assistant"])


def _get_tenant_or_404(db: Session, tenant_id: int) -> Tenant:
    """Helper to get tenant or raise 404."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    return tenant


def _check_not_customer(user: User):
    """AI assistant is not available for customers."""
    current_role = getattr(user, "_current_role", user.role)
    if current_role == UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI Assistant is not available for customer users",
        )


@router.get("/status", response_model=AIAssistantStatusResponse)
def get_ai_assistant_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Check AI Assistant availability for the current tenant.

    Returns whether the AI Assistant feature is enabled and properly
    configured for the caller's tenant. Provides actionable messages
    based on the caller's role when the feature is not ready.

    Route: GET /ai-assistant/status

    Returns:
        AI assistant status object containing:
            - enabled (bool): Whether AI Assistant is enabled for this tenant.
            - has_api_key (bool): Whether the Ollama API key is configured.
            - message (str): Human-readable status message with guidance.

    Errors:
        403 Forbidden: Customer users cannot access the AI assistant.
        401 Unauthorized: Missing or invalid authentication token.
    """
    _check_not_customer(current_user)

    if not tenant_id:
        return AIAssistantStatusResponse(
            enabled=False,
            has_api_key=False,
            message="No tenant context available",
        )

    tenant = _get_tenant_or_404(db, tenant_id)

    if not tenant.ai_assistant_enabled:
        current_role = getattr(
            current_user, "_current_role", current_user.role
        )
        if current_role == UserRole.TENANT_ADMIN:
            return AIAssistantStatusResponse(
                enabled=False,
                has_api_key=bool(tenant.ollama_api_key),
                message="AI Assistant is not enabled. Go to Settings to enable it.",
            )
        return AIAssistantStatusResponse(
            enabled=False,
            has_api_key=False,
            message="AI Assistant is not enabled. Contact your Tenant Admin to enable it.",
        )

    if not tenant.ollama_api_key:
        return AIAssistantStatusResponse(
            enabled=True,
            has_api_key=False,
            message="AI Assistant is enabled but Ollama API key is not configured.",
        )

    if not is_mcp_configured():
        return AIAssistantStatusResponse(
            enabled=True,
            has_api_key=True,
            message="AI Assistant is enabled but MCP tools are not configured. Set MCP_TOOLS in the environment.",
        )

    return AIAssistantStatusResponse(
        enabled=True,
        has_api_key=True,
        message="AI Assistant is ready to use.",
    )


@router.post("/chat", response_model=ChatSessionResponse)
async def send_chat_message(
    message_data: ChatMessageCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Send a message to the AI Assistant and receive a response.

    The chat session maintains conversation history. Pass session_id
    to continue an existing conversation, or omit it to start a new one.
    Sessions time out after 10 minutes of inactivity.
    """
    _check_not_customer(current_user)

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tenant context available",
        )

    tenant = _get_tenant_or_404(db, tenant_id)

    if not tenant.ai_assistant_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI Assistant is not enabled for this tenant",
        )

    if not tenant.ollama_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ollama API key is not configured",
        )

    if not is_mcp_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Assistant requires MCP tools but MCP_TOOLS is not configured",
        )

    # Get or create chat session
    session = get_or_create_session(
        session_id=message_data.session_id,
        user_id=current_user.id,
        tenant_id=tenant_id,
    )

    # Get the user's JWT token to pass to MCP tools for RBAC
    user_token = credentials.credentials

    # Chat with the assistant
    decrypted_api_key = decrypt_value(tenant.ollama_api_key)

    response_text = await chat_with_assistant(
        session=session,
        user_message=message_data.message,
        ollama_api_key=decrypted_api_key,
        user_token=user_token,
    )

    # Build response
    messages = [
        ChatMessageResponse(
            role=msg["role"],
            content=msg["content"],
            timestamp=msg["timestamp"],
        )
        for msg in session["messages"]
    ]

    return ChatSessionResponse(
        session_id=session["session_id"],
        created_at=session["created_at"],
        last_activity=session["last_activity"],
        messages=messages,
    )


@router.post("/chat/new", response_model=ChatSessionResponse)
def start_new_chat(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
    session_id: str | None = None,
):
    """
    Start a new chat session, clearing the previous one if it exists.

    Accepts an optional session_id query parameter to close the old session.
    Returns a fresh, empty session.
    """
    _check_not_customer(current_user)

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tenant context available",
        )

    new_session = reset_session(
        session_id=session_id,
        user_id=current_user.id,
        tenant_id=tenant_id,
    )

    return ChatSessionResponse(
        session_id=new_session["session_id"],
        created_at=new_session["created_at"],
        last_activity=new_session["last_activity"],
        messages=[],
    )


@router.delete("/chat/{session_id}")
def close_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Close a chat session.

    Removes all conversation history for the given session.
    """
    _check_not_customer(current_user)

    closed = close_session(session_id)
    if not closed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found or already closed",
        )

    return {"message": "Chat session closed"}
