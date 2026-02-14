"""AI Assistant chat schemas"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class ChatMessageCreate(BaseModel):
    """Schema for sending a chat message"""

    message: str
    session_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    """Schema for a chat message response"""

    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime


class ChatSessionResponse(BaseModel):
    """Schema for chat session info"""

    session_id: str
    created_at: datetime
    last_activity: datetime
    messages: List[ChatMessageResponse] = []


class AIAssistantStatusResponse(BaseModel):
    """Schema for AI assistant status check"""

    enabled: bool
    has_api_key: bool
    message: str
