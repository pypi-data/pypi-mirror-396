"""API client for task comment operations."""

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false

from datetime import datetime

from sdk.generated.api_config import APIConfig
from sdk.generated.models.CommentResponse import CommentResponse
from sdk.generated.models.CreateCommentRequest import CreateCommentRequest
from sdk.generated.services.async_Task_Comments_service import (  # pyright: ignore[reportMissingImports]
    createTaskComment,
    listTaskComments,
)
from cli.models.comment import Comment, CommentCreate


class CommentsAPIClient:
    """API client for task comment operations using generated OpenAPI client."""

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
    def from_config(cls) -> "CommentsAPIClient":
        """Create client from configuration.

        Uses get_effective_api_config() to get API URL and key from
        workspace config or environment variables.

        Returns:
            CommentsAPIClient instance
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

    def _convert_comment_response(self, response: CommentResponse) -> Comment:
        """Convert generated CommentResponse to domain Comment model."""
        return Comment(
            id=response.id,
            content=response.content,
            created_at=datetime.fromisoformat(
                response.created_at.replace("Z", "+00:00")
            ),
            user_id=None,  # Not in CommentResponse
            task_id=response.task_id,
            mentioned_users=response.mentioned_users,
        )

    async def create_comment(self, identifier: str, comment: CommentCreate) -> Comment:
        """Create a comment on a task.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID
            comment: Comment creation data

        Returns:
            Created Comment object

        Raises:
            ValueError: If author_id is not provided in comment
            NotFoundError: If task not found
            ValidationError: If comment data is invalid
            APIError: On other HTTP errors
        """
        # Validate author_id is provided (required for X-API-Key header)
        if not comment.author_id:
            raise ValueError(
                "Comment author_id is required (API key or user ID). "
                "Ensure API key is configured or user is authenticated."
            )

        # Validate workspace_id
        if self.workspace_id is None:
            raise ValueError(
                "workspace_id is required for creating comments. "
                "Please ensure workspace context is set."
            )

        # Convert domain model to generated API request model
        request = CreateCommentRequest(
            content=comment.content,
            mentioned_users=comment.mentioned_users,
            parent_id=comment.parent_id,
        )

        # Call generated service function with all required parameters
        response = await createTaskComment(
            api_config_override=self._get_api_config(),
            workspace_id=self.workspace_id,
            task_identifier=identifier,
            data=request,
            X_API_Key=comment.author_id,  # API key or user ID (validated above)
        )

        # Convert generated response to domain model

        return self._convert_comment_response(response)

    async def list_comments(self, identifier: str) -> list[Comment]:
        """List all comments on a task.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID

        Returns:
            List of Comment objects, ordered by creation time

        Raises:
            ValueError: If api_key is not configured
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        # Validate api_key is configured (required for X-API-Key header)
        if not self.api_key:
            raise ValueError(
                "API key not configured. "
                "Set ANYT_API_KEY environment variable to configure API authentication."
            )

        # Validate workspace_id
        if self.workspace_id is None:
            raise ValueError(
                "workspace_id is required for listing comments. "
                "Please ensure workspace context is set."
            )

        # Call generated service function
        response = await listTaskComments(
            api_config_override=self._get_api_config(),
            workspace_id=self.workspace_id,
            task_identifier=identifier,
            limit=None,
            offset=None,
            X_API_Key=self.api_key,  # Validated above
        )

        # Convert generated responses to domain models (no longer wrapped)

        response_data = response
        comments = response_data.comments if response_data else []
        return [self._convert_comment_response(c) for c in comments]
