"""Local task service for filesystem-first task management.

This service handles reading and writing tasks to the local filesystem,
enabling any AI tool to work with tasks without requiring API access.
"""

import json
from pathlib import Path
from typing import Optional

from cli.models.local_task import (
    LocalTask,
    LocalTaskMeta,
    get_task_context_dir,
    get_task_dir,
    get_task_md_path,
    get_task_meta_path,
    get_tasks_dir,
)


class LocalTaskService:
    """Service for managing locally synced tasks.

    LocalTaskService provides filesystem operations for tasks stored in
    .anyt/tasks/{identifier}/ directories. This enables any AI tool
    (Claude Code, Cursor, Gemini, etc.) to work with tasks by simply
    reading local files.

    File Structure:
        .anyt/tasks/{identifier}/
        ├── task.md          # Task description (markdown)
        ├── .meta.json       # Task metadata (JSON)
        └── context/         # Local AI context files

    Example:
        ```python
        service = LocalTaskService()

        # Check if task exists locally
        if service.task_exists("DEV-01"):
            task = service.read_task("DEV-01")
            print(f"Task: {task.meta.title}")

        # Write a task locally
        service.write_task(meta, description="Fix the login bug")

        # List all local tasks
        for task in service.list_local_tasks():
            print(f"{task.meta.identifier}: {task.meta.title}")
        ```
    """

    def __init__(self, directory: Optional[Path] = None) -> None:
        """Initialize LocalTaskService.

        Args:
            directory: Base directory for .anyt/tasks/. Defaults to current working directory.
        """
        self._directory = directory

    @property
    def directory(self) -> Path:
        """Get the base directory."""
        return self._directory if self._directory else Path.cwd()

    @property
    def tasks_dir(self) -> Path:
        """Get the .anyt/tasks/ directory path."""
        return get_tasks_dir(self._directory)

    def task_exists(self, identifier: str) -> bool:
        """Check if a task exists locally.

        A task is considered to exist if its .meta.json file exists.

        Args:
            identifier: Task identifier (e.g., "DEV-01")

        Returns:
            True if the task exists locally, False otherwise
        """
        meta_path = get_task_meta_path(identifier, self._directory)
        return meta_path.exists()

    def read_task(self, identifier: str) -> LocalTask:
        """Read a task from the local filesystem.

        Reads both .meta.json and task.md to construct a complete LocalTask.

        Args:
            identifier: Task identifier (e.g., "DEV-01")

        Returns:
            LocalTask with metadata and description

        Raises:
            FileNotFoundError: If task does not exist locally
            json.JSONDecodeError: If .meta.json is invalid JSON
            ValueError: If .meta.json has invalid data
        """
        task_dir = get_task_dir(identifier, self._directory)
        meta_path = get_task_meta_path(identifier, self._directory)
        md_path = get_task_md_path(identifier, self._directory)

        if not meta_path.exists():
            raise FileNotFoundError(f"Task {identifier} not found locally")

        # Read metadata
        with open(meta_path, "r", encoding="utf-8") as f:
            meta_data = json.load(f)
        meta = LocalTaskMeta.model_validate(meta_data)

        # Read description (optional, may not exist)
        description = ""
        if md_path.exists():
            description = md_path.read_text(encoding="utf-8")

        return LocalTask(meta=meta, description=description, path=task_dir)

    def write_task(self, meta: LocalTaskMeta, description: str = "") -> LocalTask:
        """Write a task to the local filesystem.

        Creates the task directory structure and writes both .meta.json
        and task.md files.

        Args:
            meta: Task metadata to write
            description: Task description content (markdown)

        Returns:
            LocalTask representing the written task

        Raises:
            OSError: If unable to write files (permissions, disk full, etc.)
        """
        task_dir = get_task_dir(meta.identifier, self._directory)
        meta_path = get_task_meta_path(meta.identifier, self._directory)
        md_path = get_task_md_path(meta.identifier, self._directory)
        context_dir = get_task_context_dir(meta.identifier, self._directory)

        # Create directory structure
        task_dir.mkdir(parents=True, exist_ok=True)
        context_dir.mkdir(parents=True, exist_ok=True)

        # Write metadata
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta.model_dump(mode="json"), f, indent=2, default=str)

        # Write description
        md_path.write_text(description, encoding="utf-8")

        return LocalTask(meta=meta, description=description, path=task_dir)

    def delete_task(self, identifier: str) -> bool:
        """Delete a task from the local filesystem.

        Removes the entire task directory including all files.

        Args:
            identifier: Task identifier (e.g., "DEV-01")

        Returns:
            True if task was deleted, False if it didn't exist

        Raises:
            OSError: If unable to delete files (permissions, etc.)
        """
        task_dir = get_task_dir(identifier, self._directory)

        if not task_dir.exists():
            return False

        # Remove all files in the directory
        import shutil

        shutil.rmtree(task_dir)
        return True

    def list_local_tasks(self) -> list[LocalTask]:
        """List all locally synced tasks.

        Returns:
            List of LocalTask objects for all tasks in .anyt/tasks/

        Note:
            Tasks with invalid .meta.json files are skipped with a warning.
        """
        tasks: list[LocalTask] = []
        tasks_dir = self.tasks_dir

        if not tasks_dir.exists():
            return tasks

        for item in tasks_dir.iterdir():
            if item.is_dir():
                identifier = item.name
                try:
                    task = self.read_task(identifier)
                    tasks.append(task)
                except (FileNotFoundError, json.JSONDecodeError, ValueError):
                    # Skip invalid tasks silently
                    continue

        return tasks

    def update_task_meta(self, identifier: str, **updates: object) -> LocalTaskMeta:
        """Update specific fields in a task's metadata.

        Reads the existing metadata, updates specified fields, and writes back.

        Args:
            identifier: Task identifier (e.g., "DEV-01")
            **updates: Field name/value pairs to update

        Returns:
            Updated LocalTaskMeta

        Raises:
            FileNotFoundError: If task does not exist locally
            ValueError: If updates contain invalid field names or values
        """
        task = self.read_task(identifier)

        # Update fields
        meta_dict = task.meta.model_dump()
        for key, value in updates.items():
            if key not in meta_dict:
                raise ValueError(f"Invalid field: {key}")
            meta_dict[key] = value

        # Validate and write
        new_meta = LocalTaskMeta.model_validate(meta_dict)
        self.write_task(new_meta, task.description)

        return new_meta

    def update_task_description(self, identifier: str, description: str) -> LocalTask:
        """Update a task's description.

        Args:
            identifier: Task identifier (e.g., "DEV-01")
            description: New description content (markdown)

        Returns:
            Updated LocalTask

        Raises:
            FileNotFoundError: If task does not exist locally
        """
        task = self.read_task(identifier)
        return self.write_task(task.meta, description)

    def ensure_tasks_dir(self) -> Path:
        """Ensure the .anyt/tasks/ directory exists.

        Creates the directory if it doesn't exist.

        Returns:
            Path to the .anyt/tasks/ directory
        """
        tasks_dir = self.tasks_dir
        tasks_dir.mkdir(parents=True, exist_ok=True)
        return tasks_dir
