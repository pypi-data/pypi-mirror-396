"""Storage operations for conversations."""

from __future__ import annotations

import json
from pathlib import Path

from artificer.conversations.models import Conversation, ConversationIndex


def get_conversations_dir() -> Path:
    """Get the conversations storage directory."""
    return Path.cwd() / ".artificer" / "conversations"


def ensure_storage_exists() -> None:
    """Ensure the storage directory and index file exist."""
    conversations_dir = get_conversations_dir()
    conversations_dir.mkdir(parents=True, exist_ok=True)

    index_path = conversations_dir / "index.json"
    if not index_path.exists():
        save_index(ConversationIndex())


def load_index() -> ConversationIndex:
    """Load the conversation index."""
    ensure_storage_exists()
    index_path = get_conversations_dir() / "index.json"

    with open(index_path) as f:
        data = json.load(f)

    return ConversationIndex.model_validate(data)


def save_index(index: ConversationIndex) -> None:
    """Save the conversation index."""
    conversations_dir = get_conversations_dir()
    conversations_dir.mkdir(parents=True, exist_ok=True)

    index_path = conversations_dir / "index.json"
    with open(index_path, "w") as f:
        json.dump(index.model_dump(), f, indent=2)


def load_conversation(conversation_id: str) -> Conversation:
    """Load a conversation by ID.

    Args:
        conversation_id: The conversation ID to load.

    Returns:
        The conversation object.

    Raises:
        FileNotFoundError: If the conversation does not exist.
    """
    conversation_path = get_conversations_dir() / f"{conversation_id}.json"

    if not conversation_path.exists():
        raise FileNotFoundError(f"Conversation not found: {conversation_id}")

    with open(conversation_path) as f:
        data = json.load(f)

    return Conversation.model_validate(data)


def save_conversation(conversation: Conversation) -> None:
    """Save a conversation to storage."""
    ensure_storage_exists()
    conversation_path = get_conversations_dir() / f"{conversation.conversation_id}.json"

    with open(conversation_path, "w") as f:
        json.dump(
            conversation.model_dump(mode="json"),
            f,
            indent=2,
            default=str,  # Handle datetime serialization
        )


def add_to_queue(conversation_id: str) -> None:
    """Add a conversation ID to the queue."""
    index = load_index()
    if conversation_id not in index.queue:
        index.queue.append(conversation_id)
        save_index(index)


def pop_from_queue() -> str | None:
    """Pop the first conversation ID from the queue (FIFO).

    Returns:
        The conversation ID, or None if queue is empty.
    """
    index = load_index()
    if not index.queue:
        return None

    conversation_id = index.queue.pop(0)
    save_index(index)
    return conversation_id


def remove_from_queue(conversation_id: str) -> bool:
    """Remove a conversation ID from the queue if present.

    Args:
        conversation_id: The ID to remove.

    Returns:
        True if the ID was in the queue and removed, False otherwise.
    """
    index = load_index()
    if conversation_id in index.queue:
        index.queue.remove(conversation_id)
        save_index(index)
        return True
    return False


def conversation_exists(conversation_id: str) -> bool:
    """Check if a conversation exists."""
    conversation_path = get_conversations_dir() / f"{conversation_id}.json"
    return conversation_path.exists()
