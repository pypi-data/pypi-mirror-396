"""Shared helpers for task update operations."""

from typing import Any, Optional

from cli.commands.formatters import output_json, output_json_error
from cli.commands.validators import validate_priority, validate_status
from cli.models.common import Priority, Status
from cli.models.task import TaskUpdate
from cli.models.wrappers.task import Task
from cli.services.task_service import TaskService

from ..helpers import console

# Re-export validators for backwards compatibility
__all__ = ["validate_priority", "validate_status"]


async def get_task_or_error(
    identifier: str,
    service: TaskService,
    json_output: bool = False,
    error_message: Optional[str] = None,
    suggestion: Optional[str] = None,
) -> Optional[Task]:
    """Fetch a task by identifier with standardized 404 error handling.

    Args:
        identifier: Task identifier (e.g., DEV-42)
        service: TaskService instance for fetching
        json_output: Whether to output errors as JSON
        error_message: Custom error message (default: "Task '{identifier}' not found")
        suggestion: Additional suggestion text for console output

    Returns:
        Task if found, None if not found (after printing error)
    """
    try:
        return await service.get_task(identifier)
    except Exception as e:  # noqa: BLE001 - Intentionally broad: handle any API error
        error_str = str(e)
        if "404" in error_str:
            msg = error_message or f"Task '{identifier}' not found"
            if json_output:
                output_json_error("NOT_FOUND", msg)
            else:
                console.print(f"[red]Error:[/red] {msg}")
                if suggestion:
                    console.print(f"[dim]{suggestion}[/dim]")
            return None
        # Re-raise non-404 errors
        raise


def build_task_update(
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    owner: Optional[str] = None,
    implementation_plan: Optional[str] = None,
) -> TaskUpdate:
    """Build a TaskUpdate model from optional parameters.

    Args:
        title: New task title
        description: New task description
        status: New status string
        priority: New priority value
        owner: New owner ID
        implementation_plan: Implementation plan in markdown format

    Returns:
        TaskUpdate model with non-None values
    """
    # Convert priority to enum
    priority_enum = None
    if priority is not None:
        priority_enum = Priority(priority)

    # Convert status to enum
    status_enum = None
    if status is not None:
        status_enum = Status(status)

    return TaskUpdate(
        title=title,
        description=description,
        status=status_enum,
        priority=priority_enum,
        owner_id=owner,
        implementation_plan=implementation_plan,
    )


async def resolve_task_identifiers(
    raw_identifiers: list[str],
    service: TaskService,
    workspace_identifier: Optional[str],
    json_output: bool = False,
) -> tuple[list[str], list[dict[str, Any]]]:
    """Resolve raw identifiers to task identifiers.

    Args:
        raw_identifiers: List of raw task identifiers (UIDs or workspace identifiers)
        service: Task service for resolution
        workspace_identifier: Workspace identifier for normalization
        json_output: Whether to output JSON format

    Returns:
        Tuple of (resolved_ids, errors)
    """
    from ..helpers import resolve_task_identifier

    resolved_ids: list[str] = []
    errors: list[dict[str, Any]] = []

    for raw_id in raw_identifiers:
        try:
            resolved = await resolve_task_identifier(
                raw_id, service, workspace_identifier
            )
            resolved_ids.append(resolved)
        except Exception as e:  # noqa: BLE001 - Intentionally broad: gracefully handle resolution failures
            error_msg = str(e)
            error = format_error_result(
                raw_id, "ResolutionError", f"Failed to resolve identifier: {error_msg}"
            )
            errors.append(error)
            if not json_output:
                console.print(
                    f"[red]Error:[/red] Failed to resolve identifier '{raw_id}': {error_msg}"
                )

    return resolved_ids, errors


def format_error_result(
    task_id: str,
    error_type: str,
    message: str,
    **extra: Any,
) -> dict[str, Any]:
    """Format an error result dictionary.

    Args:
        task_id: Task identifier
        error_type: Type of error (e.g., "NotFound", "ValidationError")
        message: Error message
        **extra: Additional fields to include

    Returns:
        Error dictionary
    """
    result: dict[str, Any] = {
        "task_id": task_id,
        "error": error_type,
        "message": message,
    }
    result.update(extra)
    return result


def display_dry_run_preview(
    task_id: str,
    current_task: Task,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    owner: Optional[str] = None,
    implementation_plan: Optional[str] = None,
) -> None:
    """Display a preview of changes in dry-run mode.

    Args:
        task_id: Task identifier
        current_task: Current task data
        title: New title (if changing)
        description: New description (if changing)
        status: New status (if changing)
        priority: New priority (if changing)
        owner: New owner (if changing)
        implementation_plan: New implementation plan (if changing)
    """
    console.print(f"[yellow][Preview][/yellow] Would update {task_id}:")

    if title is not None:
        console.print(f"  title: {current_task.title} -> {title}")

    if description is not None:
        console.print("  description: <updated>")

    if status is not None:
        current_status = (
            current_task.status.value
            if isinstance(current_task.status, Status)
            else current_task.status
        )
        console.print(f"  status: {current_status} -> {status}")

    if priority is not None:
        current_priority = (
            current_task.priority.value
            if isinstance(current_task.priority, Priority)
            else current_task.priority
        )
        console.print(f"  priority: {current_priority} -> {priority}")

    if owner is not None:
        console.print(f"  owner: {current_task.owner_id} -> {owner}")

    if implementation_plan is not None:
        console.print("  implementation_plan: <updated>")

    console.print(f"  updated_at: {current_task.updated_at} -> <now>")
    console.print()


def display_no_task_error(
    json_output: bool, command_example: str, pick_example: str
) -> None:
    """Display error for missing task identifier.

    Args:
        json_output: Whether to output JSON format
        command_example: Example command with task ID
        pick_example: Example pick command
    """
    if json_output:
        output_json(
            {
                "error": "ValidationError",
                "message": "No task identifier provided and no active task set",
                "suggestions": [
                    f"Specify a task: {command_example}",
                    f"Or pick a task first: {pick_example}",
                ],
            },
            success=False,
        )
    else:
        console.print(
            "[red]Error:[/red] No task identifier provided and no active task set"
        )
        console.print(f"Specify a task: [cyan]{command_example}[/cyan]")
        console.print(f"Or pick a task first: [cyan]{pick_example}[/cyan]")
