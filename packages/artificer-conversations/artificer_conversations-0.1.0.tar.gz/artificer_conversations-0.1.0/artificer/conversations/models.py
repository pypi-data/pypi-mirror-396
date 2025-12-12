"""Data models for conversations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Conversation(BaseModel):
    """A single conversation request."""

    conversation_id: str = Field(description="Unique identifier for the conversation")
    prompt: str = Field(description="The conversation prompt/request")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the conversation was created",
    )
    workflow_id: str | None = Field(
        default=None, description="Optional workflow ID that created this conversation"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ConversationIndex(BaseModel):
    """Index tracking the conversation queue."""

    queue: list[str] = Field(
        default_factory=list, description="List of queued conversation IDs (FIFO)"
    )
