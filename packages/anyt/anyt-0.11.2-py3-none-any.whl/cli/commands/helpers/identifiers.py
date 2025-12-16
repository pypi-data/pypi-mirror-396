"""Task identifier resolution and normalization utilities."""

from typing import Any, Optional

from cli.config import ActiveTaskConfig
from cli.models.task import TaskFilters
from cli.services.task_service import TaskService

__all__ = [
    "get_active_task_id",
    "resolve_task_identifier",
    "normalize_identifier",
    "find_similar_tasks",
]


def get_active_task_id() -> Optional[str]:
    """Get the active task identifier from .anyt/active_task.json.

    Returns:
        Task identifier if an active task is set, None otherwise.
    """
    active_task = ActiveTaskConfig.load()
    return active_task.identifier if active_task else None


async def resolve_task_identifier(
    identifier: str, task_service: TaskService, workspace_prefix: Optional[str] = None
) -> str:
    """Resolve task identifier, converting UIDs to workspace-scoped identifiers.

    This function enables commands to accept both UIDs (t_xxx) and workspace identifiers (DEV-42).
    UIDs are converted to workspace identifiers by fetching the task.

    Handles:
    - UIDs (t_xxx) → Fetches task and returns workspace identifier (DEV-42)
    - Workspace identifiers (DEV-42) → Normalizes and returns
    - Numeric IDs (42) → Normalizes with workspace prefix

    Args:
        identifier: Task identifier (UID, workspace identifier, or numeric ID)
        task_service: TaskService for fetching task details
        workspace_prefix: Workspace prefix (e.g., "DEV") to use if identifier is just a number

    Returns:
        Workspace-scoped task identifier (e.g., DEV-42)

    Raises:
        Exception: If task not found or UID is invalid
    """
    identifier = identifier.strip()

    # Check if it's a UID (starts with 't_')
    if identifier.startswith("t_"):
        # Fetch task by UID to get workspace identifier
        task = await task_service.get_task_by_uid(identifier)
        # Type annotation: identifier is a string attribute from the generated model
        return str(task.identifier)

    # Otherwise, normalize the identifier
    return normalize_identifier(identifier, workspace_prefix)


def normalize_identifier(task_id: str, workspace_prefix: Optional[str] = None) -> str:
    """Normalize task identifier for fuzzy matching.

    Handles variations like:
    - DEV-42 → DEV-42 (full identifier)
    - dev42 → DEV-42 (case insensitive, no dash)
    - 42 → 42 (just number)
    - DEV 42 → DEV-42 (with space)

    Args:
        task_id: The task identifier to normalize
        workspace_prefix: Workspace prefix (e.g., "DEV") to use if identifier is just a number

    Returns:
        Normalized task identifier
    """
    task_id = task_id.strip()

    # If it's just a number, prepend workspace prefix if provided
    if task_id.isdigit():
        if workspace_prefix:
            return f"{workspace_prefix}-{task_id}"
        return task_id

    # If it contains a dash already (DEV-42), normalize case
    if "-" in task_id:
        parts = task_id.split("-", 1)
        return f"{parts[0].upper()}-{parts[1]}"

    # If it contains a space (DEV 42), replace with dash
    if " " in task_id:
        parts = task_id.split(" ", 1)
        return f"{parts[0].upper()}-{parts[1]}"

    # Try to split alphanumeric (dev42 → DEV-42)
    # Find where digits start
    for i, char in enumerate(task_id):
        if char.isdigit():
            if i > 0:
                prefix = task_id[:i].upper()
                number = task_id[i:]
                return f"{prefix}-{number}"
            break

    # If nothing matched, return as uppercase
    return task_id.upper()


async def find_similar_tasks(
    task_service: TaskService, workspace_id: int, identifier: str, limit: int = 3
) -> list[dict[str, Any]]:
    """Find tasks with similar identifiers using fuzzy matching.

    Args:
        task_service: TaskService for fetching tasks
        workspace_id: Workspace ID to search in
        identifier: The identifier that wasn't found
        limit: Maximum number of suggestions to return

    Returns:
        List of similar tasks (as dicts for backward compatibility)
    """
    import difflib

    try:
        # Fetch recent tasks from workspace
        filters = TaskFilters(
            workspace_id=workspace_id, limit=50, sort_by="updated_at", order="desc"
        )
        tasks = await task_service.list_tasks(filters)

        if not tasks:
            return []

        # Get all task identifiers
        identifiers = [task.identifier or str(task.id) for task in tasks]

        # Use difflib to find similar matches
        matches = difflib.get_close_matches(
            identifier.upper(),
            [id.upper() for id in identifiers],
            n=limit,
            cutoff=0.4,  # Lower cutoff for more suggestions
        )

        # Return the corresponding tasks as dicts
        similar_tasks: list[dict[str, Any]] = []
        for match in matches:
            for task in tasks:
                task_id = task.identifier or str(task.id)
                if task_id.upper() == match:
                    # Convert Task model to dict for backward compatibility
                    similar_tasks.append(task.model_dump())
                    break

        return similar_tasks

    except Exception:  # noqa: BLE001 - Intentionally broad: return empty list on any API/parse error
        # Return empty list if similar task lookup fails - lookup is best-effort
        return []
