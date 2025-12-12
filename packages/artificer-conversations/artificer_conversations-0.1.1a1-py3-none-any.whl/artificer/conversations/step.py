"""ConversationStep for workflow integration."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from artificer.conversations.models import Conversation
from artificer.conversations.storage import add_to_queue, save_conversation

if TYPE_CHECKING:
    from artificer.workflows.workflow import Pause


class ConversationStepOutput(BaseModel):
    """Output model for ConversationStep."""

    conversation_id: str = Field(description="ID of the created conversation")
    acknowledged: bool = Field(
        default=True, description="Acknowledgment that the step completed"
    )


def create_conversation_step(workflow_class: type) -> type:
    """Create a ConversationStep class bound to a specific workflow.

    This factory function creates a ConversationStep that integrates with
    the artificer-workflows system. The step creates a conversation,
    adds it to the queue, and pauses the workflow.

    Args:
        workflow_class: The Workflow class to bind the step to.

    Returns:
        A ConversationStep class that can be used as a workflow step.

    Example:
        class MyWorkflow(Workflow):
            pass

        ConversationStep = create_conversation_step(MyWorkflow)

        class AskUserStep(ConversationStep):
            prompt = "Please review the generated code"

            def complete(self, output: ConversationStepOutput):
                return NextStep  # or None to end workflow
    """
    from artificer.workflows.workflow import Pause

    class ConversationStep(workflow_class.Step):
        """A workflow step that creates a conversation and pauses.

        Subclass this and set the `prompt` class attribute to define
        what the conversation should ask.
        """

        prompt: str = "No prompt specified"
        metadata: dict[str, Any] = {}

        def start(self, previous_result=None) -> str:  # noqa: ARG002
            """Create the conversation and return instructions."""
            _ = previous_result  # Required by Step interface but unused here
            # Create conversation
            conversation_id = str(uuid.uuid4())

            conversation = Conversation(
                conversation_id=conversation_id,
                prompt=self.prompt,
                workflow_id=self.workflow_id,
                metadata=self.metadata,
            )

            save_conversation(conversation)
            add_to_queue(conversation_id)

            # Store the conversation_id for the output
            self._conversation_id = conversation_id

            return f"""A conversation has been created and added to the queue.

Conversation ID: {conversation_id}
Prompt: {self.prompt}

The workflow will pause after you complete this step.
To resume the workflow, the conversation must be started externally using:
  artificer conversations start {conversation_id}

Then resume the workflow with:
  artificer workflows resume <workflow_id>

Please acknowledge by completing this step with the conversation_id.
"""

        def complete(self, output: ConversationStepOutput) -> "Pause":
            """Complete the step and pause the workflow."""
            return Pause(
                reason=f"Waiting for conversation {output.conversation_id} to be handled"
            )

    return ConversationStep


# For backwards compatibility and direct import
# Users should use create_conversation_step(MyWorkflow) to create bound steps
__all__ = ["ConversationStepOutput", "create_conversation_step"]
