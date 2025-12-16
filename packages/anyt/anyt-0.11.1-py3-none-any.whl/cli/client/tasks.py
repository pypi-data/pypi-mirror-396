"""API client for task operations."""

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false

from datetime import datetime
from typing import Any

from sdk.generated.api_config import APIConfig
from sdk.generated.models.AddDependencyRequest import AddDependencyRequest
from sdk.generated.models.CreateTaskRequest import CreateTaskRequest
from sdk.generated.models.DependencyResponse import DependencyResponse
from sdk.generated.models.DependencyTaskInfo import (
    DependencyTaskInfo as GeneratedDependencyTaskInfo,
)
from sdk.generated.models.Task import Task as GeneratedTask
from sdk.generated.models.TaskListResponse import TaskListResponse
from sdk.generated.models.AssigneeType import AssigneeType as GeneratedAssigneeType
from sdk.generated.models.TaskStatus import TaskStatus as GeneratedTaskStatus
from sdk.generated.models.TaskUpdate import TaskUpdate as GeneratedTaskUpdate
from cli.models.common import AssigneeType, Status
from cli.models.dependency import TaskDependency
from cli.models.task import (
    TaskCreate,
    TaskFilters,
    TaskUpdate,
)
from cli.models.wrappers.task import Task, TaskDependencyInfo
from cli.models.wrappers.suggestion import TaskSuggestionsResponse
from cli.models.wrappers.bulk_update import BulkUpdateTasksResponse

# Import generated service functions for use and testing
# These are conditionally imported with pyright ignore for missing imports
from sdk.generated.services.async_Public_Tasks_service import (  # pyright: ignore[reportMissingImports]  # noqa: F401
    getPublicTask,
)
from sdk.generated.services.async_Task_Dependencies_service import (  # pyright: ignore[reportMissingImports]  # noqa: F401
    addTaskDependency,
    getTaskDependencies,
    getTaskDependents,
    removeTaskDependency,
)
from sdk.generated.services.async_Tasks_service import (  # pyright: ignore[reportMissingImports]  # noqa: F401
    bulkUpdateTasks,
    createTask,
    deleteTask,
    getTask,
    listTasks,
    updateTask,
)
from sdk.generated.services.async_Task_Suggestions_service import (  # pyright: ignore[reportMissingImports]  # noqa: F401
    getTaskSuggestions,
)


class TasksAPIClient:
    """API client for task operations using generated OpenAPI client.

    This client uses generated service functions directly instead of the adapter
    pattern to reduce indirection and improve type safety.
    """

    def __init__(
        self,
        base_url: str | None = None,
        auth_token: str | None = None,
        api_key: str | None = None,
        workspace_id: int | None = None,
    ):
        """Initialize with API configuration.

        Args:
            base_url: Base URL for the API
            auth_token: Optional JWT auth token
            api_key: Optional API key
            workspace_id: Optional workspace ID for workspace-scoped operations
        """
        self.base_url = base_url
        self.auth_token = auth_token
        self.api_key = api_key
        self.workspace_id = workspace_id

    @classmethod
    def from_config(cls) -> "TasksAPIClient":
        """Create client from configuration.

        Uses get_effective_api_config() to get API URL and key from
        workspace config or environment variables.

        Returns:
            TasksAPIClient instance
        """
        from cli.config import get_effective_api_config, get_workspace_config_or_none

        # Get API config (from workspace config or env vars)
        api_config = get_effective_api_config()

        # Try to load workspace_id from workspace config
        workspace_id: int | None = None
        ws_config = get_workspace_config_or_none()
        if ws_config:
            workspace_id = ws_config.workspace_id

        return cls(
            base_url=api_config.get("api_url"),
            auth_token=api_config.get("auth_token"),
            api_key=api_config.get("api_key"),
            workspace_id=workspace_id,
        )

    def _get_api_config(self) -> APIConfig:
        """Get APIConfig for generated client calls."""
        if not self.base_url:
            raise ValueError("API base URL not configured")
        return APIConfig(base_path=self.base_url, access_token=self.auth_token)

    def _convert_status_to_generated(self, status: Status | str) -> GeneratedTaskStatus:
        """Convert domain Status enum or string to generated TaskStatus."""
        # Handle both Status enum instances and string values
        # (Pydantic's use_enum_values=True converts enums to strings)
        if isinstance(status, Status):
            return GeneratedTaskStatus(status.value)
        return GeneratedTaskStatus(status)

    def _convert_assignee_type_to_generated(
        self, assignee_type: AssigneeType | str
    ) -> GeneratedAssigneeType:
        """Convert domain AssigneeType enum or string to generated AssigneeType."""
        # Handle both AssigneeType enum instances and string values
        # (Pydantic's use_enum_values=True converts enums to strings)
        if isinstance(assignee_type, AssigneeType):
            return GeneratedAssigneeType(assignee_type.value)
        return GeneratedAssigneeType(assignee_type)

    @staticmethod
    def _parse_datetime(dt_str: str | datetime) -> datetime:
        """Parse ISO 8601 datetime string or return datetime as-is."""
        # Handle datetime objects directly
        if isinstance(dt_str, datetime):
            return dt_str
        # Handle both with and without 'Z' suffix for strings
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
        return datetime.fromisoformat(dt_str)

    async def list_tasks(self, filters: TaskFilters) -> list[Task]:
        """List tasks with filters.

        Args:
            filters: Task filter criteria

        Returns:
            List of Task objects

        Raises:
            APIError: On HTTP errors
        """
        # Convert domain filters to API parameters
        params = filters.model_dump(exclude_none=True)

        # Validate required path parameters
        workspace_id = params.get("workspace_id")
        if workspace_id is None:
            raise ValueError(
                "workspace_id is required for listing tasks. "
                "Please provide workspace_id in TaskFilters or ensure workspace context is set."
            )

        # Convert status and priority lists to comma-separated strings
        if "status" in params and isinstance(params["status"], list):
            params["status"] = ",".join(params["status"])
        if "priority" in params and isinstance(params["priority"], list):
            params["priority"] = ",".join(str(p) for p in params["priority"])

        # Call generated service function (note: domain uses project_id, API expects project)
        response = await listTasks(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            project=params.get("project_id"),  # Map project_id -> project
            status=params.get("status"),
            priority=params.get("priority"),
            priority_gte=params.get("priority_gte"),
            priority_lte=params.get("priority_lte"),
            owner=params.get("owner"),
            creator=params.get("creator"),
            parent=params.get("parent"),
            created_after=params.get("created_after"),
            updated_after=params.get("updated_after"),
            completed_after=params.get("completed_after"),
            completed_before=params.get("completed_before"),
            limit=params.get("limit"),
            offset=params.get("offset"),
            sort_by=params.get("sort_by"),
            order=params.get("order"),
            X_API_Key=self.api_key,
        )

        # Extract items from response (no longer wrapped)
        response_data: TaskListResponse = response
        items = response_data.items if response_data and response_data.items else []

        # Wrap generated models in domain wrappers
        return [Task(item) for item in items]

    async def get_task(self, identifier: str) -> Task:
        """Get task by identifier.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID

        Returns:
            Task object

        Raises:
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        # Use workspace-specific endpoint (requires workspace_id)
        if self.workspace_id is None:
            raise ValueError(
                "workspace_id is required for getting tasks. "
                "Please ensure workspace context is set."
            )

        response = await getTask(
            api_config_override=self._get_api_config(),
            workspace_id=self.workspace_id,
            task_identifier=identifier,
            X_API_Key=self.api_key,
        )

        task_data: GeneratedTask = response
        return Task(task_data)

    async def get_task_by_workspace(self, workspace_id: int, identifier: str) -> Task:
        """Get task by workspace and identifier.

        Args:
            workspace_id: Workspace ID
            identifier: Task identifier within workspace

        Returns:
            Task object

        Raises:
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        response = await getTask(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            task_identifier=identifier,
            X_API_Key=self.api_key,
        )

        task_data: GeneratedTask = response
        return Task(task_data)

    async def get_task_by_uid(self, uid: str) -> Task:
        """Get task by UID.

        Args:
            uid: Task UID in string format (e.g., t_1Z)

        Returns:
            Task object

        Raises:
            NotFoundError: If task not found
            ForbiddenError: If user doesn't have access to the task
            APIError: On other HTTP errors
        """
        response = await getPublicTask(
            api_config_override=self._get_api_config(),
            uid=uid,
            X_API_Key=self.api_key,
        )

        task_data: GeneratedTask = response
        return Task(task_data)

    async def create_task(
        self, project_id: int, task: TaskCreate, workspace_id: int | None = None
    ) -> Task:
        """Create a new task.

        Args:
            project_id: Project ID to create task in
            task: Task creation data
            workspace_id: Optional workspace ID (uses self.workspace_id if not provided)

        Returns:
            Created Task object

        Raises:
            ValidationError: If task data is invalid
            ValueError: If workspace_id is not available
            APIError: On other HTTP errors
        """
        # Use provided workspace_id or fall back to instance workspace_id
        ws_id = workspace_id or self.workspace_id
        if ws_id is None:
            raise ValueError(
                "workspace_id is required for creating tasks. "
                "Please provide workspace_id or ensure workspace context is set."
            )

        # Convert domain model to generated API request model
        request = CreateTaskRequest(
            project_id=project_id,  # Now part of request body
            title=task.title,
            description=task.description,
            status=self._convert_status_to_generated(task.status)
            if task.status
            else None,
            priority=task.priority.value
            if task.priority and hasattr(task.priority, "value")
            else (task.priority if isinstance(task.priority, int) else None),
            owner_id=task.owner_id,
            assignee_type=self._convert_assignee_type_to_generated(task.assignee_type)
            if task.assignee_type
            else None,
            parent_id=task.parent_id,
            depends_on=task.depends_on,
            phase=task.phase,
            implementation_plan=task.implementation_plan,
        )

        # Call generated service function with workspace_id
        response = await createTask(
            api_config_override=self._get_api_config(),
            workspace_id=ws_id,  # Changed from project_id to workspace_id
            data=request,
            X_API_Key=self.api_key,
        )

        task_data: GeneratedTask = response
        return Task(task_data)

    async def update_task(self, identifier: str, updates: TaskUpdate) -> Task:
        """Update an existing task.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID
            updates: Task update data

        Returns:
            Updated Task object

        Raises:
            NotFoundError: If task not found
            ValidationError: If update data is invalid
            APIError: On other HTTP errors
        """
        # Use workspace-specific endpoint (requires workspace_id)
        if self.workspace_id is None:
            raise ValueError(
                "workspace_id is required for updating tasks. "
                "Please ensure workspace context is set."
            )

        # Convert domain model to generated API model
        request = GeneratedTaskUpdate(
            title=updates.title,
            description=updates.description,
            status=self._convert_status_to_generated(updates.status)
            if updates.status
            else None,
            priority=updates.priority.value
            if updates.priority and hasattr(updates.priority, "value")
            else (updates.priority if isinstance(updates.priority, int) else None),
            owner_id=updates.owner_id,
            assignee_type=self._convert_assignee_type_to_generated(
                updates.assignee_type
            )
            if updates.assignee_type
            else None,
            parent_id=updates.parent_id,
            phase=updates.phase,
            project_id=updates.project_id,
            implementation_plan=updates.implementation_plan,
        )

        # Call generated service function
        response = await updateTask(
            api_config_override=self._get_api_config(),
            workspace_id=self.workspace_id,
            task_identifier=identifier,
            data=request,
            If_Match=None,
            X_API_Key=self.api_key,
        )

        task_data: GeneratedTask = response
        return Task(task_data)

    async def delete_task(self, identifier: str) -> None:
        """Delete a task.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID

        Raises:
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        # Use workspace-specific endpoint (requires workspace_id)
        if self.workspace_id is None:
            raise ValueError(
                "workspace_id is required for deleting tasks. "
                "Please ensure workspace context is set."
            )

        await deleteTask(
            api_config_override=self._get_api_config(),
            workspace_id=self.workspace_id,
            task_identifier=identifier,
            X_API_Key=self.api_key,
        )

    async def add_task_dependency(
        self, identifier: str, depends_on: str
    ) -> TaskDependency:
        """Add a dependency to a task.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID
            depends_on: Identifier of task this depends on

        Returns:
            Created TaskDependency object

        Raises:
            NotFoundError: If either task not found
            ConflictError: If dependency would create a cycle
            APIError: On other HTTP errors
        """
        # Use workspace-specific endpoint (requires workspace_id)
        if self.workspace_id is None:
            raise ValueError(
                "workspace_id is required for adding task dependencies. "
                "Please ensure workspace context is set."
            )

        request = AddDependencyRequest(depends_on=depends_on)

        response = await addTaskDependency(
            api_config_override=self._get_api_config(),
            workspace_id=self.workspace_id,
            task_identifier=identifier,
            data=request,
            X_API_Key=self.api_key,
        )

        # Convert response to TaskDependency
        # Note: The generated API returns task identifiers as strings, but domain expects IDs as ints
        # We'll need to parse the identifiers or use placeholder values
        dep_response: DependencyResponse = response

        # Try to extract numeric IDs from identifiers (e.g., "DEV-42" -> 42)
        # If not possible, use 0 as placeholder (this is a known limitation)
        task_id_int = 0
        depends_on_id_int = 0

        try:
            # Try to parse as integer directly
            task_id_int = int(dep_response.task_id)
        except (ValueError, AttributeError):
            # If it's an identifier format, we can't convert - use 0
            task_id_int = 0

        try:
            depends_on_id_int = int(dep_response.depends_on)
        except (ValueError, AttributeError):
            depends_on_id_int = 0

        return TaskDependency(
            task_id=task_id_int,
            depends_on_id=depends_on_id_int,
            created_at=self._parse_datetime(dep_response.created_at),
        )

    async def remove_task_dependency(self, identifier: str, depends_on: str) -> None:
        """Remove a dependency from a task.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID
            depends_on: Identifier of task dependency to remove

        Raises:
            NotFoundError: If task or dependency not found
            APIError: On other HTTP errors
        """
        # Use workspace-specific endpoint (requires workspace_id)
        if self.workspace_id is None:
            raise ValueError(
                "workspace_id is required for removing task dependencies. "
                "Please ensure workspace context is set."
            )

        await removeTaskDependency(
            api_config_override=self._get_api_config(),
            workspace_id=self.workspace_id,
            task_identifier=identifier,
            depends_on_identifier=depends_on,
            X_API_Key=self.api_key,
        )

    async def get_task_dependencies(self, identifier: str) -> list[TaskDependencyInfo]:
        """Get tasks that this task depends on.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID

        Returns:
            List of TaskDependencyInfo objects this task depends on

        Raises:
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        # Use workspace-specific endpoint (requires workspace_id)
        if self.workspace_id is None:
            raise ValueError(
                "workspace_id is required for getting task dependencies. "
                "Please ensure workspace context is set."
            )

        response = await getTaskDependencies(
            api_config_override=self._get_api_config(),
            workspace_id=self.workspace_id,
            task_identifier=identifier,
            X_API_Key=self.api_key,
        )

        deps_data: list[GeneratedDependencyTaskInfo] = response

        return [TaskDependencyInfo(dep) for dep in deps_data]

    async def get_task_dependents(self, identifier: str) -> list[TaskDependencyInfo]:
        """Get tasks that depend on this task (blocked by this task).

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID

        Returns:
            List of TaskDependencyInfo objects that depend on this task

        Raises:
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        # Use workspace-specific endpoint (requires workspace_id)
        if self.workspace_id is None:
            raise ValueError(
                "workspace_id is required for getting task dependents. "
                "Please ensure workspace context is set."
            )

        response = await getTaskDependents(
            api_config_override=self._get_api_config(),
            workspace_id=self.workspace_id,
            task_identifier=identifier,
            X_API_Key=self.api_key,
        )

        deps_data: list[GeneratedDependencyTaskInfo] = response

        return [TaskDependencyInfo(dep) for dep in deps_data]

    async def get_task_events(
        self,
        identifier: str,
        event_type: str | None = None,
        _since: str | None = None,
        _limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get chronological timeline of events for a task.

        Note: This is a placeholder. The generated client doesn't have a
        dedicated events endpoint yet. Returns empty list for now.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID
            event_type: Optional filter by event type (created, updated, etc.)
            _since: Optional filter events since date (ISO format: YYYY-MM-DD) - unused
            _limit: Max number of events to return (default 50) - unused

        Returns:
            List of task events with timestamps and descriptions

        Raises:
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        # Suppress unused variable warnings - this is a placeholder method
        del identifier, event_type  # Will be used when endpoint is implemented
        return []

    async def suggest_tasks(
        self,
        workspace_id: int,
        max_suggestions: int = 10,
        status: str = "todo,backlog",
        include_assigned: bool = False,
        coding_agents: list[str] | None = None,
        project_id: int | None = None,
    ) -> TaskSuggestionsResponse:
        """Get task suggestions from backend.

        Uses the backend's suggestion algorithm to recommend tasks that are
        ready to work on (all dependencies complete). Results are sorted by
        priority.

        Args:
            workspace_id: Workspace to search in
            max_suggestions: Maximum number of suggestions (default 10, max 50)
            status: Comma-separated status values (default "todo,backlog")
            include_assigned: Include already-assigned tasks (default False)
            coding_agents: List of coding agent types to filter by (e.g., ["claude_code", "codex"])
            project_id: Optional project ID to filter suggestions to a specific project

        Returns:
            TaskSuggestionsResponse with suggestions, total_ready, and total_blocked

        Raises:
            APIError: On HTTP errors
        """
        # Convert list to comma-separated string for API
        coding_agents_str = ",".join(coding_agents) if coding_agents else None

        response = await getTaskSuggestions(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            project_id=project_id,
            max_suggestions=max_suggestions,
            status=status,
            include_assigned=include_assigned,
            coding_agent=None,
            coding_agents=coding_agents_str,
            X_API_Key=self.api_key,
        )

        # Response is now unwrapped, return wrapped domain model
        return TaskSuggestionsResponse(response)

    async def suggest_project_tasks(
        self,
        workspace_id: int,
        project_id: int,
        max_suggestions: int = 10,
        task_status: str = "todo,backlog",
        include_assigned: bool = False,
        coding_agents: list[str] | None = None,
    ) -> TaskSuggestionsResponse:
        """Get task suggestions for a specific project.

        Uses the backend's suggestion algorithm to recommend tasks that are
        ready to work on (all dependencies complete). Results are sorted by
        priority and scoped to the specified project.

        Args:
            workspace_id: Workspace containing the project
            project_id: Project to search for tasks
            max_suggestions: Maximum number of suggestions (default 10, max 50)
            task_status: Comma-separated status values (default "todo,backlog")
            include_assigned: Include already-assigned tasks (default False)
            coding_agents: List of coding agent types to filter by (e.g., ["claude_code", "codex"])

        Returns:
            TaskSuggestionsResponse with suggestions, total_ready, and total_blocked

        Raises:
            APIError: On HTTP errors
        """
        # Delegate to suggest_tasks with project_id
        return await self.suggest_tasks(
            workspace_id=workspace_id,
            max_suggestions=max_suggestions,
            status=task_status,
            include_assigned=include_assigned,
            coding_agents=coding_agents,
            project_id=project_id,
        )

    async def bulk_update(
        self,
        task_ids: list[str],
        updates: TaskUpdate,
        workspace_id: int | None = None,
    ) -> BulkUpdateTasksResponse:
        """Update multiple tasks at once.

        Args:
            task_ids: List of task identifiers (e.g., ["DEV-1", "DEV-2"])
            updates: TaskUpdate with fields to change
            workspace_id: Optional workspace ID (uses self.workspace_id if not provided)

        Returns:
            BulkUpdateTasksResponse with results

        Raises:
            ValueError: If task_ids is empty or workspace_id is not available
            APIError: If API call fails
        """
        from sdk.generated.models.BulkUpdateTasksRequest import BulkUpdateTasksRequest
        from sdk.generated.models.BulkUpdateTasksResponse import (
            BulkUpdateTasksResponse as GeneratedBulkUpdateTasksResponse,
        )

        if not task_ids:
            raise ValueError("task_ids cannot be empty")

        # Use provided workspace_id or fall back to instance workspace_id
        ws_id = workspace_id or self.workspace_id
        if ws_id is None:
            raise ValueError(
                "workspace_id is required for bulk update. "
                "Please provide workspace_id or ensure workspace context is set."
            )

        # Convert domain TaskUpdate to generated TaskUpdate
        generated_update = GeneratedTaskUpdate()
        if updates.title is not None:
            generated_update.title = updates.title
        if updates.description is not None:
            generated_update.description = updates.description
        if updates.status is not None:
            generated_update.status = self._convert_status_to_generated(updates.status)
        if updates.priority is not None:
            generated_update.priority = updates.priority
        if updates.owner_id is not None:
            generated_update.owner_id = updates.owner_id
        if updates.assignee_type is not None:
            generated_update.assignee_type = self._convert_assignee_type_to_generated(
                updates.assignee_type
            )
        if updates.project_id is not None:
            generated_update.project_id = updates.project_id
        if updates.parent_id is not None:
            generated_update.parent_id = updates.parent_id
        if updates.phase is not None:
            generated_update.phase = updates.phase
        if updates.implementation_plan is not None:
            generated_update.implementation_plan = updates.implementation_plan

        # Create request
        request = BulkUpdateTasksRequest(
            task_ids=task_ids,
            updates=generated_update,
        )

        # Call generated service function
        response = await bulkUpdateTasks(
            api_config_override=self._get_api_config(),
            workspace_id=ws_id,
            data=request,
            X_API_Key=self.api_key,
        )

        # Extract data from success response
        response_data: GeneratedBulkUpdateTasksResponse = response

        return BulkUpdateTasksResponse(response_data)
