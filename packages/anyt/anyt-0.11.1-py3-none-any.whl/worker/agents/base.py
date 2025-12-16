"""
Base classes for coding agent abstraction.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class CodeExecutionResult:
    """Result from executing a coding agent command.

    Attributes:
        exit_code: The exit code from the CLI process.
        completed: Whether the command completed (vs was interrupted/timed out).
        stdout: Raw stdout output from the process.
        stderr: Raw stderr output from the process.
        summary: Parsed summary text of what the agent did.
        files_read: List of files the agent read during execution.
        files_written: List of files the agent wrote/modified during execution.
        tools_used: List of tools the agent used (if trackable).
        thinking: Extended thinking content (if available).
        raw_output: The complete raw output for debugging.
    """

    exit_code: int
    completed: bool
    stdout: str = ""
    stderr: str = ""
    summary: str = ""
    files_read: list[str] = field(default_factory=list)
    files_written: list[str] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)
    thinking: str = ""
    raw_output: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary for workflow integration."""
        return {
            "exit_code": self.exit_code,
            "completed": self.completed,
            "summary": self.summary,
            "files_read": self.files_read,
            "files_written": self.files_written,
            "tools_used": self.tools_used,
        }


class CodingAgent(ABC):
    """Abstract base class for coding agent CLI wrappers.

    Each implementation wraps a specific coding CLI tool (Claude, Codex,
    Gemini CLI, Cursor) and provides a consistent interface for:
    - Building CLI commands with appropriate flags
    - Parsing output to extract structured information
    - Streaming output during execution
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The display name of this agent (e.g., 'Claude Code')."""
        pass

    @property
    @abstractmethod
    def cli_command(self) -> str:
        """The base CLI command to execute (e.g., 'claude', 'codex')."""
        pass

    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Whether this agent supports streaming JSON output."""
        pass

    @abstractmethod
    def build_command(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        skip_permissions: bool = False,
        stream: bool = True,
        extra_args: Optional[list[str]] = None,
    ) -> list[str]:
        """Build the CLI command to execute.

        Args:
            prompt: The prompt to send to the coding agent.
            model: Optional model override (agent-specific format).
            skip_permissions: Whether to skip permission prompts (auto-approve).
            stream: Whether to enable streaming output (if supported).
            extra_args: Additional CLI arguments to pass.

        Returns:
            List of command arguments suitable for subprocess execution.
        """
        pass

    @abstractmethod
    def parse_output(self, output: str) -> CodeExecutionResult:
        """Parse the raw CLI output into a structured result.

        Args:
            output: The raw stdout output from the CLI process.

        Returns:
            A CodeExecutionResult with parsed information.
        """
        pass

    def get_working_dir_args(self, _working_dir: Path) -> list[str]:
        """Get CLI arguments for setting the working directory.

        Default implementation returns empty list (working dir set via cwd).
        Override if the agent has specific CLI flags for working directory.

        Args:
            _working_dir: The directory to run the agent in (unused in base).

        Returns:
            List of CLI arguments for working directory, or empty list.
        """
        return []
