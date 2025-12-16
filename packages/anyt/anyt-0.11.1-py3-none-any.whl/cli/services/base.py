"""Base service class with common patterns."""

from abc import ABC
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from cli.config import WorkspaceConfig


class BaseService(ABC):
    """Base service class with common functionality.

    All services should inherit from BaseService to get:
    - Client initialization
    - Common error handling patterns
    - from_config() class method for easy instantiation

    Services now use the new config system:
    - API clients load config from environment variables or workspace config
    - No more GlobalConfig dependency

    Example:
        ```python
        class MyService(BaseService):
            def _init_clients(self):
                self.my_client = MyAPIClient.from_config()

            async def do_something(self):
                return await self.my_client.get_something()

        # Usage
        service = MyService.from_config()
        result = await service.do_something()
        ```
    """

    def __init__(self) -> None:
        """Initialize BaseService.

        Loads workspace config (if available) and initializes API clients.
        API clients use the new config system that reads from:
        1. Environment variables (ANYT_API_KEY, ANYT_API_URL)
        2. Workspace config file (.anyt/anyt.json)
        """
        from cli.config import get_workspace_config_or_none

        self.workspace_config: "WorkspaceConfig | None" = get_workspace_config_or_none()
        self._init_clients()

    def _init_clients(self) -> None:
        """Initialize API clients.

        Override this method in subclasses to initialize the specific
        API clients needed by the service.

        Example:
            ```python
            def _init_clients(self):
                self.tasks = TasksAPIClient.from_config()
                self.workspaces = WorkspacesAPIClient.from_config()
            ```
        """
        pass

    @classmethod
    def from_config(cls) -> Self:
        """Create service from configuration.

        This is the preferred way to instantiate services in CLI commands
        and other code. The service will automatically load config from:
        1. Environment variables (ANYT_API_KEY, ANYT_API_URL)
        2. Workspace config file (.anyt/anyt.json) if available

        Returns:
            Configured service instance

        Example:
            ```python
            # Create service (auto-loads config from env/workspace)
            service = MyService.from_config()
            result = await service.do_something()
            ```
        """
        return cls()

    def _get_effective_workspace_id(self) -> int | None:
        """Get workspace ID from config/context.

        This helper method resolves the workspace context from:
        1. Workspace config file (.anyt/anyt.json)
        2. None if no workspace configured

        Returns:
            Workspace ID if available, None otherwise

        Note:
            This is a convenience method. Services may need to implement
            their own workspace resolution logic based on specific needs.
        """
        if self.workspace_config and self.workspace_config.workspace_id:
            return self.workspace_config.workspace_id

        return None
