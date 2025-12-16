"""API client for pull request operations."""

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false

from sdk.generated.api_config import APIConfig
from sdk.generated.models.CreateTaskPRRequest import CreateTaskPRRequest
from sdk.generated.models.PRStatus import PRStatus as GeneratedPRStatus
from sdk.generated.models.PullRequest import PullRequest as GeneratedPullRequest
from sdk.generated.models.UpdatePRRequest import UpdatePRRequest
from sdk.generated.services.async_Pull_Requests_service import (  # pyright: ignore[reportMissingImports]
    createTaskPullRequest,
    listTaskPullRequests,
    updateTaskPullRequest,
)


class PullRequestsAPIClient:
    """API client for pull request operations using generated OpenAPI client.

    This client uses generated service functions directly instead of the adapter
    pattern to reduce indirection and improve type safety.

    All PR operations are task-scoped - PRs are always associated with a task.
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
    def from_config(cls) -> "PullRequestsAPIClient":
        """Create client from configuration.

        Uses get_effective_api_config() to get API URL and key from
        workspace config or environment variables.

        Returns:
            PullRequestsAPIClient instance
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

    async def create_pr(
        self,
        identifier: str,
        pr_number: int,
        pr_url: str,
        head_branch: str,
        base_branch: str,
        head_sha: str,
        pr_status: GeneratedPRStatus | None = None,
    ) -> GeneratedPullRequest:
        """Create a new pull request record for a task.

        Args:
            identifier: Task identifier (e.g., DEV-42)
            pr_number: GitHub PR number
            pr_url: URL to the PR on GitHub
            head_branch: Source branch name
            base_branch: Target branch name
            head_sha: SHA of the head commit
            pr_status: Optional PR status (draft, open, merged, closed)

        Returns:
            Created PullRequest object

        Raises:
            ValueError: If workspace_id is not available
            ValidationError: If PR data is invalid
            APIError: On other HTTP errors
        """
        if self.workspace_id is None:
            raise ValueError(
                "workspace_id is required for creating pull requests. "
                "Please ensure workspace context is set."
            )

        # Create request (task is identified via URL path, not in body)
        request = CreateTaskPRRequest(
            pr_number=pr_number,
            pr_url=pr_url,
            head_branch=head_branch,
            base_branch=base_branch,
            head_sha=head_sha,
            pr_status=pr_status,
        )

        # Call generated service function
        response: GeneratedPullRequest = await createTaskPullRequest(
            api_config_override=self._get_api_config(),
            workspace_id=self.workspace_id,
            identifier=identifier,
            data=request,
            X_API_Key=self.api_key,
        )

        return response

    async def list_task_prs(self, identifier: str) -> list[GeneratedPullRequest]:
        """Get all pull requests for a specific task.

        Args:
            identifier: Task identifier (e.g., DEV-42)

        Returns:
            List of PullRequest objects for the task

        Raises:
            ValueError: If workspace_id is not available
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        if self.workspace_id is None:
            raise ValueError(
                "workspace_id is required for listing task pull requests. "
                "Please ensure workspace context is set."
            )

        response: list[GeneratedPullRequest] = await listTaskPullRequests(
            api_config_override=self._get_api_config(),
            workspace_id=self.workspace_id,
            identifier=identifier,
            X_API_Key=self.api_key,
        )

        return response

    async def update_pr(
        self,
        identifier: str,
        pr_id: int,
        updates: UpdatePRRequest,
    ) -> GeneratedPullRequest:
        """Update an existing pull request record.

        Args:
            identifier: Task identifier (e.g., DEV-42)
            pr_id: ID of the pull request to update
            updates: UpdatePRRequest with fields to update

        Returns:
            Updated PullRequest object

        Raises:
            ValueError: If workspace_id is not available
            NotFoundError: If PR or task not found
            ValidationError: If update data is invalid
            APIError: On other HTTP errors
        """
        if self.workspace_id is None:
            raise ValueError(
                "workspace_id is required for updating pull requests. "
                "Please ensure workspace context is set."
            )

        response = await updateTaskPullRequest(
            api_config_override=self._get_api_config(),
            workspace_id=self.workspace_id,
            identifier=identifier,
            pr_id=pr_id,
            data=updates,
            X_API_Key=self.api_key,
        )

        return response
