"""Project service with business logic for project operations."""

from cli.client.exceptions import NotFoundError
from cli.client.projects import ProjectsAPIClient
from cli.models.project import Project, ProjectCreate
from cli.services.base import BaseService
from cli.utils.interactive import is_interactive, select_one, text_input
from InquirerPy.base.control import Choice


class ProjectService(BaseService):
    """Business logic for project operations.

    ProjectService encapsulates business rules and workflows for project
    management, including:
    - Listing projects in a workspace
    - Creating new projects
    - Getting or creating default project
    - Project validation and context resolution

    Example:
        ```python
        service = ProjectService.from_config()

        # List projects in workspace
        projects = await service.list_projects(workspace_id=123)

        # Get or create default project
        project = await service.get_or_create_default_project(workspace_id=123)

        # Create a new project
        project = await service.create_project(
            workspace_id=123,
            project=ProjectCreate(name="API")
        )
        ```
    """

    projects: ProjectsAPIClient

    def _init_clients(self) -> None:
        """Initialize API clients."""
        self.projects = ProjectsAPIClient.from_config()

    async def list_projects(self, workspace_id: int) -> list[Project]:
        """List all projects in a workspace.

        Args:
            workspace_id: The workspace ID

        Returns:
            List of Project objects

        Raises:
            NotFoundError: If workspace not found
            APIError: On other HTTP errors
        """
        return await self.projects.list_projects(workspace_id)

    async def create_project(
        self, workspace_id: int, project: ProjectCreate
    ) -> Project:
        """Create a new project in a workspace.

        Args:
            workspace_id: The workspace ID
            project: Project creation data

        Returns:
            Created Project object

        Raises:
            NotFoundError: If workspace not found
            ValidationError: If project data is invalid
            ConflictError: If identifier already exists
            APIError: On other HTTP errors
        """
        return await self.projects.create_project(workspace_id, project)

    async def get_current_project(self, workspace_id: int) -> Project:
        """Get the current/default project for a workspace.

        Args:
            workspace_id: The workspace ID

        Returns:
            Project object

        Raises:
            NotFoundError: If workspace not found
            APIError: On other HTTP errors
        """
        return await self.projects.get_current_project(workspace_id)

    async def get_or_create_default_project(
        self, workspace_id: int, workspace_name: str = "Default"
    ) -> Project:
        """Get current project or create a default one if none exists.

        Business logic:
        1. Try to get current project
        2. If not found, create a default project named after the workspace
        3. Return the project

        Args:
            workspace_id: The workspace ID
            workspace_name: Workspace name for default project naming

        Returns:
            Current or newly created Project object

        Raises:
            APIError: If creation fails
        """
        try:
            return await self.projects.get_current_project(workspace_id)
        except NotFoundError:
            # Create default project
            default_project = ProjectCreate(
                name=f"{workspace_name} Project",
                description="Default project",
            )
            return await self.projects.create_project(workspace_id, default_project)

    async def get_workspace_projects(self, workspace_id: int) -> list[Project]:
        """Fetch all projects in a workspace.

        This is a convenience alias for list_projects(), primarily used
        during workspace discovery and initialization flows.

        Args:
            workspace_id: The workspace ID

        Returns:
            List of Project objects in the workspace

        Raises:
            NotFoundError: If workspace not found
            APIError: On other HTTP errors
        """
        return await self.list_projects(workspace_id)

    def select_project_interactive(
        self,
        projects: list[Project],
        message: str = "Select a project:",
        allow_create: bool = True,
    ) -> Project | None:
        """Interactively select a project from a list.

        Behavior:
        - If only one project and allow_create=False: auto-selects it
        - If multiple projects: shows interactive selection prompt
        - If allow_create=True: adds '+ Create new project' option at end
        - If not in interactive mode (no TTY): returns None

        Args:
            projects: List of available projects
            message: Prompt message for selection
            allow_create: Whether to show 'Create new project' option

        Returns:
            Selected Project, None if:
            - not in interactive mode
            - user cancels with Ctrl+C
            - user selects 'Create new project' (caller should handle)

        Note:
            If the return value is None and allow_create was True, the caller
            should check if the user selected the create option by catching
            the special _CREATE_NEW sentinel value.
        """
        # Auto-select if only one project and no create option
        # (do this before interactive check so it works in non-TTY)
        if len(projects) == 1 and not allow_create:
            return projects[0]

        # Check if we're in an interactive environment
        if not is_interactive():
            return None

        # Build choices for InquirerPy select
        choices: list[Choice] = []
        for proj in projects:
            display_name = f"{proj.name}"
            if proj.description:
                display_name += f" - {proj.description}"
            choices.append(Choice(value=proj.id, name=display_name))

        # Add create option at the end if allowed
        if allow_create:
            choices.append(Choice(value="_CREATE_NEW", name="+ Create new project"))

        try:
            selected_value = select_one(
                choices=choices,
                message=message,
                default=projects[0].id if projects else "_CREATE_NEW",
            )
        except KeyboardInterrupt:
            return None

        # Check if user selected create option
        if selected_value == "_CREATE_NEW":
            return None  # Caller should handle creation

        # Find and return the selected project
        for proj in projects:
            if proj.id == selected_value:
                return proj

        # Should not reach here, but return None if no match
        return None

    def create_project_interactive(
        self,
        workspace_id: int,
    ) -> ProjectCreate | None:
        """Interactively prompt for project details.

        Prompts for:
        - Project name (required)
        - Description (optional)

        Args:
            workspace_id: The workspace ID (for context, not used directly)

        Returns:
            ProjectCreate with user-provided details, or None if:
            - not in interactive mode
            - user cancels with Ctrl+C
            - user provides empty name
        """
        # Check if we're in an interactive environment
        if not is_interactive():
            return None

        try:
            # Prompt for name (required)
            name = text_input(
                message="Project name:",
                validate=lambda x: len(x.strip()) > 0,
            )

            if not name or not name.strip():
                return None

            # Prompt for description (optional)
            description = text_input(
                message="Description (optional):",
                default="",
            )

            return ProjectCreate(
                name=name.strip(),
                description=description.strip() if description else None,
            )
        except KeyboardInterrupt:
            return None
