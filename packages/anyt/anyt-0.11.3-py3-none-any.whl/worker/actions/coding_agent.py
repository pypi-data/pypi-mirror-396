"""
Generic coding agent workflow action.

Dispatches to the appropriate coding agent based on task assignment.
"""

import asyncio
import shutil
from typing import Any, Dict, List

from rich.markup import escape

from cli.commands.console import console
from worker.agents import CodingAgentRegistry, CodeExecutionResult

from .base import Action
from ..context import ExecutionContext


# Mapping from CodingAgentType enum values to registry agent names
AGENT_TYPE_TO_REGISTRY: Dict[str, str] = {
    "claude_code": "claude",
    "codex": "codex",
    "gemini_cli": "gemini",
}


class CodingAgentAction(Action):
    """Execute the assigned coding agent for implementation.

    This action dispatches to the appropriate coding agent based on the
    task's assigned_coding_agent field. It provides a unified interface
    for all supported coding agents (Claude, Codex, Gemini).

    The action:
    - Reads assigned_coding_agent from task context
    - Validates the agent is available before execution
    - Dispatches to the correct agent via CodingAgentRegistry
    - Creates a diff artifact if files are written
    - Returns standardized output for workflow integration
    """

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute the assigned coding agent.

        Args:
            params: Action parameters:
                - prompt: The prompt to send to the agent
                - stream: Whether to enable streaming (default: True)
                - dangerously-skip-permissions: Skip permission prompts (default: False)
                - model: Optional model override
            ctx: Execution context with task data and workspace info

        Returns:
            Dictionary containing:
                - exit_code: Process exit code
                - completed: Whether execution completed
                - summary: Summary of what the agent did
                - files_read: List of files read
                - files_written: List of files written
                - agent_used: Name of the agent that executed

        Raises:
            RuntimeError: If no agent is assigned or agent is not available
        """
        # Get assigned agent from task context
        assigned_agent = ctx.task.get("assigned_coding_agent")
        if not assigned_agent:
            raise RuntimeError(
                "No coding agent assigned to this task. "
                "Please assign a coding agent before running this action."
            )

        # Map CodingAgentType enum value to registry name
        registry_name = AGENT_TYPE_TO_REGISTRY.get(assigned_agent)
        if not registry_name:
            raise RuntimeError(
                f"Unknown coding agent type: {assigned_agent}. "
                f"Supported types: {list(AGENT_TYPE_TO_REGISTRY.keys())}"
            )

        # Get agent from registry
        agent = CodingAgentRegistry.get_agent(registry_name)
        if not agent:
            raise RuntimeError(
                f"Coding agent '{registry_name}' is not available. "
                f"Available agents: {CodingAgentRegistry.list_agents()}"
            )

        # Extract parameters
        # Model priority: params override > backend config > no model (use CLI default)
        model = params.get("model") or ctx.get_coding_agent_model()
        prompt = params.get("prompt", "")
        stream = params.get("stream", True)
        skip_permissions = params.get("dangerously-skip-permissions", False)

        # Build command using agent abstraction
        cmd = agent.build_command(
            prompt,
            model=model,
            skip_permissions=skip_permissions,
            stream=stream,
        )

        # Resolve the executable path (required for Windows where npm commands
        # are .cmd files that asyncio.create_subprocess_exec cannot find directly)
        cli_executable = shutil.which(cmd[0])
        if not cli_executable:
            raise RuntimeError(
                f"Cannot find '{cmd[0]}' executable. "
                f"Please ensure {agent.name} is installed and in your PATH."
            )
        cmd[0] = cli_executable

        # Execute command
        console.print(f"  [dim]Executing {agent.name}...[/dim]")

        # Use a large buffer limit (16MB) to handle large tool outputs
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

        # Stream output if requested and agent supports it
        if stream and agent.supports_streaming and process.stdout:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                line_str = line.decode().strip()
                stdout_lines.append(line_str)
                console.print(f"  [dim]{escape(line_str)}[/dim]")

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"{agent.name} failed: {stderr.decode()}")

        # Parse output using agent-specific parser
        stdout_text = "\n".join(stdout_lines) if stdout_lines else stdout.decode()
        result: CodeExecutionResult = agent.parse_output(stdout_text)

        # Update exit code from process
        result.exit_code = process.returncode or 0

        return {
            "exit_code": result.exit_code,
            "completed": result.completed,
            "summary": result.summary,
            "files_read": result.files_read,
            "files_written": result.files_written,
            "tools_used": result.tools_used,
            "agent_used": registry_name,
        }
