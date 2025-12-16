"""Shared conversion functions for sync commands.

This module contains helper functions for converting between API task models
and local filesystem task representations.
"""

from datetime import UTC, datetime
from typing import Any, Optional

from cli.models.common import Priority, Status
from cli.models.local_task import LocalTask, LocalTaskMeta
from cli.models.task import TaskUpdate
from cli.models.wrappers.task import Task


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


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.2 KB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


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


def _parse_plan_md(content: str) -> str:
    """Parse plan.md content, stripping the header if present.

    Args:
        content: Raw content of plan.md file

    Returns:
        Plan content without the "# Implementation Plan" header
    """
    lines = content.strip().split("\n")
    # Skip the header line if present
    start = 0
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("# implementation plan"):
            start = i + 1
            # Skip any empty lines after the header
            while start < len(lines) and not lines[start].strip():
                start += 1
            break
    return "\n".join(lines[start:]).strip()


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


def _detect_local_changes(
    local_task: LocalTask, server_task: Task
) -> dict[str, tuple[Any, Any]]:
    """Detect differences between local and server versions.

    Args:
        local_task: Local task from filesystem
        server_task: Task from server

    Returns:
        Dictionary of field names to (local_value, server_value) tuples
    """
    changes: dict[str, tuple[Any, Any]] = {}

    # Parse local task.md
    local_title, local_description = _parse_task_md(local_task.description)

    # Compare title
    if local_title and local_title != server_task.title:
        changes["title"] = (local_title, server_task.title)

    # Compare description
    server_description = server_task.description or ""
    if local_description != server_description:
        changes["description"] = (local_description, server_description)

    # Compare status
    if local_task.meta.status != server_task.status.value:
        changes["status"] = (local_task.meta.status, server_task.status.value)

    # Compare priority
    local_priority = local_task.meta.priority
    server_priority = server_task.priority.value if server_task.priority else 0
    if local_priority != server_priority:
        changes["priority"] = (local_priority, server_priority)

    return changes


def _build_update_from_local(
    local_task: LocalTask,
    status_override: Optional[str] = None,
    done_flag: bool = False,
) -> TaskUpdate:
    """Build TaskUpdate from local task data.

    Args:
        local_task: Local task to push
        status_override: Status to use instead of local status
        done_flag: If True, set status to 'done'

    Returns:
        TaskUpdate with local changes
    """
    # Parse task.md
    title, description = _parse_task_md(local_task.description)

    # Determine status
    status: Optional[Status] = None
    if done_flag:
        status = Status.DONE
    elif status_override:
        status = Status(status_override)
    else:
        status = Status(local_task.meta.status)

    # Map priority int to Priority enum
    priority_map = {
        -2: Priority.LOWEST,
        -1: Priority.LOW,
        0: Priority.NORMAL,
        1: Priority.HIGH,
        2: Priority.HIGHEST,
    }
    priority = priority_map.get(local_task.meta.priority, Priority.NORMAL)

    return TaskUpdate(
        title=title if title else None,
        description=description if description else None,
        status=status,
        priority=priority,
    )
