# Implementation Plan — artificer-conversations MVP

## Overview

Build a queue-based conversation system for the Artificer ecosystem with CLI integration and optional workflow support.

## Phase 1: Package Structure & Models

### Step 1.1: Create Package Structure
- Create `src/artificer/conversations/` namespace package
- Add `__init__.py` with public exports
- Configure `pyproject.toml` for namespace package

### Step 1.2: Define Data Models (`models.py`)
- `Conversation` model with fields:
  - `conversation_id: str`
  - `prompt: str`
  - `created_at: datetime`
  - `workflow_id: Optional[str]`
  - `metadata: dict`
- `ConversationIndex` model with:
  - `queue: list[str]`

## Phase 2: Storage Layer

### Step 2.1: Implement Storage Operations (`storage.py`)
- `get_conversations_dir() -> Path` — Returns `.artificer/conversations/`
- `ensure_storage_exists()` — Creates directory and index.json if missing
- `load_index() -> ConversationIndex` — Load queue from index.json
- `save_index(index: ConversationIndex)` — Save queue to index.json
- `load_conversation(id: str) -> Conversation` — Load single conversation
- `save_conversation(conversation: Conversation)` — Save conversation JSON

### Step 2.2: Queue Operations
- `add_to_queue(id: str)` — Append ID to queue
- `pop_from_queue() -> Optional[str]` — Pop first ID (FIFO)
- `remove_from_queue(id: str)` — Remove specific ID if present

## Phase 3: CLI Module

### Step 3.1: Create Module Class (`module.py`)
- `ConversationsModule(ArtificerModule)` class
- Implement `register(cli, config)` method
- Register `conversations` command group

### Step 3.2: Implement CLI Commands
- `add <prompt>` command:
  - Generate unique ID (uuid4)
  - Create Conversation object
  - Save to JSON file
  - Add to queue
  - Print ID

- `list` command:
  - Load index
  - For each queued ID, load conversation
  - Print ID + prompt summary

- `next` command:
  - Pop first ID from queue
  - Load conversation
  - Print prompt + ID
  - Exit 1 if queue empty

- `start <id>` command:
  - Validate ID exists (exit 1 if not)
  - Remove from queue if present (no-op if not)
  - Load and print conversation details

## Phase 4: Workflow Integration (Optional)

### Step 4.1: Create ConversationStep (`step.py`)
- Import from artificer-workflows if available
- Define `ConversationStep` class
- Accept prompt as parameter
- On execute:
  - Create conversation
  - Add to queue
  - Return conversation_id in output
  - Pause workflow

## Phase 5: Testing

### Step 5.1: Unit Tests
- Test adding conversations
- Test listing (only queued items)
- Test FIFO behavior of `next`
- Test idempotent `start`
- Test error cases (empty queue, invalid ID)

### Step 5.2: Integration Tests
- Test full CLI flow
- Test workflow step if available

## File Checklist

```
src/artificer/conversations/
├── __init__.py          # Exports: ConversationsModule, Conversation, ConversationStep
├── module.py            # CLI module registration
├── storage.py           # JSON file operations
├── models.py            # Pydantic models
└── step.py              # Workflow step (optional)

tests/
└── test_conversations.py
```

## Dependencies

- `artificer-cli>=0.1.0a2` (required)
- `artificer-workflows>=0.1.0a9` (optional, for ConversationStep)
- No additional dependencies

## Implementation Order

1. `models.py` — Define data structures first
2. `storage.py` — Build storage layer
3. `module.py` — Wire up CLI commands
4. `step.py` — Add workflow integration
5. Tests — Verify everything works
