"""
Configuration specifications for coding agent CLIs.

This module contains pre-configured specs learned from each agent's --help output.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentCLIConfig:
    """Configuration specification for a coding agent CLI.

    Attributes:
        name: Display name of the agent.
        cli_command: Base CLI command (e.g., 'claude', 'codex').
        backend_type: The CodingAgentType value expected by the backend API.
        subcommand: Subcommand for non-interactive mode (e.g., 'exec' for codex).
        prompt_flag: Flag for passing the prompt (e.g., '-p', '--prompt').
        model_flag: Flag for specifying model (e.g., '--model').
        skip_permissions_flag: Flag for auto-approve/skip permissions.
        stream_flag: Flag for enabling streaming output (if supported).
        stream_format: The streaming output format name (e.g., 'stream-json').
        print_flag: Flag for printing output (e.g., '--print').
        supports_streaming: Whether the agent supports streaming JSON output.
        default_extra_args: Default extra arguments to always include.
    """

    name: str
    cli_command: str
    backend_type: str  # Must match CodingAgentType enum values from backend
    subcommand: Optional[str] = None
    prompt_flag: str = "-p"
    model_flag: str = "--model"
    skip_permissions_flag: Optional[str] = None
    stream_flag: Optional[str] = None
    stream_format: Optional[str] = None
    print_flag: Optional[str] = None
    supports_streaming: bool = False
    default_extra_args: list[str] = field(default_factory=list)


# Pre-configured specs for each supported coding agent
# Keys are local identifiers, backend_type must match CodingAgentType enum from backend
AGENT_CONFIGS: dict[str, AgentCLIConfig] = {
    "claude": AgentCLIConfig(
        name="Claude Code",
        cli_command="claude",
        backend_type="claude_code",  # Maps to CodingAgentType.CLAUDE_CODE
        prompt_flag="-p",
        model_flag="--model",
        skip_permissions_flag="--dangerously-skip-permissions",
        stream_flag="--output-format",
        stream_format="stream-json",
        print_flag="--print",
        supports_streaming=True,
        default_extra_args=["--include-partial-messages", "--verbose"],
    ),
    "codex": AgentCLIConfig(
        name="Codex",
        cli_command="codex",
        backend_type="codex",  # Maps to CodingAgentType.CODEX
        subcommand="exec",
        prompt_flag="",  # Codex exec takes prompt as positional argument
        model_flag="--model",
        skip_permissions_flag="--dangerously-bypass-approvals-and-sandbox",
        stream_flag="--json",  # Enables JSON streaming output
        supports_streaming=True,
        default_extra_args=["--sandbox", "workspace-write", "--skip-git-repo-check"],
    ),
    "gemini": AgentCLIConfig(
        name="Gemini CLI",
        cli_command="gemini",
        backend_type="gemini_cli",  # Maps to CodingAgentType.GEMINI_CLI
        prompt_flag="-p",
        model_flag="--model",
        skip_permissions_flag="--yolo",
        stream_flag="--output-format",
        stream_format="stream-json",
        supports_streaming=True,
    ),
}


def get_agent_config(agent_name: str) -> Optional[AgentCLIConfig]:
    """Get the configuration for a named coding agent.

    Args:
        agent_name: The agent identifier (e.g., 'claude', 'codex').

    Returns:
        The AgentCLIConfig for the agent, or None if not found.
    """
    return AGENT_CONFIGS.get(agent_name.lower())


def list_agent_names() -> list[str]:
    """Get list of all supported agent names.

    Returns:
        List of agent identifiers.
    """
    return sorted(AGENT_CONFIGS.keys())


def get_backend_type(agent_name: str) -> Optional[str]:
    """Get the backend CodingAgentType value for an agent.

    Args:
        agent_name: The local agent identifier (e.g., 'claude', 'gemini').

    Returns:
        The backend type string (e.g., 'claude_code', 'gemini_cli'), or None if not found.
    """
    config = AGENT_CONFIGS.get(agent_name.lower())
    return config.backend_type if config else None


def list_backend_types() -> list[str]:
    """Get list of all backend CodingAgentType values.

    Returns:
        List of backend type strings suitable for API calls.
    """
    return [config.backend_type for config in AGENT_CONFIGS.values()]
