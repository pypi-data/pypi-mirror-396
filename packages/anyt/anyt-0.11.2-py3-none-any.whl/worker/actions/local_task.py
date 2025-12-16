"""
Local task workflow actions for filesystem-first task management.

These actions enable workflows to read/write task files directly from the
filesystem, allowing AI agents to work with local task context.
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Optional

from cli.models.common import Priority, Status
from cli.models.local_task import (
    LocalTaskMeta,
    get_task_checklist_path,
    get_task_context_dir,
)
from cli.models.task import TaskUpdate
from cli.models.wrappers.task import Task
from cli.services.local_task_service import LocalTaskService

from ..context import ExecutionContext
from .base import Action


def _task_to_local_meta(task: Task) -> LocalTaskMeta:
    """Convert a Task from the API to LocalTaskMeta for local storage.

    Args:
        task: Task object from the API

    Returns:
        LocalTaskMeta ready for local storage
    """
    now = datetime.now(UTC)

    return LocalTaskMeta(
        identifier=task.identifier,
        id=task.id,
        title=task.title,
        status=task.status.value,
        priority=task.priority.value if task.priority else 0,
        owner_id=task.owner_id,
        project_id=task.project_id,
        workspace_id=task.workspace_id,
        pulled_at=now,
        pushed_at=None,
        server_updated_at=task.updated_at,
    )


def _get_context_files(identifier: str, directory: Optional[Path] = None) -> list[str]:
    """Get list of files in the task's context directory.

    Args:
        identifier: Task identifier
        directory: Base directory (defaults to cwd)

    Returns:
        List of filenames in the context directory
    """
    context_dir = get_task_context_dir(identifier, directory)
    if not context_dir.exists():
        return []

    files: list[str] = []
    for item in context_dir.iterdir():
        if item.is_file():
            files.append(item.name)
    return files


def _get_context_content(
    identifier: str, directory: Optional[Path] = None, max_file_size: int = 50000
) -> Dict[str, str]:
    """Get content of all files in the task's context directory.

    Args:
        identifier: Task identifier
        directory: Base directory (defaults to cwd)
        max_file_size: Maximum file size to read (default 50KB)

    Returns:
        Dictionary of filename -> content
    """
    context_dir = get_task_context_dir(identifier, directory)
    if not context_dir.exists():
        return {}

    content: Dict[str, str] = {}
    for item in context_dir.iterdir():
        if item.is_file():
            try:
                # Skip files that are too large
                if item.stat().st_size > max_file_size:
                    content[item.name] = (
                        f"<file too large: {item.stat().st_size} bytes>"
                    )
                    continue
                content[item.name] = item.read_text(encoding="utf-8")
            except Exception as e:
                content[item.name] = f"<error reading file: {e}>"
    return content


def _format_context_content(context: Dict[str, str]) -> str:
    """Format context content dictionary for prompt inclusion.

    Args:
        context: Dictionary of filename -> content

    Returns:
        Formatted string with all context files
    """
    if not context:
        return "_No additional context files provided._"

    parts = []
    for filename, file_content in sorted(context.items()):
        parts.append(f"### {filename}\n```\n{file_content}\n```")
    return "\n\n".join(parts)


def _parse_task_md(content: str) -> tuple[str, str]:
    """Parse task.md into (title, description).

    The title is extracted from the first line starting with '# '.
    The description is the remaining content after the title.

    Args:
        content: Raw content of task.md file

    Returns:
        Tuple of (title, description)
    """
    lines = content.strip().split("\n")
    title = ""
    desc_start = 0

    for i, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
            desc_start = i + 1
            break

    description = "\n".join(lines[desc_start:]).strip()
    return title, description


def _parse_checklist_md(content: str) -> str:
    """Parse checklist.md content, stripping the header if present.

    Args:
        content: Raw content of checklist.md file

    Returns:
        Checklist content without the "# Checklist" header
    """
    lines = content.strip().split("\n")
    # Skip the header line if present
    start = 0
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("# checklist"):
            start = i + 1
            # Skip any empty lines after the header
            while start < len(lines) and not lines[start].strip():
                start += 1
            break
    return "\n".join(lines[start:]).strip()


class LocalTaskPullAction(Action):
    """Pull a task from the server to local filesystem.

    This action downloads task data from the AnyTask server and stores it
    locally in .anyt/tasks/{identifier}/ for AI tools to access.

    Parameters:
        task_id: Task identifier to pull (optional, uses ctx.task if not provided)

    Outputs:
        path: Path to the task directory
        task_md: Content of task.md file
        meta: Task metadata as dictionary
        pulled: Whether the pull was successful
    """

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute the pull action."""
        # Get task_id from params or context
        task_id = params.get("task_id") or ctx.task.get("identifier")
        if not task_id:
            raise ValueError("Task identifier required (via task_id param or context)")

        # Initialize task client with appropriate authentication
        task_client = self._get_task_client(ctx)

        # Fetch task from server
        task = await task_client.get_task(task_id)

        # Initialize local service
        local_service = LocalTaskService(ctx.workspace_dir)
        local_service.ensure_tasks_dir()

        # Convert and write to local filesystem
        meta = _task_to_local_meta(task)
        description = task.description or ""

        # Create task.md content with title header
        task_md_content = f"# {task.title}\n\n{description}"

        local_task = local_service.write_task(meta, task_md_content)

        # Write checklist.md if task has a checklist
        gen_task = task.to_generated()
        checklist_md_content = ""
        has_checklist = False
        if gen_task.checklist:
            checklist_md_content = f"# Checklist\n\n{gen_task.checklist}"
            checklist_path = get_task_checklist_path(task.identifier, ctx.workspace_dir)
            checklist_path.write_text(checklist_md_content, encoding="utf-8")
            has_checklist = True

        return {
            "path": str(local_task.path),
            "task_md": task_md_content,
            "checklist_md": checklist_md_content,
            "has_checklist": has_checklist,
            "meta": meta.model_dump(mode="json"),
            "pulled": True,
        }

    def _get_task_client(self, ctx: ExecutionContext) -> "_TaskClientAdapter":
        """Get task client adapter with appropriate authentication.

        Uses ANYT_API_KEY with standard API clients.

        Args:
            ctx: Execution context (checked for env vars first, then os.environ)
        """
        import os

        from cli.client.tasks import TasksAPIClient

        # Get authentication tokens - check context env first, then os.environ
        ctx_env = ctx.env or {}
        api_key = ctx_env.get("ANYT_API_KEY") or os.getenv("ANYT_API_KEY")
        api_url = (
            ctx_env.get("ANYT_API_URL")
            or os.getenv("ANYT_API_URL")
            or "https://api.anyt.dev"
        )

        if api_key:
            task_client = TasksAPIClient(
                base_url=api_url,
                api_key=api_key,
                workspace_id=ctx.workspace_id,
            )
            return _TaskClientAdapter(tasks_client=task_client)
        else:
            raise ValueError(
                "Authentication required: Set ANYT_API_KEY environment variable."
            )


class _TaskClientAdapter:
    """Adapter to provide unified interface for task operations.

    Uses TasksAPIClient for all operations.
    """

    def __init__(
        self,
        tasks_client: Any = None,
    ) -> None:
        self.tasks_client = tasks_client

    async def get_task(self, identifier: str) -> Task:
        """Get task by identifier."""
        result: Task = await self.tasks_client.get_task(identifier)
        return result

    async def update_task(self, identifier: str, updates: TaskUpdate) -> Task:
        """Update task by identifier."""
        result: Task = await self.tasks_client.update_task(identifier, updates)
        return result


class LocalTaskPushAction(Action):
    """Push local task changes to the server.

    This action uploads local task.md and metadata changes back to the
    AnyTask server.

    Parameters:
        task_id: Task identifier to push (optional, uses ctx.task if not provided)
        status: Status override (optional)

    Outputs:
        pushed: Whether the push was successful
        updated_fields: List of fields that were updated
    """

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute the push action."""
        # Get task_id from params or context
        task_id = params.get("task_id") or ctx.task.get("identifier")
        if not task_id:
            raise ValueError("Task identifier required (via task_id param or context)")

        status_override = params.get("status")

        # Initialize local service
        local_service = LocalTaskService(ctx.workspace_dir)

        # Check if task exists locally
        if not local_service.task_exists(task_id):
            raise ValueError(f"Task '{task_id}' not found locally")

        # Read local task
        local_task = local_service.read_task(task_id)

        # Get task client
        task_client = self._get_task_client(ctx)

        # Get current server state for comparison
        server_task = await task_client.get_task(task_id)

        # Detect changes
        updated_fields: list[str] = []
        local_title, local_description = _parse_task_md(local_task.description)

        # Build update
        update_dict: Dict[str, Any] = {}

        if local_title and local_title != server_task.title:
            update_dict["title"] = local_title
            updated_fields.append("title")

        server_description = server_task.description or ""
        if local_description != server_description:
            update_dict["description"] = local_description
            updated_fields.append("description")

        if status_override:
            update_dict["status"] = Status(status_override)
            updated_fields.append("status")
        elif local_task.meta.status != server_task.status.value:
            update_dict["status"] = Status(local_task.meta.status)
            updated_fields.append("status")

        if local_task.meta.priority != (
            server_task.priority.value if server_task.priority else 0
        ):
            priority_map = {
                -2: Priority.LOWEST,
                -1: Priority.LOW,
                0: Priority.NORMAL,
                1: Priority.HIGH,
                2: Priority.HIGHEST,
            }
            update_dict["priority"] = priority_map.get(
                local_task.meta.priority, Priority.NORMAL
            )
            updated_fields.append("priority")

        # Check for local checklist.md
        checklist_path = get_task_checklist_path(task_id, ctx.workspace_dir)
        if checklist_path.exists():
            local_checklist = _parse_checklist_md(
                checklist_path.read_text(encoding="utf-8")
            )
            gen_task = server_task.to_generated()
            server_checklist = gen_task.checklist or ""
            if local_checklist != server_checklist:
                update_dict["checklist"] = local_checklist
                updated_fields.append("checklist")

        if not updated_fields:
            return {
                "pushed": False,
                "updated_fields": [],
                "message": "No local changes to push",
            }

        # Push update
        update = TaskUpdate(**update_dict)
        updated_task = await task_client.update_task(task_id, update)

        # Update local .meta.json with pushed_at timestamp
        now = datetime.now(UTC)
        local_service.update_task_meta(
            task_id,
            pushed_at=now,
            server_updated_at=updated_task.updated_at,
            status=updated_task.status.value,
            priority=updated_task.priority.value if updated_task.priority else 0,
        )

        return {
            "pushed": True,
            "updated_fields": updated_fields,
        }

    def _get_task_client(self, ctx: ExecutionContext) -> "_TaskClientAdapter":
        """Get task client adapter with appropriate authentication.

        Uses ANYT_API_KEY with standard API clients.

        Args:
            ctx: Execution context (checked for env vars first, then os.environ)
        """
        import os

        from cli.client.tasks import TasksAPIClient

        # Get authentication tokens - check context env first, then os.environ
        ctx_env = ctx.env or {}
        api_key = ctx_env.get("ANYT_API_KEY") or os.getenv("ANYT_API_KEY")
        api_url = (
            ctx_env.get("ANYT_API_URL")
            or os.getenv("ANYT_API_URL")
            or "https://api.anyt.dev"
        )

        if api_key:
            task_client = TasksAPIClient(
                base_url=api_url,
                api_key=api_key,
                workspace_id=ctx.workspace_id,
            )
            return _TaskClientAdapter(tasks_client=task_client)
        else:
            raise ValueError(
                "Authentication required: Set ANYT_API_KEY environment variable."
            )


class LocalTaskReadAction(Action):
    """Read a task from the local filesystem without API calls.

    This action reads task data directly from the local .anyt/tasks/ directory,
    enabling offline access to task information.

    Parameters:
        task_id: Task identifier to read (optional, uses ctx.task if not provided)
        include_context_content: Whether to include context file contents (default: true)

    Outputs:
        exists: Whether the task exists locally
        task_md: Content of task.md file (empty if not exists)
        checklist_md: Content of checklist.md file (empty if not exists)
        meta: Task metadata as dictionary (empty if not exists)
        context_files: List of files in the context directory
        context_content: Formatted string of all context file contents
        context_content_raw: Dictionary of filename -> content
    """

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute the read action."""
        # Get task_id from params or context
        task_id = params.get("task_id") or ctx.task.get("identifier")
        if not task_id:
            raise ValueError("Task identifier required (via task_id param or context)")

        include_context = params.get("include_context_content", True)

        # Initialize local service
        local_service = LocalTaskService(ctx.workspace_dir)

        # Check if task exists
        if not local_service.task_exists(task_id):
            return {
                "exists": False,
                "task_md": "",
                "checklist_md": "",
                "meta": {},
                "context_files": [],
                "context_content": "",
                "context_content_raw": {},
            }

        # Read task
        local_task = local_service.read_task(task_id)

        # Read checklist.md if exists
        checklist_md = ""
        checklist_path = get_task_checklist_path(task_id, ctx.workspace_dir)
        if checklist_path.exists():
            checklist_md = checklist_path.read_text(encoding="utf-8")

        # Get context files
        context_files = _get_context_files(task_id, ctx.workspace_dir)

        # Get context content if requested
        context_content_raw: Dict[str, str] = {}
        context_content = ""
        if include_context:
            context_content_raw = _get_context_content(task_id, ctx.workspace_dir)
            context_content = _format_context_content(context_content_raw)

        return {
            "exists": True,
            "task_md": local_task.description,
            "checklist_md": checklist_md,
            "meta": local_task.meta.model_dump(mode="json"),
            "context_files": context_files,
            "context_content": context_content,
            "context_content_raw": context_content_raw,
        }


class LocalTaskWriteAction(Action):
    """Write to a local task without API calls.

    This action writes directly to the local task files, useful for
    updating task content during workflow execution.

    Parameters:
        task_id: Task identifier to write (optional, uses ctx.task if not provided)
        task_md: New task.md content (optional)
        status: New status (optional)
        append_md: Content to append to task.md (optional)

    Outputs:
        written: Whether the write was successful
        path: Path to the task directory
    """

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute the write action."""
        # Get task_id from params or context
        task_id = params.get("task_id") or ctx.task.get("identifier")
        if not task_id:
            raise ValueError("Task identifier required (via task_id param or context)")

        task_md = params.get("task_md")
        status = params.get("status")
        append_md = params.get("append_md")

        # Initialize local service
        local_service = LocalTaskService(ctx.workspace_dir)

        # Check if task exists
        if not local_service.task_exists(task_id):
            raise ValueError(
                f"Task '{task_id}' not found locally. Run local_task_pull first."
            )

        # Read current task
        local_task = local_service.read_task(task_id)

        # Update description if provided
        new_description = local_task.description
        if task_md is not None:
            new_description = task_md
        elif append_md:
            new_description = local_task.description + "\n\n" + append_md

        # Update metadata if status changed
        new_meta = local_task.meta
        if status:
            meta_dict = local_task.meta.model_dump()
            meta_dict["status"] = status
            new_meta = LocalTaskMeta.model_validate(meta_dict)

        # Write updated task
        updated_task = local_service.write_task(new_meta, new_description)

        return {
            "written": True,
            "path": str(updated_task.path),
        }


class TaskValidateSectionsAction(Action):
    """Validate that a task.md contains required sections.

    This action checks if the task markdown contains all required sections,
    enabling workflows to conditionally enrich incomplete tasks.

    Parameters:
        task_md: Content of task.md to validate
        required_sections: List of section headers to check for

    Outputs:
        is_complete: Whether all required sections are present
        missing_sections: List of missing section headers
        found_sections: List of found section headers
        completeness_score: Percentage of required sections found (0.0 to 1.0)
    """

    # Default required sections for a well-specified task
    DEFAULT_SECTIONS = [
        "Problem Statement",
        "Acceptance Criteria",
        "Implementation Plan",
        "Files to Modify",
        "Testing Checklist",
    ]

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute the validation action."""
        task_md = params.get("task_md", "")
        required_sections = params.get("required_sections", self.DEFAULT_SECTIONS)

        # Normalize section names for comparison
        def normalize(s: str) -> str:
            return s.lower().strip().replace(" ", "").replace("-", "").replace("_", "")

        # Extract all ## headers from the markdown
        found_sections: list[str] = []
        found_normalized: set[str] = set()

        for line in task_md.split("\n"):
            line = line.strip()
            if line.startswith("## "):
                section_name = line[3:].strip()
                found_sections.append(section_name)
                found_normalized.add(normalize(section_name))

        # Check which required sections are missing
        missing_sections: list[str] = []
        for section in required_sections:
            if normalize(section) not in found_normalized:
                missing_sections.append(section)

        # Calculate completeness
        total = len(required_sections)
        found_count = total - len(missing_sections)
        completeness_score = found_count / total if total > 0 else 1.0

        return {
            "is_complete": len(missing_sections) == 0,
            "missing_sections": missing_sections,
            "found_sections": found_sections,
            "completeness_score": completeness_score,
        }
