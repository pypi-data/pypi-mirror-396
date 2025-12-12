# Artificer Conversations — Architecture

## Core Principles

1. **Minimal Complexity**: A simple queue-based system with no state machines
2. **JSON-First Storage**: Human-readable, inspectable files in `.artificer/conversations/`
3. **Workflow Integration**: Works seamlessly with artificer-workflows for pause/resume
4. **CLI-Driven**: All functionality accessible via `artificer conversations` commands
5. **FIFO Semantics**: First-in, first-out queue processing

## Component Overview

```
artificer-conversations/
├── artificer/
│   └── conversations/
│       ├── __init__.py          # Package exports
│       ├── module.py            # ConversationsModule (CLI registration)
│       ├── storage.py           # JSON file operations (read/write/queue)
│       ├── models.py            # Pydantic models (Conversation, Index)
│       └── step.py              # ConversationStep for workflow integration
└── tests/
    └── test_conversations.py    # Unit tests
```

## Architecture Decisions

### Storage Layer (`storage.py`)
- Single responsibility: all JSON file I/O
- Manages `.artificer/conversations/` directory
- Provides atomic-ish operations for queue manipulation
- No external database dependencies

### Data Models (`models.py`)
- `Conversation`: Single conversation entity with id, prompt, metadata
- `ConversationIndex`: Queue tracking (list of IDs)
- Pydantic models for validation and serialization

### CLI Module (`module.py`)
- Implements `ArtificerModule` interface from `artificer-cli`
- Registers `conversations` command group
- Subcommands: `add`, `list`, `next`, `start`

### Workflow Step (`step.py`)
- Optional integration with `artificer-workflows`
- `ConversationStep` creates conversation, queues it, pauses workflow
- Output includes conversation_id for downstream steps

## Integration Points

### With artificer-cli
- Auto-discovered when `features = ["conversations"]` in `pyproject.toml`
- Expected path: `artificer.conversations.module.ConversationsModule`

### With artificer-workflows (Optional)
- `ConversationStep` for workflow pause/resume patterns
- Workflow resumes when conversation is started externally

## Intentional Constraints

1. **No Transcripts**: We don't store conversation history
2. **No Active Registry**: Conversations are either queued or not
3. **No Retry Logic**: Simple operations that succeed or fail
4. **No UI**: CLI and workflow integration only

## Recent Changes

### 2025-12-08 — Initial Architecture
- Established core component structure
- Defined storage format and queue semantics
- Integrated with artificer-cli module system
- Added optional workflow step support
