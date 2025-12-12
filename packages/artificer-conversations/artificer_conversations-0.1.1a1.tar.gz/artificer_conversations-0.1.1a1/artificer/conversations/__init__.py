"""Artificer Conversations — Queue-based conversation system."""

from artificer.conversations.config import ConversationsConfig, load_conversations_config
from artificer.conversations.models import Conversation, ConversationIndex
from artificer.conversations.module import ConversationModule

__all__ = [
    "Conversation",
    "ConversationIndex",
    "ConversationModule",
    "ConversationsConfig",
    "load_conversations_config",
]

# Optional: ConversationStep and ConversationWorkflow if workflows are available
try:
    from artificer.conversations.step import ConversationStepOutput, create_conversation_step
    from artificer.conversations.workflow import (
        ConversationOutput,
        ConversationWorkflow,
        create_conversation_workflow,
    )

    __all__.extend([
        "ConversationStepOutput",
        "create_conversation_step",
        "ConversationOutput",
        "ConversationWorkflow",
        "create_conversation_workflow",
    ])
except ImportError:
    pass
