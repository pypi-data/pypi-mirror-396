"""
Task management workflow actions.
"""

import json
from typing import Any, Dict, Optional, cast


from .base import Action
from ..context import ExecutionContext


class TaskUpdateAction(Action):
    """Update AnyTask task with enhanced note support and metadata storage."""

    def __init__(self) -> None:
        """Initialize TaskUpdateAction."""
        # Clients are created lazily with workspace context
        pass

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Update task in AnyTask."""
        status = params.get("status")
        note = params.get("note")
        add_timestamp = params.get("timestamp", False)
        metadata = params.get("metadata")

        task_id = ctx.task.get("identifier")
        if not task_id:
            raise ValueError("Task identifier not found in context")

        # Get workspace_id from task context or execution context
        workspace_id = ctx.task.get("workspace_id") or ctx.workspace_id
        if not workspace_id:
            raise ValueError("Workspace ID not found in task context")

        # Initialize clients with workspace context and env from execution context
        self._init_clients(workspace_id, ctx.env)

        # Add timestamp if requested
        if note and add_timestamp:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            note = f"**{timestamp}**\n\n{note}"

        # Update status if provided
        if status:
            await self._update_status(task_id, status)

        # Add note if provided
        if note:
            await self._add_note(ctx, note)

        # Store metadata if provided
        if metadata:
            await self._store_metadata(ctx, metadata)

        return {
            "updated": True,
            "status": status,
            "note_added": bool(note),
            "metadata_stored": bool(metadata),
        }

    def _init_clients(
        self, workspace_id: int, ctx_env: Optional[Dict[str, str]] = None
    ) -> None:
        """Initialize API clients with workspace context.

        Uses ANYT_API_KEY with standard API clients.

        Args:
            workspace_id: Workspace ID from task context
            ctx_env: Optional environment dict from execution context (checked first)
        """
        import os
        from cli.client.tasks import TasksAPIClient
        from cli.client.comments import CommentsAPIClient

        # Get authentication tokens - check context env first, then os.environ
        ctx_env = ctx_env or {}
        api_key = ctx_env.get("ANYT_API_KEY") or os.getenv("ANYT_API_KEY")
        api_url = (
            ctx_env.get("ANYT_API_URL")
            or os.getenv("ANYT_API_URL")
            or "https://api.anyt.dev"
        )

        if api_key:
            self.task_client = TasksAPIClient(
                base_url=api_url, api_key=api_key, workspace_id=workspace_id
            )
            self.comments_client = CommentsAPIClient(
                base_url=api_url, api_key=api_key, workspace_id=workspace_id
            )
            self.workspace_id = workspace_id
            self.api_key = api_key
        else:
            raise ValueError(
                "Authentication required: Set ANYT_API_KEY environment variable."
            )

    async def _update_status(self, task_id: str, status: str) -> None:
        """Update task status."""
        from cli.models.task import TaskUpdate
        from cli.models.common import Status

        # Convert string status to Status enum
        status_enum = Status(status.lower())
        update_data = TaskUpdate(status=status_enum)
        await self.task_client.update_task(task_id, update_data)

    async def _add_note(self, ctx: ExecutionContext, note: str) -> None:
        """Add comment to task."""
        from cli.models.comment import CommentCreate

        task_identifier = ctx.task.get("identifier")
        if not task_identifier:
            raise ValueError("Task identifier required in context")

        task_id = ctx.task.get("id")
        if not task_id:
            raise ValueError("Task ID required in context for comment creation")

        comment_data = CommentCreate(
            content=note, task_id=int(task_id), author_id=self.api_key
        )
        await self.comments_client.create_comment(task_identifier, comment_data)

    async def _store_metadata(
        self, ctx: ExecutionContext, metadata: Dict[str, Any]
    ) -> None:
        """Store workflow execution metadata in task notes.

        Since task custom fields are not currently supported by the API,
        we store metadata as a structured note with a special marker.
        This allows for later retrieval and parsing.

        Args:
            ctx: Execution context containing task data
            metadata: Workflow execution metadata dictionary
        """
        from cli.models.workflow import WorkflowExecutionMetadata

        # Validate and convert metadata to proper format
        try:
            meta = WorkflowExecutionMetadata(**metadata)
        except Exception as e:  # noqa: BLE001 - Intentionally broad: wrap validation errors
            # Wrap any Pydantic validation error in ValueError with context
            raise ValueError(f"Invalid metadata format: {e}")

        # Store as structured note with HTML comment marker for easy parsing
        note = f"""<!-- workflow-metadata
{meta.model_dump_json(indent=2)}
-->"""

        # Add metadata note to task
        await self._add_note(ctx, note)


class TaskAnalyzeAction(Action):
    """Send Claude Code analysis results to task notes with formatting."""

    def __init__(self) -> None:
        """Initialize TaskAnalyzeAction."""
        # Client is created lazily with workspace context
        pass

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Send formatted analysis to task."""
        analysis_raw = params.get("analysis", {})
        title = params.get("title", "Analysis Results")
        include_empty = params.get("include_empty", False)

        # Get workspace_id from task context or execution context
        workspace_id = ctx.task.get("workspace_id") or ctx.workspace_id
        if not workspace_id:
            raise ValueError("Workspace ID not found in task context")

        # Initialize client with workspace context and env from execution context
        self._init_client(workspace_id, ctx.env)

        # Handle both dict and JSON string (from template interpolation)
        analysis: Dict[str, Any]
        if isinstance(analysis_raw, str):
            try:
                analysis = cast(Dict[str, Any], json.loads(analysis_raw))
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"analysis must be a valid JSON string or dictionary: {e}"
                )
        elif isinstance(analysis_raw, dict):
            analysis = cast(Dict[str, Any], analysis_raw)
        else:
            raise ValueError("analysis must be a dictionary or JSON string")

        # Format analysis as markdown
        note = self._format_analysis(title, analysis, include_empty)

        # Send to task using appropriate client
        task_identifier = ctx.task.get("identifier")

        if not task_identifier:
            raise ValueError("Task identifier required in context")

        # Add comment
        from cli.models.comment import CommentCreate

        task_id = ctx.task.get("id")
        if not task_id:
            raise ValueError("Task ID required in context for comment creation")

        comment_data = CommentCreate(
            content=note, task_id=int(task_id), author_id=self.api_key
        )
        domain_comment = await self.comments_client.create_comment(
            task_identifier, comment_data
        )
        comment_id = domain_comment.id

        # Determine which sections were included
        sections: list[str] = []
        if analysis.get("files_read"):
            sections.append("files_read")
        if analysis.get("files_written"):
            sections.append("files_written")
        if analysis.get("tools_used"):
            sections.append("tools_used")
        if analysis.get("thinking"):
            sections.append("thinking")
        if analysis.get("summary"):
            sections.append("summary")

        return {
            "sent": True,
            "sections": sections,
            "note_length": len(note),
            "comment_id": comment_id,
        }

    def _init_client(
        self, workspace_id: int, ctx_env: Optional[Dict[str, str]] = None
    ) -> None:
        """Initialize API clients with workspace context.

        Uses ANYT_API_KEY with standard API clients.

        Args:
            workspace_id: Workspace ID from task context
            ctx_env: Optional environment dict from execution context (checked first)
        """
        import os
        from cli.client.comments import CommentsAPIClient

        # Get authentication tokens - check context env first, then os.environ
        ctx_env = ctx_env or {}
        api_key = ctx_env.get("ANYT_API_KEY") or os.getenv("ANYT_API_KEY")
        api_url = (
            ctx_env.get("ANYT_API_URL")
            or os.getenv("ANYT_API_URL")
            or "https://api.anyt.dev"
        )

        if api_key:
            self.comments_client = CommentsAPIClient(
                base_url=api_url, api_key=api_key, workspace_id=workspace_id
            )
            self.workspace_id = workspace_id
            self.api_key = api_key
        else:
            raise ValueError(
                "Authentication required: Set ANYT_API_KEY environment variable."
            )

    def _format_analysis(
        self, title: str, analysis: Dict[str, Any], include_empty: bool
    ) -> str:
        """Format analysis results as markdown."""
        lines: list[str] = [f"## {title}\n"]

        # Files Read
        files_read = analysis.get("files_read", [])
        if files_read or include_empty:
            lines.append("### Files Read")
            if files_read:
                for f in files_read:
                    lines.append(f"- `{f}`")
            else:
                lines.append("_None_")
            lines.append("")

        # Files Written
        files_written = analysis.get("files_written", [])
        if files_written or include_empty:
            lines.append("### Files Written")
            if files_written:
                for f in files_written:
                    lines.append(f"- `{f}`")
            else:
                lines.append("_None_")
            lines.append("")

        # Tools Used
        tools_used = analysis.get("tools_used", [])
        if tools_used or include_empty:
            lines.append("### Tools Used")
            if tools_used:
                for tool in tools_used:
                    lines.append(f"- `{tool}`")
            else:
                lines.append("_None_")
            lines.append("")

        # Thinking (optional)
        thinking = analysis.get("thinking", "")
        if thinking:
            lines.append("### Analysis")
            # Truncate if too long
            if len(thinking) > 500:
                thinking = thinking[:500] + "..."
            lines.append(thinking)
            lines.append("")

        # Summary
        summary = analysis.get("summary", "")
        if summary or include_empty:
            lines.append("### Summary")
            if summary:
                lines.append(summary)
            else:
                lines.append("_No summary available_")
            lines.append("")

        return "\n".join(lines)


class TaskDetailAction(Action):
    """Send workflow execution details to task notes."""

    def __init__(self) -> None:
        """Initialize TaskDetailAction."""
        # Client is created lazily with workspace context
        pass

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Send formatted execution details to task."""
        status = params.get("status", "unknown")
        error = params.get("error")
        workflow_name = params.get("workflow_name", "unknown")
        duration = params.get("duration")  # seconds

        # Get workspace_id from task context or execution context
        workspace_id = ctx.task.get("workspace_id") or ctx.workspace_id
        if not workspace_id:
            raise ValueError("Workspace ID not found in task context")

        # Initialize client with workspace context and env from execution context
        self._init_client(workspace_id, ctx.env)

        # Format execution details
        note = self._format_execution_details(
            ctx, status, error, workflow_name, duration
        )

        # Send to task using appropriate client
        task_identifier = ctx.task.get("identifier")

        if not task_identifier:
            raise ValueError("Task identifier required in context")

        # Add comment
        from cli.models.comment import CommentCreate

        task_id = ctx.task.get("id")
        if not task_id:
            raise ValueError("Task ID required in context for comment creation")

        comment_data = CommentCreate(
            content=note, task_id=int(task_id), author_id=self.api_key
        )
        domain_comment = await self.comments_client.create_comment(
            task_identifier, comment_data
        )
        comment_id = domain_comment.id

        return {"sent": True, "comment_id": comment_id}

    def _init_client(
        self, workspace_id: int, ctx_env: Optional[Dict[str, str]] = None
    ) -> None:
        """Initialize API clients with workspace context.

        Uses ANYT_API_KEY with standard API clients.

        Args:
            workspace_id: Workspace ID from task context
            ctx_env: Optional environment dict from execution context (checked first)
        """
        import os
        from cli.client.comments import CommentsAPIClient

        # Get authentication tokens - check context env first, then os.environ
        ctx_env = ctx_env or {}
        api_key = ctx_env.get("ANYT_API_KEY") or os.getenv("ANYT_API_KEY")
        api_url = (
            ctx_env.get("ANYT_API_URL")
            or os.getenv("ANYT_API_URL")
            or "https://api.anyt.dev"
        )

        if api_key:
            self.comments_client = CommentsAPIClient(
                base_url=api_url, api_key=api_key, workspace_id=workspace_id
            )
            self.workspace_id = workspace_id
            self.api_key = api_key
        else:
            raise ValueError(
                "Authentication required: Set ANYT_API_KEY environment variable."
            )

    def _format_execution_details(
        self,
        ctx: ExecutionContext,
        status: str,
        error: Optional[str],
        workflow_name: str,
        duration: Optional[float],
    ) -> str:
        """Format execution details as markdown."""
        from datetime import datetime

        lines: list[str] = ["## Workflow Execution Details\n"]

        # Status with emoji
        status_emoji = "✅" if status == "success" else "❌"
        lines.append(f"**Status**: {status_emoji} {status.title()}")
        lines.append("")

        # Workflow info
        lines.append(f"**Workflow**: `{workflow_name}`")

        # Worker info
        agent_id = ctx.task.get("agent_id", "unknown")
        lines.append(f"**Worker**: `{agent_id}`")

        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"**Timestamp**: {timestamp}")

        # Duration if available
        if duration is not None:
            lines.append(f"**Duration**: {self._format_duration(duration)}")
        lines.append("")

        # Steps completed
        if ctx.outputs:
            lines.append("### Steps Completed")
            for step_id, output in ctx.outputs.items():
                # Determine step status from output
                step_status = "✓"
                if isinstance(output, dict):
                    output_dict: dict[str, Any] = cast(dict[str, Any], output)
                    if output_dict.get("error"):
                        step_status = "✗"
                lines.append(f"- {step_status} `{step_id}`")
            lines.append("")

        # Error details if failed
        if error and status != "success":
            lines.append("### Error Details")
            lines.append("```")
            lines.append(error)
            lines.append("```")
            lines.append("")

        return "\n".join(lines)

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
