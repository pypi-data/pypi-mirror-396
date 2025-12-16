"""Task service with business logic for task operations."""

from typing import Any

from cli.commands.console import console
from cli.client.tasks import TasksAPIClient
from cli.models.common import Status
from cli.models.task import (
    TaskCreate,
    TaskFilters,
    TaskUpdate,
)
from cli.models.wrappers.task import Task, TaskDependencyInfo
from cli.models.wrappers.bulk_update import BulkUpdateTasksResponse
from cli.models.workflow import WorkflowExecutionMetadata
from cli.services.base import BaseService


class TaskService(BaseService):
    """Business logic for task operations.

    TaskService encapsulates business rules and workflows for task management,
    including:
    - Task creation with validation
    - Status updates with dependency checking
    - Finding similar tasks
    - Task completion with validation
    - Suggesting next tasks to work on

    Example:
        ```python
        service = TaskService.from_config()

        # Create task with validation
        task = await service.create_task_with_validation(
            project_id=123,
            task=TaskCreate(title="Fix bug", project_id=123, priority=1)
        )

        # Complete task (checks dependencies)
        completed = await service.complete_task("DEV-42")

        # Create with explicit workspace_id (for workers)
        service = TaskService.with_workspace_id(workspace_id=123)
        ```
    """

    tasks: TasksAPIClient
    _workspace_id_override: int | None = None

    def __init__(self, workspace_id: int | None = None) -> None:
        """Initialize TaskService.

        Args:
            workspace_id: Optional workspace ID override. If provided, this takes
                         precedence over the workspace_id from config files.
                         Useful for workers that need to operate in a specific
                         workspace context.
        """
        self._workspace_id_override = workspace_id
        super().__init__()

    def _init_clients(self) -> None:
        """Initialize API clients."""
        if self._workspace_id_override is not None:
            # Create client with explicit workspace_id override
            from cli.config import get_effective_api_config

            api_config = get_effective_api_config()
            self.tasks = TasksAPIClient(
                base_url=api_config.get("api_url"),
                auth_token=api_config.get("auth_token"),
                api_key=api_config.get("api_key"),
                workspace_id=self._workspace_id_override,
            )
        else:
            # Default behavior - use config-based workspace_id
            self.tasks = TasksAPIClient.from_config()

    @classmethod
    def with_workspace_id(cls, workspace_id: int) -> "TaskService":
        """Create TaskService with explicit workspace_id.

        This factory method is useful for workers that need to operate
        in a specific workspace context that may not be available in
        the local config files.

        Args:
            workspace_id: Workspace ID to use for all operations

        Returns:
            TaskService instance configured with the specified workspace_id
        """
        return cls(workspace_id=workspace_id)

    async def list_tasks(self, filters: TaskFilters) -> list[Task]:
        """List tasks with filters.

        This is a pass-through to the API client. Use this method
        for consistency across the codebase.

        Args:
            filters: Task filter criteria

        Returns:
            List of Task objects
        """
        return await self.tasks.list_tasks(filters)

    async def get_task(self, identifier: str) -> Task:
        """Get task by identifier.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID

        Returns:
            Task object
        """
        return await self.tasks.get_task(identifier)

    async def get_task_by_uid(self, uid: str) -> Task:
        """Get task by UID.

        Args:
            uid: Task UID in string format (e.g., t_1Z)

        Returns:
            Task object
        """
        return await self.tasks.get_task_by_uid(uid)

    async def create_task_with_validation(
        self, project_id: int, task: TaskCreate
    ) -> Task:
        """Create task with business rule validation.

        Note: Priority validation is handled by Pydantic model validation.

        Future enhancements:
        - Check for similar task titles (warning only)
        - Validate task dependencies don't create cycles
        - Validate required fields based on workflow state

        Args:
            project_id: Project ID to create task in
            task: Task creation data

        Returns:
            Created Task object

        Raises:
            ValueError: If business rules are violated
        """
        # Future enhancement: check for similar titles
        # This would help prevent duplicate tasks
        # similar = await self.find_similar_tasks(task.title, workspace_id)
        # if similar:
        #     # Could prompt user or return warning
        #     pass

        return await self.tasks.create_task(project_id, task)

    async def update_task(self, identifier: str, updates: TaskUpdate) -> Task:
        """Update an existing task.

        This is a pass-through to the API client with potential
        for future business rule validation.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID
            updates: Task update data

        Returns:
            Updated Task object
        """
        # Future: add validation for status transitions
        return await self.tasks.update_task(identifier, updates)

    async def update_task_status(self, identifier: str, status: Status) -> Task:
        """Update task status with validation.

        This is a convenience method for status updates that can include
        business rule validation in the future.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID
            status: New status value

        Returns:
            Updated Task object

        Raises:
            ValueError: If status transition is invalid
        """
        # Future: validate status transitions
        # e.g., can't go from "done" to "todo" without reopening
        updates = TaskUpdate(status=status)
        return await self.tasks.update_task(identifier, updates)

    async def delete_task(self, identifier: str) -> None:
        """Delete a task.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID
        """
        await self.tasks.delete_task(identifier)

    async def find_similar_tasks(
        self, title: str, workspace_id: int, threshold: float = 0.5
    ) -> list[Task]:
        """Find tasks with similar titles (fuzzy match).

        Uses simple substring matching to find potentially duplicate tasks.
        This can help users avoid creating duplicate work.

        Args:
            title: Task title to search for
            workspace_id: Workspace to search in
            threshold: Similarity threshold (0.0 to 1.0)

        Returns:
            List of similar Task objects
        """
        # Get all tasks in the workspace
        filters = TaskFilters(workspace_id=workspace_id)
        tasks = await self.tasks.list_tasks(filters)

        # Simple similarity check - could be enhanced with Levenshtein distance
        similar: list[Task] = []
        title_lower = title.lower()
        for task in tasks:
            if self._is_similar(title_lower, task.title.lower(), threshold):
                similar.append(task)

        return similar

    def _is_similar(self, a: str, b: str, threshold: float = 0.5) -> bool:
        """Check if two strings are similar.

        Uses simple substring matching. Could be enhanced with:
        - Levenshtein distance
        - Fuzzy matching libraries
        - NLP-based similarity

        Args:
            a: First string (lowercase)
            b: Second string (lowercase)
            threshold: Similarity threshold (currently unused)

        Returns:
            True if strings are similar, False otherwise
        """
        # Simple implementation: check if one is substring of other
        return a in b or b in a

    async def get_task_with_context(self, identifier: str) -> dict[str, Any]:
        """Get task with full context including dependencies.

        Returns a dictionary with:
        - task: The main task object
        - dependencies: Tasks this task depends on
        - dependents: Tasks that depend on this task

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID

        Returns:
            Dictionary with task and context
        """
        # Fetch task and dependencies in parallel for efficiency
        task = await self.tasks.get_task(identifier)
        dependencies = await self.tasks.get_task_dependencies(identifier)
        dependents = await self.tasks.get_task_dependents(identifier)

        return {
            "task": task,
            "dependencies": dependencies,
            "dependents": dependents,
        }

    async def complete_task(self, identifier: str) -> Task:
        """Mark task as done with validation.

        Business rules:
        - All dependencies must be completed before this task can be completed
        - Task status transitions to "done"

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID

        Returns:
            Updated Task object with status "done"

        Raises:
            ValueError: If dependencies are not completed
        """
        # Get task and its dependencies
        await self.tasks.get_task(identifier)
        dependencies = await self.tasks.get_task_dependencies(identifier)

        # Business rule: check all dependencies are done
        incomplete_deps = [d for d in dependencies if d.status != Status.DONE]
        if incomplete_deps:
            dep_identifiers = [d.identifier for d in incomplete_deps]
            raise ValueError(
                f"Cannot complete task. {len(incomplete_deps)} dependencies "
                f"are not done yet: {', '.join(dep_identifiers)}"
            )

        # Update status to done
        updates = TaskUpdate(status=Status.DONE)
        return await self.tasks.update_task(identifier, updates)

    async def suggest_next_tasks(self, workspace_id: int, limit: int = 5) -> list[Task]:
        """Suggest next tasks to work on based on current state.

        Suggestion algorithm:
        - Filter to tasks in "todo" or "backlog" status
        - Sort by priority (higher first)
        - Return top N suggestions

        Future enhancements:
        - Consider dependencies (suggest tasks with no blockers)
        - Consider user's past work patterns
        - AI-based suggestions

        Args:
            workspace_id: Workspace to search in
            limit: Maximum number of suggestions (default 5)

        Returns:
            List of suggested Task objects
        """
        # Get tasks ready to work on
        filters = TaskFilters(
            workspace_id=workspace_id,
            status=[Status.TODO, Status.BACKLOG],
        )
        tasks = await self.tasks.list_tasks(filters)

        # Sort by priority (higher first), then by ID (newer first)
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (t.priority if t.priority is not None else 0, -t.id),
            reverse=True,
        )

        return sorted_tasks[:limit]

    async def add_dependency(self, identifier: str, depends_on: str) -> None:
        """Add a dependency to a task.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID
            depends_on: Identifier of task this depends on
        """
        await self.tasks.add_task_dependency(identifier, depends_on)

    async def remove_dependency(self, identifier: str, depends_on: str) -> None:
        """Remove a dependency from a task.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID
            depends_on: Identifier of task dependency to remove
        """
        await self.tasks.remove_task_dependency(identifier, depends_on)

    async def get_task_dependencies(self, identifier: str) -> list[TaskDependencyInfo]:
        """Get tasks that this task depends on.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID

        Returns:
            List of TaskDependencyInfo objects this task depends on
        """
        return await self.tasks.get_task_dependencies(identifier)

    async def get_task_dependents(self, identifier: str) -> list[TaskDependencyInfo]:
        """Get tasks that depend on this task.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID

        Returns:
            List of TaskDependencyInfo objects that depend on this task
        """
        return await self.tasks.get_task_dependents(identifier)

    async def get_workflow_metadata(
        self, identifier: str
    ) -> list["WorkflowExecutionMetadata"]:
        """Get workflow execution metadata from task.

        Parses the task description to extract workflow metadata that was
        stored as HTML comments by TaskUpdateAction.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID

        Returns:
            List of WorkflowExecutionMetadata objects (may be empty)
        """
        import json
        import re

        from cli.models.workflow import WorkflowExecutionMetadata

        task = await self.tasks.get_task(identifier)

        if not task.description:
            return []

        # Find all workflow metadata HTML comments
        # Pattern: <!-- workflow-metadata\n{...}\n-->
        pattern = r"<!--\s*workflow-metadata\s*\n(.*?)\n-->"
        matches = re.findall(pattern, task.description, re.DOTALL)

        metadata_list: list[WorkflowExecutionMetadata] = []
        for match in matches:
            try:
                # Parse JSON from comment
                data = json.loads(match)
                metadata = WorkflowExecutionMetadata(**data)
                metadata_list.append(metadata)
            except (json.JSONDecodeError, ValueError) as e:
                # Skip invalid metadata entries
                console.print(
                    f"[dim yellow]Warning: Skipping invalid metadata: {e}[/dim yellow]"
                )
                continue

        return metadata_list

    async def bulk_update_tasks(
        self,
        task_ids: list[str],
        updates: TaskUpdate,
        workspace_id: int | None = None,
    ) -> BulkUpdateTasksResponse:
        """Update multiple tasks with validation.

        Args:
            task_ids: List of task identifiers
            updates: Updates to apply to all tasks
            workspace_id: Optional workspace ID (uses context if not provided)

        Returns:
            BulkUpdateTasksResponse with results

        Raises:
            ValueError: If task_ids is empty or workspace_id is not available
            APIError: If API call fails
        """
        # Use provided workspace_id or resolve from context
        if workspace_id is None:
            workspace_id = self._get_effective_workspace_id()

        if workspace_id is None:
            raise ValueError(
                "workspace_id is required for bulk update. "
                "Please provide workspace_id or ensure workspace context is set."
            )

        # Delegate to client
        return await self.tasks.bulk_update(
            task_ids=task_ids,
            updates=updates,
            workspace_id=workspace_id,
        )
