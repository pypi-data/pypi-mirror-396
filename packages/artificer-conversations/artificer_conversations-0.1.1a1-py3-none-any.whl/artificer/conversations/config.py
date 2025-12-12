"""Configuration for the conversations module."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class ConversationsConfig:
    """Configuration for conversations module.

    Reads agent_command from [tool.artificer.workflows] section.
    """

    agent_command: str | None = None


def load_conversations_config(base_path: Path | None = None) -> ConversationsConfig:
    """Load conversations configuration from pyproject.toml.

    Reads agent_command from [tool.artificer.workflows] section.

    Args:
        base_path: Directory containing pyproject.toml. Defaults to CWD.

    Returns:
        ConversationsConfig with parsed configuration.
    """
    if base_path is None:
        base_path = Path.cwd()

    pyproject_path = base_path / "pyproject.toml"

    if not pyproject_path.exists():
        return ConversationsConfig()

    with open(pyproject_path, "rb") as f:
        try:
            data = tomllib.load(f)
        except tomllib.TOMLDecodeError:
            return ConversationsConfig()

    tool_config = data.get("tool", {})
    artificer_config = tool_config.get("artificer", {})
    workflows_config = artificer_config.get("workflows", {})

    agent_command = workflows_config.get("agent_command")

    return ConversationsConfig(agent_command=agent_command)
