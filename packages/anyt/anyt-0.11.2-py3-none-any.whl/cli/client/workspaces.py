"""API client for workspace operations."""

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false

from datetime import datetime
from typing import Any, cast

from sdk.generated.api_config import APIConfig
from sdk.generated.models.CreateWorkspaceRequest import CreateWorkspaceRequest
from sdk.generated.models.Workspace import Workspace as GeneratedWorkspace
from sdk.generated.models.DependencyGraphResponse import (
    DependencyGraphResponse as GeneratedDependencyGraphResponse,
)
from cli.models.workspace import Workspace, WorkspaceCreate
from cli.models.wrappers.dependency_graph import (
    DependencyGraphResponse as DomainDependencyGraphResponse,
)

# Import generated service functions
from sdk.generated.services.async_Health_service import (  # pyright: ignore[reportMissingImports]  # noqa: F401
    healthCheck,
)
from sdk.generated.services.async_Workspaces_service import (  # pyright: ignore[reportMissingImports]  # noqa: F401
    createWorkspace,
    getWorkspace,
    listWorkspaces,
)
from sdk.generated.services.async_Workspace_Dependencies_service import (  # pyright: ignore[reportMissingImports]  # noqa: F401
    getWorkspaceDependencyGraph,
)
from cli.models.wrappers.dependency_graph import DependencyGraphResponse


class WorkspacesAPIClient:
    """API client for workspace operations using generated OpenAPI client.

    This client uses generated service functions directly instead of the adapter
    pattern to reduce indirection and improve type safety.
    """

    def __init__(
        self,
        base_url: str | None = None,
        auth_token: str | None = None,
        api_key: str | None = None,
    ):
        """Initialize with API configuration.

        Args:
            base_url: Base URL for the API
            auth_token: Optional JWT auth token
            api_key: Optional API key
        """
        self.base_url = base_url
        self.auth_token = auth_token
        self.api_key = api_key

    @classmethod
    def from_config(cls) -> "WorkspacesAPIClient":
        """Create client from configuration.

        Uses get_effective_api_config() to get API URL and key from
        workspace config or environment variables.

        Returns:
            WorkspacesAPIClient instance
        """
        from cli.config import get_effective_api_config

        api_config = get_effective_api_config()
        return cls(
            base_url=api_config.get("api_url"),
            auth_token=api_config.get("auth_token"),
            api_key=api_config.get("api_key"),
        )

    def _get_api_config(self) -> APIConfig:
        """Get APIConfig for generated client calls.

        When using API keys, we pass a placeholder token since the actual
        authentication happens via the X-API-Key header.
        """
        if not self.base_url:
            raise ValueError(
                "API base URL not configured. "
                "Run 'anyt env add' to configure an environment."
            )
        # Use auth_token if available, otherwise use placeholder for API keys
        token = self.auth_token if self.auth_token else "agent_auth"
        return APIConfig(base_path=self.base_url, access_token=token)

    def _is_authenticated(self) -> bool:
        """Check if client has valid authentication credentials.

        Returns:
            True if auth_token or api_key is configured
        """
        return bool(self.auth_token or self.api_key)

    def _parse_datetime(self, dt_str: str | datetime) -> datetime:
        """Parse ISO 8601 datetime string or return datetime as-is."""
        # Handle datetime objects directly
        if isinstance(dt_str, datetime):
            return dt_str
        # Handle both with and without 'Z' suffix for strings
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
        return datetime.fromisoformat(dt_str)

    def _convert_workspace_response(self, response: GeneratedWorkspace) -> Workspace:
        """Convert generated Workspace to domain Workspace model."""
        return Workspace(
            id=response.id,
            identifier=response.identifier,
            name=response.name,
            description=response.description,
            owner_id=response.owner_id,
            task_counter=response.task_counter,
            created_at=self._parse_datetime(response.created_at),
            updated_at=self._parse_datetime(response.updated_at),
            deleted_at=self._parse_datetime(response.deleted_at)
            if response.deleted_at
            else None,
        )

    async def list_workspaces(self) -> list[Workspace]:
        """List accessible workspaces.

        Returns:
            List of Workspace objects the authenticated user/agent has access to

        Raises:
            APIError: On HTTP errors
        """
        if not self._is_authenticated():
            raise ValueError(
                "Authentication not configured. Run 'anyt auth login' to authenticate."
            )

        response = await listWorkspaces(
            api_config_override=self._get_api_config(),
            X_API_Key=self.api_key,
        )

        # Extract data from response (no longer wrapped)

        api_response = response
        items = api_response.items if api_response and api_response.items else []

        return [self._convert_workspace_response(ws) for ws in items]

    async def get_workspace(self, workspace_id: str | int) -> Workspace:
        """Get a specific workspace by ID.

        Args:
            workspace_id: The workspace identifier (can be string or integer ID)

        Returns:
            Workspace object

        Raises:
            NotFoundError: If workspace not found
            APIError: On other HTTP errors
        """
        if not self._is_authenticated():
            raise ValueError(
                "Authentication not configured. Run 'anyt auth login' to authenticate."
            )

        # Convert to int if string
        ws_id = int(workspace_id) if isinstance(workspace_id, str) else workspace_id

        response = await getWorkspace(
            api_config_override=self._get_api_config(),
            workspace_id=ws_id,
            X_API_Key=self.api_key,
        )

        # Extract data from response (no longer wrapped)

        workspace_data = response

        return self._convert_workspace_response(workspace_data)

    async def get_current_workspace(self) -> Workspace:
        """Get the current/default workspace for the authenticated user.

        Returns the first workspace by creation date from the user's accessible
        workspaces.

        Returns:
            Workspace object

        Raises:
            NotFoundError: If user has no workspaces
            APIError: On other HTTP errors
        """
        from cli.client.exceptions import NotFoundError

        workspaces = await self.list_workspaces()
        if not workspaces:
            raise NotFoundError("No workspaces found for the authenticated user")

        # Return first workspace (list is already sorted by created_at from API)
        return workspaces[0]

    async def create_workspace(self, workspace: WorkspaceCreate) -> Workspace:
        """Create a new workspace.

        Args:
            workspace: Workspace creation data

        Returns:
            Created Workspace object

        Raises:
            ValidationError: If workspace data is invalid
            ConflictError: If identifier already exists
            APIError: On other HTTP errors
        """
        if not self._is_authenticated():
            raise ValueError(
                "Authentication not configured. Run 'anyt auth login' to authenticate."
            )

        # Convert domain model to generated request model
        request = CreateWorkspaceRequest(
            identifier=workspace.identifier,
            name=workspace.name,
            description=workspace.description,
        )

        response = await createWorkspace(
            api_config_override=self._get_api_config(),
            data=request,
            X_API_Key=self.api_key,
        )

        # Extract data from response (no longer wrapped)

        workspace_data = response

        return self._convert_workspace_response(workspace_data)

    async def health_check(self) -> dict[str, Any]:
        """Check API health status.

        Returns:
            Health status response from the API

        Raises:
            APIError: If the health check fails
        """
        response = await healthCheck(api_config_override=self._get_api_config())

        # Extract data from HealthResponse
        api_response = cast(Any, response)
        return {
            "status": api_response.status,
            "timestamp": api_response.timestamp,
        }

    async def get_dependency_graph(
        self, workspace_id: int, project_id: int | None = None
    ) -> DependencyGraphResponse:
        """Get complete dependency graph for workspace.

        This endpoint returns all tasks and their dependency relationships
        in a single API call, enabling efficient dependency analysis.

        Args:
            workspace_id: The workspace ID
            project_id: Optional project ID to filter tasks by project

        Returns:
            DependencyGraphResponse with all tasks (nodes) and dependencies (edges)

        Raises:
            NotFoundError: If workspace not found
            APIError: On other HTTP errors
        """
        if not self._is_authenticated():
            raise ValueError(
                "Authentication not configured. Run 'anyt auth login' to authenticate."
            )

        response = await getWorkspaceDependencyGraph(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            project_id=project_id,
            X_API_Key=self.api_key,
        )

        # Extract data from response (no longer wrapped)
        graph_data: GeneratedDependencyGraphResponse = response

        return DomainDependencyGraphResponse.from_generated(graph_data)
