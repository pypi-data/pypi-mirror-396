"""
Codex agent implementation.
"""

import json
from typing import Any, Optional

from .base import CodeExecutionResult, CodingAgent
from .config import AGENT_CONFIGS


class CodexAgent(CodingAgent):
    """Codex CLI agent implementation.

    Wraps the `codex` CLI tool with support for:
    - Non-interactive execution via `codex exec` subcommand
    - Model selection
    - Permission skipping via --dangerously-bypass-approvals-and-sandbox
    - JSON streaming output via --json flag
    """

    def __init__(self) -> None:
        """Initialize with pre-configured settings."""
        self._config = AGENT_CONFIGS["codex"]

    @property
    def name(self) -> str:
        """The display name of this agent."""
        return self._config.name

    @property
    def cli_command(self) -> str:
        """The base CLI command to execute."""
        return self._config.cli_command

    @property
    def supports_streaming(self) -> bool:
        """Whether this agent supports streaming JSON output."""
        return self._config.supports_streaming

    def build_command(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        skip_permissions: bool = False,
        stream: bool = True,
        extra_args: Optional[list[str]] = None,
    ) -> list[str]:
        """Build the Codex CLI command.

        Args:
            prompt: The prompt to send to Codex.
            model: Optional model override.
            skip_permissions: Whether to skip permission prompts.
            stream: Whether to enable JSON streaming output.
            extra_args: Additional CLI arguments.

        Returns:
            List of command arguments.
        """
        cmd: list[str] = [self._config.cli_command]

        # Add subcommand (exec for non-interactive mode)
        if self._config.subcommand:
            cmd.append(self._config.subcommand)

        # Add model if specified
        if model:
            cmd.extend([self._config.model_flag, model])

        # Add skip permissions flag
        if skip_permissions and self._config.skip_permissions_flag:
            cmd.append(self._config.skip_permissions_flag)

        # Add JSON streaming flag if streaming enabled
        if stream and self._config.stream_flag:
            cmd.append(self._config.stream_flag)

        # Add default extra arguments from config
        if self._config.default_extra_args:
            cmd.extend(self._config.default_extra_args)

        # Add any extra arguments
        if extra_args:
            cmd.extend(extra_args)

        # Codex exec takes prompt as positional argument (must be last)
        cmd.append(prompt)

        return cmd

    def parse_output(self, output: str) -> CodeExecutionResult:
        """Parse JSON streaming output from Codex.

        Codex with --json outputs newline-delimited JSON events:
        - thread.started: Thread initialized
        - turn.started: Turn started
        - item.completed: Item completed (reasoning, command_execution, agent_message)
        - turn.completed: Turn completed with usage stats

        Args:
            output: The raw stdout output from the CLI process.

        Returns:
            A CodeExecutionResult with parsed information.
        """
        files_read: list[str] = []
        files_written: list[str] = []
        tools_used: list[str] = []
        thinking_parts: list[str] = []
        messages: list[str] = []
        commands_executed: list[dict[str, Any]] = []

        # Parse each JSON line
        for line in output.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                # If not JSON, treat as plain text output (fallback)
                if line:
                    messages.append(line)
                continue

            event_type = event.get("type", "")

            if event_type == "item.completed":
                item = event.get("item", {})
                item_type = item.get("type", "")

                if item_type == "reasoning":
                    # Reasoning/thinking text
                    text = item.get("text", "")
                    if text:
                        thinking_parts.append(text)

                elif item_type == "command_execution":
                    # Command was executed
                    command = item.get("command", "")
                    cmd_output = item.get("aggregated_output", "")
                    exit_code = item.get("exit_code")
                    status = item.get("status", "")

                    commands_executed.append(
                        {
                            "command": command,
                            "output": cmd_output,
                            "exit_code": exit_code,
                            "status": status,
                        }
                    )
                    tools_used.append(f"command: {command}")

                elif item_type == "agent_message":
                    # Final agent message
                    text = item.get("text", "")
                    if text:
                        messages.append(text)

                elif item_type == "file_read":
                    # File was read
                    file_path = item.get("path", "")
                    if file_path:
                        files_read.append(file_path)

                elif item_type == "file_write":
                    # File was written
                    file_path = item.get("path", "")
                    if file_path:
                        files_written.append(file_path)

        # Build summary from agent messages
        summary = "\n".join(messages) if messages else output.strip()

        # Build thinking from reasoning parts
        thinking = "\n".join(thinking_parts)

        return CodeExecutionResult(
            exit_code=0,  # Will be set by caller based on process exit
            completed=True,
            stdout=output,
            summary=summary,
            files_read=files_read,
            files_written=files_written,
            tools_used=tools_used,
            thinking=thinking,
            raw_output=output,
        )
