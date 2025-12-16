"""
Claude AI-related workflow actions.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Set

from rich.markup import escape

from cli.commands.console import console
from .base import Action
from ..context import ExecutionContext


class ClaudePromptAction(Action):
    """Execute a Claude prompt and capture output."""

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute Claude CLI with a prompt."""
        # Model priority: params override > backend config > no model (use CLI default)
        model = params.get("model") or ctx.get_coding_agent_model()
        prompt = params.get("prompt", "")
        output_var = params.get("output", "result")

        # Execute Claude CLI
        cmd: list[str] = [
            "claude",
            "-p",
            prompt,
        ]

        # Only include --model if explicitly specified
        if model:
            cmd.extend(["--model", model])

        cmd.extend(
            [
                "--dangerously-skip-permissions",
                "--print",
            ]
        )

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"Claude CLI failed: {stderr.decode()}")

        result = stdout.decode().strip()

        return {output_var: result}


class ClaudeCodeAction(Action):
    """Execute Claude Code for implementation."""

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute Claude Code CLI."""
        # Model priority: params override > backend config > no model (use CLI default)
        model = params.get("model") or ctx.get_coding_agent_model()
        prompt = params.get("prompt", "")
        stream = params.get("stream", True)
        skip_permissions = params.get("dangerously-skip-permissions", False)

        # Build command
        cmd: list[str] = [
            "claude",
            "-p",
            prompt,
        ]

        # Only include --model if explicitly specified
        if model:
            cmd.extend(["--model", model])

        cmd.append("--print")

        if skip_permissions:
            cmd.append("--dangerously-skip-permissions")

        if stream:
            # stream-json with --print requires --verbose
            cmd.extend(
                [
                    "--output-format=stream-json",
                    "--include-partial-messages",
                    "--verbose",
                ]
            )

        # Execute command
        console.print("  [dim]Executing Claude Code...[/dim]")

        # Use a large buffer limit (16MB) to handle large tool outputs like Jupyter notebooks
        # The default 64KB limit causes LimitOverrunError when reading large files
        buffer_limit = 16 * 1024 * 1024  # 16MB

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
            limit=buffer_limit,
        )

        # Accumulate stdout for parsing
        stdout_lines: List[str] = []

        # Stream output if requested
        if stream and process.stdout:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                line_str = line.decode().strip()
                stdout_lines.append(line_str)
                console.print(f"  [dim]{escape(line_str)}[/dim]")

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"Claude Code failed: {stderr.decode()}")

        # Parse stream output to extract analysis
        stdout_text = "\n".join(stdout_lines) if stdout_lines else stdout.decode()
        analysis = self._parse_stream_output(stdout_text)

        return {
            "exit_code": process.returncode,
            "completed": True,
            "analysis": analysis,
            # Also return individual fields for easier template access
            "summary": analysis.get("summary", ""),
            "files_written": analysis.get("files_written", []),
            "files_read": analysis.get("files_read", []),
            "tools_used": analysis.get("tools_used", []),
        }

    def _parse_stream_output(self, output: str) -> Dict[str, Any]:
        """Parse stream-json output and extract analysis.

        Args:
            output: Stream-json formatted output from Claude Code CLI

        Returns:
            Dictionary containing:
                - files_read: List of files read
                - files_written: List of files written
                - tools_used: List of tools used
                - thinking: Concatenated thinking content
                - summary: Final text output
        """
        files_read: Set[str] = set()
        files_written: Set[str] = set()
        tools_used: Set[str] = set()
        thinking_parts: List[str] = []
        text_parts: List[str] = []
        final_result: Optional[str] = None

        # Track current tool to determine file operation type
        current_tool: Optional[str] = None
        tool_inputs: Dict[int, str] = {}  # index -> accumulated JSON

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

        except Exception as e:  # noqa: BLE001 - Intentionally broad: analysis parsing is best-effort
            # Analysis parsing is best-effort; continue with partial results on any failure
            console.print(
                f"  [dim yellow]Warning: Failed to parse analysis: {e}[/dim yellow]"
            )

        # Use final result if available, otherwise use accumulated text parts
        summary = final_result if final_result else "".join(text_parts).strip()

        return {
            "files_read": sorted(files_read),
            "files_written": sorted(files_written),
            "tools_used": sorted(tools_used),
            "thinking": "".join(thinking_parts).strip() if thinking_parts else "",
            "summary": summary,
        }
