"""Local task models for filesystem-first task management.

These models represent task data stored locally in the .anyt/tasks/ directory,
enabling any AI tool to work with tasks by reading local files.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LocalTaskMeta(BaseModel):
    """Metadata for a locally synced task stored in .meta.json.

    This model represents the structured metadata for tasks synced to the local
    filesystem. The actual task description is stored separately in task.md.

    File Structure:
        .anyt/tasks/{identifier}/
        ├── task.md          # Task description (markdown)
        ├── .meta.json       # This metadata (JSON)
        └── context/         # Local AI context files

    Attributes:
        identifier: Task identifier (e.g., "DEV-01")
        id: Server-side task ID
        title: Task title
        status: Task status (backlog, todo, active, done, etc.)
        priority: Task priority (-2 to 2)
        owner_id: Owner user ID (optional)
        project_id: Project ID
        workspace_id: Workspace ID
        pulled_at: When the task was last pulled from server
        pushed_at: When the task was last pushed to server (None if never pushed)
        server_updated_at: Server's last update timestamp

    Example:
        >>> meta = LocalTaskMeta(
        ...     identifier="DEV-01",
        ...     id=123,
        ...     title="Fix login bug",
        ...     status="active",
        ...     priority=1,
        ...     project_id=1,
        ...     workspace_id=1,
        ...     pulled_at=datetime.now(),
        ...     server_updated_at=datetime.now(),
        ... )
    """

    identifier: str = Field(description="Task identifier (e.g., 'DEV-01')")
    id: int = Field(description="Server-side task ID")
    title: str = Field(description="Task title")
    status: str = Field(description="Task status")
    priority: int = Field(default=0, description="Task priority (-2 to 2)")
    owner_id: Optional[str] = Field(default=None, description="Owner user ID")
    project_id: int = Field(description="Project ID")
    workspace_id: int = Field(description="Workspace ID")
    pulled_at: datetime = Field(description="When task was last pulled from server")
    pushed_at: Optional[datetime] = Field(
        default=None, description="When task was last pushed to server"
    )
    server_updated_at: datetime = Field(description="Server's last update timestamp")


class LocalTask(BaseModel):
    """Complete local task representation combining metadata and description.

    This model combines the .meta.json data with the task.md content for
    a complete local task representation.

    Attributes:
        meta: Task metadata from .meta.json
        description: Task description content from task.md
        path: Path to the task directory
    """

    meta: LocalTaskMeta = Field(description="Task metadata")
    description: str = Field(default="", description="Task description from task.md")
    path: Path = Field(description="Path to task directory")

    model_config = ConfigDict(arbitrary_types_allowed=True)


def get_tasks_dir(directory: Optional[Path] = None) -> Path:
    """Get the path to the .anyt/tasks/ directory.

    Args:
        directory: Base directory. Defaults to current working directory.

    Returns:
        Path to .anyt/tasks/ directory
    """
    if directory is None:
        directory = Path.cwd()
    return directory / ".anyt" / "tasks"


def get_task_dir(identifier: str, directory: Optional[Path] = None) -> Path:
    """Get the path to a specific task's directory.

    Args:
        identifier: Task identifier (e.g., "DEV-01")
        directory: Base directory. Defaults to current working directory.

    Returns:
        Path to .anyt/tasks/{identifier}/ directory
    """
    return get_tasks_dir(directory) / identifier


def get_task_meta_path(identifier: str, directory: Optional[Path] = None) -> Path:
    """Get the path to a task's .meta.json file.

    Args:
        identifier: Task identifier (e.g., "DEV-01")
        directory: Base directory. Defaults to current working directory.

    Returns:
        Path to .anyt/tasks/{identifier}/.meta.json
    """
    return get_task_dir(identifier, directory) / ".meta.json"


def get_task_md_path(identifier: str, directory: Optional[Path] = None) -> Path:
    """Get the path to a task's task.md file.

    Args:
        identifier: Task identifier (e.g., "DEV-01")
        directory: Base directory. Defaults to current working directory.

    Returns:
        Path to .anyt/tasks/{identifier}/task.md
    """
    return get_task_dir(identifier, directory) / "task.md"


def get_task_context_dir(identifier: str, directory: Optional[Path] = None) -> Path:
    """Get the path to a task's context directory.

    Args:
        identifier: Task identifier (e.g., "DEV-01")
        directory: Base directory. Defaults to current working directory.

    Returns:
        Path to .anyt/tasks/{identifier}/context/
    """
    return get_task_dir(identifier, directory) / "context"


def get_task_checklist_path(identifier: str, directory: Optional[Path] = None) -> Path:
    """Get the path to a task's checklist.md file.

    Args:
        identifier: Task identifier (e.g., "DEV-01")
        directory: Base directory. Defaults to current working directory.

    Returns:
        Path to .anyt/tasks/{identifier}/checklist.md
    """
    return get_task_dir(identifier, directory) / "checklist.md"
