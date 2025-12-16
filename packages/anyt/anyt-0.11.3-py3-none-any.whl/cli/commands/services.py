"""Service registry for centralized service management."""

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from cli.client.comments import CommentsAPIClient
    from cli.client.projects import ProjectsAPIClient
    from cli.client.pull_requests import PullRequestsAPIClient
    from cli.client.tasks import TasksAPIClient
    from cli.client.workspaces import WorkspacesAPIClient
    from cli.services.context import ServiceContext
    from cli.services.local_task_service import LocalTaskService
    from cli.services.project_service import ProjectService
    from cli.services.task_service import TaskService
    from cli.services.user_service import UserService
    from cli.services.workspace_service import WorkspaceService


class ServiceRegistry:
    """Centralized service registry with lazy initialization and caching.

    Provides a singleton-like pattern for service instances, ensuring they are
    created only when needed and reused across commands. This improves performance
    and reduces boilerplate code.

    Example:
        from cli.commands.services import ServiceRegistry as services

        # Get service (lazy-created and cached)
        task_service = services.get_task_service()

        # Clear cache (useful for testing)
        services.clear()
    """

    _instances: dict[type, Any] = {}

    @classmethod
    def get_task_service(cls) -> "TaskService":
        """Get or create TaskService instance.

        Returns:
            Cached TaskService instance
        """
        from cli.services.task_service import TaskService

        if TaskService not in cls._instances:
            cls._instances[TaskService] = TaskService.from_config()
        return cast("TaskService", cls._instances[TaskService])

    @classmethod
    def get_workspace_service(cls) -> "WorkspaceService":
        """Get or create WorkspaceService instance.

        Returns:
            Cached WorkspaceService instance
        """
        from cli.services.workspace_service import WorkspaceService

        if WorkspaceService not in cls._instances:
            cls._instances[WorkspaceService] = WorkspaceService.from_config()
        return cast("WorkspaceService", cls._instances[WorkspaceService])

    @classmethod
    def get_project_service(cls) -> "ProjectService":
        """Get or create ProjectService instance.

        Returns:
            Cached ProjectService instance
        """
        from cli.services.project_service import ProjectService

        if ProjectService not in cls._instances:
            cls._instances[ProjectService] = ProjectService.from_config()
        return cast("ProjectService", cls._instances[ProjectService])

    @classmethod
    def get_user_service(cls) -> "UserService":
        """Get or create UserService instance.

        Returns:
            Cached UserService instance
        """
        from cli.services.user_service import UserService

        if UserService not in cls._instances:
            cls._instances[UserService] = UserService.from_config()
        return cast("UserService", cls._instances[UserService])

    @classmethod
    def get_workspaces_client(cls) -> "WorkspacesAPIClient":
        """Get or create WorkspacesAPIClient instance.

        Returns:
            Cached WorkspacesAPIClient instance
        """
        from cli.client.workspaces import WorkspacesAPIClient

        if WorkspacesAPIClient not in cls._instances:
            cls._instances[WorkspacesAPIClient] = WorkspacesAPIClient.from_config()
        return cast("WorkspacesAPIClient", cls._instances[WorkspacesAPIClient])

    @classmethod
    def get_tasks_client(cls) -> "TasksAPIClient":
        """Get or create TasksAPIClient instance.

        Returns:
            Cached TasksAPIClient instance
        """
        from cli.client.tasks import TasksAPIClient

        if TasksAPIClient not in cls._instances:
            cls._instances[TasksAPIClient] = TasksAPIClient.from_config()
        return cast("TasksAPIClient", cls._instances[TasksAPIClient])

    @classmethod
    def get_projects_client(cls) -> "ProjectsAPIClient":
        """Get or create ProjectsAPIClient instance.

        Returns:
            Cached ProjectsAPIClient instance
        """
        from cli.client.projects import ProjectsAPIClient

        if ProjectsAPIClient not in cls._instances:
            cls._instances[ProjectsAPIClient] = ProjectsAPIClient.from_config()
        return cast("ProjectsAPIClient", cls._instances[ProjectsAPIClient])

    @classmethod
    def get_comments_client(cls) -> "CommentsAPIClient":
        """Get or create CommentsAPIClient instance.

        Returns:
            Cached CommentsAPIClient instance
        """
        from cli.client.comments import CommentsAPIClient

        if CommentsAPIClient not in cls._instances:
            cls._instances[CommentsAPIClient] = CommentsAPIClient.from_config()
        return cast("CommentsAPIClient", cls._instances[CommentsAPIClient])

    @classmethod
    def get_pull_requests_client(cls) -> "PullRequestsAPIClient":
        """Get or create PullRequestsAPIClient instance.

        Returns:
            Cached PullRequestsAPIClient instance
        """
        from cli.client.pull_requests import PullRequestsAPIClient

        if PullRequestsAPIClient not in cls._instances:
            cls._instances[PullRequestsAPIClient] = PullRequestsAPIClient.from_config()
        return cast("PullRequestsAPIClient", cls._instances[PullRequestsAPIClient])

    @classmethod
    def get_service_context(cls) -> "ServiceContext":
        """Get or create ServiceContext instance.

        Returns:
            Cached ServiceContext instance
        """
        from cli.services.context import ServiceContext

        if ServiceContext not in cls._instances:
            cls._instances[ServiceContext] = ServiceContext.from_config()
        return cast("ServiceContext", cls._instances[ServiceContext])

    @classmethod
    def get_local_task_service(cls) -> "LocalTaskService":
        """Get or create LocalTaskService instance.

        Returns:
            Cached LocalTaskService instance
        """
        from cli.services.local_task_service import LocalTaskService

        if LocalTaskService not in cls._instances:
            cls._instances[LocalTaskService] = LocalTaskService()
        return cast("LocalTaskService", cls._instances[LocalTaskService])

    @classmethod
    def clear(cls) -> None:
        """Clear all cached service instances.

        Useful for testing to ensure fresh service instances between tests.
        Should be called in test teardown or setup.
        """
        cls._instances.clear()
