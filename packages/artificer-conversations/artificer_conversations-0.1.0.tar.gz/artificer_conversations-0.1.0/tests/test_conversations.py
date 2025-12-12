"""Tests for artificer-conversations."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from artificer.conversations.models import Conversation, ConversationIndex
from artificer.conversations.storage import (
    add_to_queue,
    conversation_exists,
    ensure_storage_exists,
    get_conversations_dir,
    load_conversation,
    load_index,
    pop_from_queue,
    remove_from_queue,
    save_conversation,
    save_index,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, "cwd", return_value=Path(tmpdir)):
            yield Path(tmpdir)


class TestModels:
    """Tests for data models."""

    def test_conversation_creation(self):
        """Test creating a Conversation."""
        conv = Conversation(
            conversation_id="test-123",
            prompt="Hello world",
        )
        assert conv.conversation_id == "test-123"
        assert conv.prompt == "Hello world"
        assert conv.workflow_id is None
        assert conv.metadata == {}
        assert conv.created_at is not None

    def test_conversation_with_workflow(self):
        """Test Conversation with workflow reference."""
        conv = Conversation(
            conversation_id="test-456",
            prompt="Review code",
            workflow_id="wf-789",
            metadata={"priority": "high"},
        )
        assert conv.workflow_id == "wf-789"
        assert conv.metadata["priority"] == "high"

    def test_conversation_index_default(self):
        """Test ConversationIndex default state."""
        index = ConversationIndex()
        assert index.queue == []

    def test_conversation_index_with_items(self):
        """Test ConversationIndex with queued items."""
        index = ConversationIndex(queue=["a", "b", "c"])
        assert len(index.queue) == 3
        assert index.queue[0] == "a"


class TestStorage:
    """Tests for storage operations."""

    def test_ensure_storage_exists(self, temp_dir):
        """Test that storage directory is created."""
        ensure_storage_exists()

        conversations_dir = temp_dir / ".artificer" / "conversations"
        assert conversations_dir.exists()
        assert (conversations_dir / "index.json").exists()

    def test_load_empty_index(self, temp_dir):
        """Test loading an empty index."""
        index = load_index()
        assert index.queue == []

    def test_save_and_load_index(self, temp_dir):
        """Test saving and loading index."""
        index = ConversationIndex(queue=["id1", "id2"])
        save_index(index)

        loaded = load_index()
        assert loaded.queue == ["id1", "id2"]

    def test_save_and_load_conversation(self, temp_dir):
        """Test saving and loading a conversation."""
        conv = Conversation(
            conversation_id="conv-1",
            prompt="Test prompt",
        )
        save_conversation(conv)

        loaded = load_conversation("conv-1")
        assert loaded.conversation_id == "conv-1"
        assert loaded.prompt == "Test prompt"

    def test_load_nonexistent_conversation(self, temp_dir):
        """Test loading a conversation that doesn't exist."""
        ensure_storage_exists()
        with pytest.raises(FileNotFoundError):
            load_conversation("nonexistent")

    def test_conversation_exists(self, temp_dir):
        """Test checking if conversation exists."""
        ensure_storage_exists()
        assert not conversation_exists("missing")

        conv = Conversation(conversation_id="exists", prompt="test")
        save_conversation(conv)
        assert conversation_exists("exists")


class TestQueueOperations:
    """Tests for queue operations."""

    def test_add_to_queue(self, temp_dir):
        """Test adding to queue."""
        add_to_queue("first")
        add_to_queue("second")

        index = load_index()
        assert index.queue == ["first", "second"]

    def test_add_duplicate_to_queue(self, temp_dir):
        """Test that duplicates are not added."""
        add_to_queue("item")
        add_to_queue("item")

        index = load_index()
        assert index.queue == ["item"]

    def test_pop_from_queue_fifo(self, temp_dir):
        """Test FIFO pop behavior."""
        add_to_queue("first")
        add_to_queue("second")
        add_to_queue("third")

        assert pop_from_queue() == "first"
        assert pop_from_queue() == "second"
        assert pop_from_queue() == "third"

    def test_pop_from_empty_queue(self, temp_dir):
        """Test popping from empty queue."""
        ensure_storage_exists()
        result = pop_from_queue()
        assert result is None

    def test_remove_from_queue(self, temp_dir):
        """Test removing specific item from queue."""
        add_to_queue("a")
        add_to_queue("b")
        add_to_queue("c")

        removed = remove_from_queue("b")
        assert removed is True

        index = load_index()
        assert index.queue == ["a", "c"]

    def test_remove_nonexistent_from_queue(self, temp_dir):
        """Test removing item not in queue."""
        add_to_queue("x")

        removed = remove_from_queue("y")
        assert removed is False

        index = load_index()
        assert index.queue == ["x"]


class TestIntegration:
    """Integration tests for full workflows."""

    def test_add_list_start_flow(self, temp_dir):
        """Test the full add -> list -> start flow."""
        # Add a conversation
        conv = Conversation(
            conversation_id="flow-test",
            prompt="Integration test prompt",
        )
        save_conversation(conv)
        add_to_queue("flow-test")

        # Verify it's in queue
        index = load_index()
        assert "flow-test" in index.queue

        # Start the conversation
        remove_from_queue("flow-test")
        loaded = load_conversation("flow-test")

        # Verify it's removed from queue but still exists
        index = load_index()
        assert "flow-test" not in index.queue
        assert loaded.prompt == "Integration test prompt"

    def test_multiple_conversations(self, temp_dir):
        """Test handling multiple conversations."""
        for i in range(5):
            conv = Conversation(
                conversation_id=f"conv-{i}",
                prompt=f"Prompt {i}",
            )
            save_conversation(conv)
            add_to_queue(f"conv-{i}")

        # Pop first three
        for i in range(3):
            conv_id = pop_from_queue()
            assert conv_id == f"conv-{i}"

        # Two remain
        index = load_index()
        assert len(index.queue) == 2
        assert index.queue == ["conv-3", "conv-4"]
