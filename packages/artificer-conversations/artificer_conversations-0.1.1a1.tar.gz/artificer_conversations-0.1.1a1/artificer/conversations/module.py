"""ConversationsModule for Artificer CLI integration."""

from __future__ import annotations

import os
import shlex
import uuid
from typing import TYPE_CHECKING

import click
from artificer.cli.module import ArtificerModule

from artificer.conversations.config import load_conversations_config
from artificer.conversations.models import Conversation
from artificer.conversations.storage import (
    add_to_queue,
    conversation_exists,
    load_conversation,
    load_index,
    pop_from_queue,
    remove_from_queue,
    save_conversation,
)
from artificer.conversations.workflow import create_conversation_workflow

if TYPE_CHECKING:
    from artificer.cli.config import ArtificerConfig


def _launch_agent(conversation: Conversation) -> None:
    """Launch the agent interactively with the conversation prompt.

    Replaces the current process with the agent command, allowing
    the agent to take over the terminal for interactive use.

    Args:
        conversation: The conversation to process.

    Raises:
        click.ClickException: If agent_command is not configured.
    """
    config = load_conversations_config()

    if config.agent_command is None:
        raise click.ClickException(
            "agent_command not configured. "
            "Add 'agent_command' to [tool.artificer.workflows] in pyproject.toml"
        )

    # Build the command with placeholders
    # Supports: {prompt}, {conversation_id}, {workflow_id}
    command = config.agent_command.format(
        prompt=conversation.prompt,
        conversation_id=conversation.conversation_id,
        workflow_id=conversation.workflow_id or "",
    )

    click.echo(f"Launching agent: {command}")

    # Replace current process with the agent command
    # This allows the agent to take over the terminal interactively
    args = shlex.split(command)
    os.execvp(args[0], args)


class ConversationModule(ArtificerModule):
    """Module providing CLI commands for conversation management."""

    @classmethod
    def register(cls, cli: click.Group, config: "ArtificerConfig") -> None:
        """Register conversation commands with the CLI."""

        @cli.group()
        def conversations():
            """Manage conversations."""
            pass

        @conversations.command("add")
        @click.argument("prompt")
        @click.option(
            "--workflow-id",
            default=None,
            help="Optional workflow ID to associate with the conversation",
        )
        def add_cmd(prompt: str, workflow_id: str | None):
            """Add a new conversation to the queue.

            If no workflow_id is provided, a default ConversationWorkflow
            will be created and paused on the first step.
            """
            conversation_id = str(uuid.uuid4())

            # Create a default workflow if none provided
            if workflow_id is None:
                workflow_id = create_conversation_workflow(conversation_id, prompt)

            conversation = Conversation(
                conversation_id=conversation_id,
                prompt=prompt,
                workflow_id=workflow_id,
            )

            save_conversation(conversation)
            add_to_queue(conversation_id)

            click.echo(conversation_id)

        @conversations.command("list")
        def list_cmd():
            """List all queued conversations."""
            index = load_index()

            if not index.queue:
                click.echo("No conversations in queue.")
                return

            for conversation_id in index.queue:
                try:
                    conversation = load_conversation(conversation_id)
                    # Truncate prompt for display
                    prompt_preview = conversation.prompt[:60]
                    if len(conversation.prompt) > 60:
                        prompt_preview += "..."
                    click.echo(f"{conversation_id}  {prompt_preview}")
                except FileNotFoundError:
                    click.echo(f"{conversation_id}  [ERROR: file missing]")

        @conversations.command("next")
        def next_cmd():
            """Pop and start the next conversation from the queue.

            Launches the agent interactively using agent_command from
            [tool.artificer.workflows] in pyproject.toml.
            """
            conversation_id = pop_from_queue()

            if conversation_id is None:
                click.echo("Queue is empty.", err=True)
                raise SystemExit(1)

            try:
                conversation = load_conversation(conversation_id)
                click.echo(f"ID: {conversation_id}")
                click.echo(f"Prompt: {conversation.prompt}")
                if conversation.workflow_id:
                    click.echo(f"Workflow: {conversation.workflow_id}")

                _launch_agent(conversation)

            except FileNotFoundError:
                click.echo(f"ID: {conversation_id}")
                click.echo("[ERROR: conversation file missing]", err=True)
                raise SystemExit(1)

        @conversations.command("start")
        @click.argument("conversation_id")
        def start_cmd(conversation_id: str):
            """Start a conversation by ID (removes from queue if present).

            Launches the agent interactively using agent_command from
            [tool.artificer.workflows] in pyproject.toml.
            """
            if not conversation_exists(conversation_id):
                click.echo(f"Conversation not found: {conversation_id}", err=True)
                raise SystemExit(1)

            # Remove from queue if present (idempotent)
            remove_from_queue(conversation_id)

            conversation = load_conversation(conversation_id)
            click.echo(f"ID: {conversation.conversation_id}")
            click.echo(f"Prompt: {conversation.prompt}")
            click.echo(f"Created: {conversation.created_at.isoformat()}")
            if conversation.workflow_id:
                click.echo(f"Workflow: {conversation.workflow_id}")
            if conversation.metadata:
                click.echo(f"Metadata: {conversation.metadata}")

            _launch_agent(conversation)
