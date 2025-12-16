"""User service with business logic for user operations."""

from cli.client.users import UsersAPIClient
from cli.models.user import User, UserInitResponse
from cli.services.base import BaseService


class UserService(BaseService):
    """Business logic for user operations.

    UserService encapsulates business rules and workflows for user
    management, including:
    - User initialization (first-time setup)
    - Getting current user information

    Example:
        ```python
        service = UserService.from_config()

        # Initialize new user (creates default workspace & project)
        init_result = await service.init_user()
        print(f"Workspace: {init_result.workspace_name}")
        print(f"Project: {init_result.project_name}")

        # Get current user
        user = await service.get_current_user()
        ```
    """

    users: UsersAPIClient

    def _init_clients(self) -> None:
        """Initialize API clients."""
        self.users = UsersAPIClient.from_config()

    async def init_user(self) -> UserInitResponse:
        """Initialize user account with default workspace and project.

        This is the primary method for first-time user setup. It:
        1. Calls POST /v1/users/init to create default workspace & project
        2. Updates local config with workspace information
        3. Returns initialization details

        The endpoint is idempotent - safe to call multiple times.

        Returns:
            UserInitResponse with user_id, workspace, and project details

        Raises:
            APIError: If initialization fails
        """
        result = await self.users.init_user()

        # Note: In the new config system, workspace config is saved separately
        # by the init command after creating the workspace
        # No automatic config update needed here

        return result

    async def get_current_user(self) -> User:
        """Get current authenticated user information.

        Returns:
            User object with id, email, name, created_at

        Raises:
            APIError: On HTTP errors
        """
        return await self.users.get_current_user()
