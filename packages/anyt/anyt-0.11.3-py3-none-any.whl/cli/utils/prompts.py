"""Interactive prompt utilities for CLI commands."""

from typing import TYPE_CHECKING

import typer
from rich.prompt import Prompt
from InquirerPy.base.control import Choice

from cli.commands.console import console
from cli.models.workspace import Workspace
from cli.models.project import Project
from cli.utils.interactive import select_one, confirm, is_interactive

if TYPE_CHECKING:
    from cli.client.projects import ProjectsAPIClient


def select_workspace(
    workspaces: list[Workspace],
    preselected_id: int | None = None,
    non_interactive: bool = False,
) -> Workspace:
    """Interactive workspace selection.

    Args:
        workspaces: List of available workspaces
        preselected_id: Optional workspace ID to pre-select
        non_interactive: If True, auto-select first workspace

    Returns:
        Selected workspace

    Raises:
        typer.Exit: If user cancels or no workspaces available
        ValueError: If preselected_id not found
    """
    if not workspaces:
        console.print("[red]Error:[/red] No accessible workspaces found")
        raise typer.Exit(1)

    # Handle preselection
    if preselected_id:
        for ws in workspaces:
            if ws.id == preselected_id:
                console.print(
                    f"[green]✓[/green] Using workspace: {ws.name} ({ws.identifier})"
                )
                return ws
        raise ValueError(f"Workspace {preselected_id} not found")

    # Handle non-interactive mode or non-TTY
    if non_interactive or not is_interactive():
        workspace = workspaces[0]
        console.print(
            f"[green]✓[/green] Using workspace: {workspace.name} ({workspace.identifier})"
        )
        return workspace

    # Handle single workspace case
    if len(workspaces) == 1:
        workspace = workspaces[0]
        console.print(
            f"\nFound 1 workspace: [cyan]{workspace.name}[/cyan] ([yellow]{workspace.identifier}[/yellow])"
        )
        try:
            if not confirm(f"Use workspace '{workspace.name}'?", default=True):
                console.print("[yellow]Initialization cancelled[/yellow]")
                raise typer.Exit(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Initialization cancelled[/yellow]")
            raise typer.Exit(1)
        return workspace

    # Interactive selection for multiple workspaces with InquirerPy
    console.print()
    console.print("[bold cyan]Step 2: Workspace Selection[/bold cyan]")
    console.print()

    # Build choices for select prompt
    choices: list[Choice] = [
        Choice(
            value=ws.id,
            name=f"{ws.name} ({ws.identifier}) - ID: {ws.id}",
        )
        for ws in workspaces
    ]

    try:
        selected_id = select_one(
            choices=choices,
            message="Which workspace would you like to use?",
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Initialization cancelled[/yellow]")
        raise typer.Exit(1)

    # Find selected workspace
    selected = next(ws for ws in workspaces if ws.id == selected_id)

    console.print(f"[green]✓[/green] Selected: {selected.name} ({selected.identifier})")
    return selected


async def select_project(
    projects: list[Project],
    preselected_id: int | None = None,
    non_interactive: bool = False,
    workspace_id: int | None = None,
    workspace_identifier: str | None = None,
    proj_client: "ProjectsAPIClient | None" = None,
) -> Project | None:
    """Interactive project selection with optional creation.

    Args:
        projects: List of available projects
        preselected_id: Optional project ID to pre-select
        non_interactive: If True, auto-select first project
        workspace_id: Workspace ID (required for creating new projects)
        workspace_identifier: Workspace identifier for default project name
        proj_client: ProjectsAPIClient instance (required for creating new projects)

    Returns:
        Selected project, or None if no projects available

    Raises:
        typer.Exit: If user cancels
        ValueError: If preselected_id not found
    """
    # Handle no projects - return None to signal that default should be created
    if not projects:
        return None

    # Handle preselection
    if preselected_id:
        for proj in projects:
            if proj.id == preselected_id:
                console.print(f"[green]✓[/green] Using project: {proj.name}")
                return proj
        raise ValueError(f"Project {preselected_id} not found")

    # Handle non-interactive mode or non-TTY
    if non_interactive or not is_interactive():
        project = projects[0]
        console.print(f"[green]✓[/green] Using project: {project.name}")
        return project

    # Handle single project case
    if len(projects) == 1:
        project = projects[0]
        console.print(f"\nFound 1 project: [cyan]{project.name}[/cyan]")
        if project.description:
            console.print(f"  [dim]{project.description}[/dim]")
        try:
            if not confirm(f"Use project '{project.name}'?", default=True):
                console.print("[yellow]Initialization cancelled[/yellow]")
                raise typer.Exit(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Initialization cancelled[/yellow]")
            raise typer.Exit(1)
        return project

    # Interactive selection for multiple projects with InquirerPy
    console.print()
    console.print("[bold cyan]Step 3: Project Selection[/bold cyan]")
    console.print()

    # Build choices for select prompt
    # Use a special marker for "Create new project"
    CREATE_NEW_MARKER = -1
    proj_choices: list[Choice] = []

    for proj in projects:
        desc = proj.description or ""
        if len(desc) > 40:
            desc = desc[:37] + "..."
        name = f"{proj.name}" + (f" - {desc}" if desc else "")
        proj_choices.append(Choice(value=proj.id, name=name))

    # Add "Create new project" option if we can create projects
    can_create = workspace_id is not None and proj_client is not None
    if can_create:
        proj_choices.append(
            Choice(value=CREATE_NEW_MARKER, name="+ Create new project")
        )

    try:
        selected_id = select_one(
            choices=proj_choices,
            message="Which project would you like to use?",
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Initialization cancelled[/yellow]")
        raise typer.Exit(1)

    # Handle "Create new project" selection
    if selected_id == CREATE_NEW_MARKER:
        # Validate required parameters for creation
        if workspace_id is None or proj_client is None:
            console.print(
                "[red]Error:[/red] Cannot create project without workspace context"
            )
            raise typer.Exit(1)

        console.print()
        console.print("[bold cyan]Creating New Project[/bold cyan]")
        console.print()

        # Import here to avoid circular imports
        from cli.models.project import ProjectCreate
        from cli.models.common import ProjectStatus

        # Prompt for project details using Rich prompts for text input
        default_name = (
            f"{workspace_identifier} Project" if workspace_identifier else "New Project"
        )
        project_name = Prompt.ask("Project name", default=default_name)

        description_input = Prompt.ask("Description (optional)", default="")
        description = description_input if description_input else None

        # Status selection with InquirerPy
        status_choices: list[Choice] = [
            Choice(value=status.value, name=status.value) for status in ProjectStatus
        ]
        try:
            status_value: str = select_one(
                choices=status_choices,
                message="Status:",
                default=ProjectStatus.ACTIVE.value,
            )
            status = ProjectStatus(status_value)
        except KeyboardInterrupt:
            console.print("\n[yellow]Project creation cancelled[/yellow]")
            raise typer.Exit(1)

        # Create the project
        try:
            project_create = ProjectCreate(
                name=project_name,
                description=description,
                status=status,
            )
            # workspace_id and proj_client guaranteed to be non-None here
            new_project = await proj_client.create_project(workspace_id, project_create)
            console.print()
            console.print(f"[green]✓[/green] Created project: {new_project.name}")
            return new_project

        except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error
            # Display user-friendly error for any project creation failure
            console.print()
            console.print(f"[red]Error:[/red] Failed to create project: {e}")
            raise typer.Exit(1)

    # Handle existing project selection
    selected = next(proj for proj in projects if proj.id == selected_id)
    console.print(f"[green]✓[/green] Selected: {selected.name}")
    return selected
