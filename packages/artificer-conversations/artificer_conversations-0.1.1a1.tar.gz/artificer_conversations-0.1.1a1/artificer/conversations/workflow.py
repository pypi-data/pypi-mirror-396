"""Default ConversationWorkflow for standalone conversations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    pass

# Only create workflow if artificer-workflows is available
try:
    from artificer.workflows.workflow import Pause, Workflow

    class ConversationOutput(BaseModel):
        """Output model for the conversation step."""

        response: str = Field(description="The response from handling the conversation")
        completed: bool = Field(
            default=True, description="Whether the conversation was completed"
        )

    class ConversationWorkflow(Workflow):
        """A minimal workflow for standalone conversations.

        This workflow is automatically created when a conversation is queued
        without an associated workflow_id. It has a single step that pauses
        immediately, allowing the conversation to be processed externally
        before the workflow can be resumed.
        """

        pass

    class HandleConversationStep(ConversationWorkflow.Step, start=True):
        """Step that handles the conversation and pauses."""

        def __init__(self, *args, prompt: str = "", **kwargs):
            super().__init__(*args, **kwargs)
            self.prompt = prompt

        def start(self, previous_result=None) -> str:
            """Return instructions for handling the conversation."""
            _ = previous_result
            return f"""Handle the following conversation:

{self.prompt}

When complete, provide a response summarizing what was done.
"""

        def complete(self, output: ConversationOutput) -> Pause | None:
            """Complete the step - pauses for external handling, then completes workflow."""
            # If completed, end the workflow
            if output.completed:
                return None
            # Otherwise pause for more work
            return Pause(reason="Conversation requires additional handling")

    WORKFLOW_AVAILABLE = True

except ImportError:
    WORKFLOW_AVAILABLE = False
    ConversationWorkflow = None  # type: ignore
    ConversationOutput = None  # type: ignore
    HandleConversationStep = None  # type: ignore


def create_conversation_workflow(
    conversation_id: str, prompt: str
) -> str | None:
    """Create a ConversationWorkflow for a standalone conversation.

    Args:
        conversation_id: The ID of the conversation.
        prompt: The conversation prompt.

    Returns:
        The workflow_id if created, None if workflows not available.
    """
    if not WORKFLOW_AVAILABLE:
        return None

    from artificer.workflows.store import workflow_store

    workflow = ConversationWorkflow()

    # Create the initial step with the conversation prompt
    # HandleConversationStep is a module-level class (defined after ConversationWorkflow)
    step = HandleConversationStep(
        workflow_id=workflow.workflow_id,
        prompt=prompt,
    )

    workflow.steps[step.step_id] = step
    workflow.current_step_id = step.step_id

    # Pause the workflow immediately - it will be resumed when the conversation starts
    from artificer.workflows.types import WorkflowStatus

    workflow.status = WorkflowStatus.PAUSED

    workflow_store.save_workflow(workflow)

    return workflow.workflow_id
