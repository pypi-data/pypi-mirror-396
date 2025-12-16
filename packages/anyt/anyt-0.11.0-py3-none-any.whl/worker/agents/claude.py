"""
Claude Code agent implementation.
"""

import json
from typing import Optional

from .base import CodeExecutionResult, CodingAgent
from .config import AGENT_CONFIGS


class ClaudeCodeAgent(CodingAgent):
    """Claude Code CLI agent implementation.

    Wraps the `claude` CLI tool with support for:
    - Stream-JSON output format for structured parsing
    - Model selection
    - Permission skipping via --dangerously-skip-permissions
    """

    def __init__(self) -> None:
        """Initialize with pre-configured settings."""
        self._config = AGENT_CONFIGS["claude"]

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
        """Build the Claude CLI command.

        Args:
            prompt: The prompt to send to Claude.
            model: Optional model override.
            skip_permissions: Whether to skip permission prompts.
            stream: Whether to enable streaming JSON output.
            extra_args: Additional CLI arguments.

        Returns:
            List of command arguments.
        """
        cmd: list[str] = [self._config.cli_command]

        # Add prompt
        cmd.extend([self._config.prompt_flag, prompt])

        # Add model if specified
        if model:
            cmd.extend([self._config.model_flag, model])

        # Add print flag
        if self._config.print_flag:
            cmd.append(self._config.print_flag)

        # Add skip permissions flag
        if skip_permissions and self._config.skip_permissions_flag:
            cmd.append(self._config.skip_permissions_flag)

        # Add streaming flags
        if stream and self._config.supports_streaming:
            if self._config.stream_flag and self._config.stream_format:
                cmd.append(f"{self._config.stream_flag}={self._config.stream_format}")
            # Add default extra args for streaming
            cmd.extend(self._config.default_extra_args)

        # Add any extra arguments
        if extra_args:
            cmd.extend(extra_args)

        return cmd

    def parse_output(self, output: str) -> CodeExecutionResult:
        """Parse stream-json output from Claude Code.

        Args:
            output: The raw stdout output from the CLI process.

        Returns:
            A CodeExecutionResult with parsed information.
        """
        files_read: set[str] = set()
        files_written: set[str] = set()
        tools_used: set[str] = set()
        thinking_parts: list[str] = []
        text_parts: list[str] = []
        final_result: Optional[str] = None

        # Track current tool to determine file operation type
        current_tool: Optional[str] = None
        tool_inputs: dict[int, str] = {}  # index -> accumulated JSON

        try:
            for line in output.strip().split("\n"):
                if not line:
                    continue

                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue  # Skip malformed lines

                obj_type = obj.get("type")

                # Handle BOTH wrapped stream_event format AND direct event format
                if obj_type == "stream_event":
                    # Wrapped format from newer Claude Code CLI
                    event = obj.get("event", {})
                    event_type = event.get("type")
                    index = event.get("index", 0)
                elif obj_type in [
                    "content_block_start",
                    "content_block_delta",
                    "content_block_stop",
                ]:
                    # Direct/unwrapped format (original)
                    event = obj
                    event_type = obj_type
                    index = obj.get("index", 0)
                elif obj_type == "result":
                    # Handle final result object
                    final_result = obj.get("result", "")
                    continue
                else:
                    # Unknown format, skip
                    continue

                # Capture thinking and text deltas
                if event_type == "content_block_delta":
                    delta = event.get("delta", {})
                    if delta.get("type") == "thinking_delta":
                        thinking_parts.append(delta.get("thinking", ""))
                    elif delta.get("type") == "text_delta":
                        text_parts.append(delta.get("text", ""))
                    elif delta.get("type") == "input_json_delta":
                        # Accumulate partial JSON for this tool use
                        partial = delta.get("partial_json", "")
                        tool_inputs[index] = tool_inputs.get(index, "") + partial

                # Capture tool uses
                if event_type == "content_block_start":
                    block = event.get("content_block", {})
                    if block.get("type") == "tool_use":
                        tool_name = block.get("name", "")
                        if tool_name:
                            tools_used.add(tool_name)
                            current_tool = tool_name

                # Parse complete tool inputs for file paths
                if event_type == "content_block_stop":
                    if index in tool_inputs:
                        try:
                            tool_input = json.loads(tool_inputs[index])
                            file_path = tool_input.get("file_path") or tool_input.get(
                                "path"
                            )

                            if file_path:
                                # Categorize based on tool name
                                if current_tool in [
                                    "Read",
                                    "read",
                                    "read_file",
                                    "Grep",
                                    "grep",
                                    "Glob",
                                    "glob",
                                ]:
                                    files_read.add(file_path)
                                elif current_tool in [
                                    "Write",
                                    "write",
                                    "write_file",
                                    "Edit",
                                    "edit",
                                    "edit_file",
                                ]:
                                    files_written.add(file_path)
                        except (json.JSONDecodeError, KeyError):
                            # Unable to parse tool input, skip
                            pass
                        finally:
                            # Clean up processed input
                            del tool_inputs[index]

        except Exception:
            # Analysis parsing is best-effort; continue with partial results
            pass

        # Use final result if available, otherwise use accumulated text parts
        summary = final_result if final_result else "".join(text_parts).strip()

        return CodeExecutionResult(
            exit_code=0,  # Will be set by caller based on process exit
            completed=True,
            stdout=output,
            summary=summary,
            files_read=sorted(files_read),
            files_written=sorted(files_written),
            tools_used=sorted(tools_used),
            thinking="".join(thinking_parts).strip() if thinking_parts else "",
            raw_output=output,
        )
