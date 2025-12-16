"""Shared utility functions for CLI commands."""

from typing import TYPE_CHECKING, TypeVar, Callable, Optional
from pathlib import Path
import typer

from cli.commands.console import console
from cli.config import WorkspaceConfig
from cli.utils.interactive import confirm

if TYPE_CHECKING:
    from cli.client.projects import ProjectsAPIClient

T = TypeVar("T")


def confirm_deletion(
    items: list[T],
    item_formatter: Callable[[T], str],
    force: bool = False,
    json_output: bool = False,
) -> None:
    """Prompt user to confirm deletion of items.

    Args:
        items: Items to delete
        item_formatter: Function to format item for display
        force: Skip confirmation if True
        json_output: Skip confirmation if True

    Raises:
        typer.Exit: If user cancels

    Example:
        confirm_deletion(
            items=labels,
            item_formatter=lambda l: l.name,
            force=force_flag,
        )
    """
    if force or json_output:
        return

    count = len(items)
    plural = "s" if count != 1 else ""
    console.print(f"[yellow]About to delete {count} item{plural}:[/yellow]")

    for item in items[:10]:  # Show max 10 items
        console.print(f"  - {item_formatter(item)}")

    if count > 10:
        console.print(f"  ... and {count - 10} more")

    if not confirm("Are you sure?"):
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit(0)


async def get_project_id(
    project_arg: Optional[int],
    ws_config: WorkspaceConfig,
    projects_client: Optional["ProjectsAPIClient"] = None,
) -> int:
    """Get project ID from argument, config, or API.

    Priority order:
    1. --project argument (explicit)
    2. workspace_config.current_project_id (configured default)
    3. API default project (fetched from backend)

    Args:
        project_arg: Project ID from --project flag
        ws_config: Workspace configuration
        projects_client: Optional projects client (lazy-created if needed)

    Returns:
        Project ID

    Raises:
        typer.Exit: If project cannot be determined

    Example:
        project_id = await get_project_id(
            project_arg=args.project,
            ws_config=workspace_config,
        )
    """
    # Explicit --project flag
    if project_arg:
        return project_arg

    # Configured default project
    if ws_config.current_project_id:
        console.print(
            f"[dim]Using configured project ID: {ws_config.current_project_id}[/dim]"
        )
        return ws_config.current_project_id

    # Fetch default from API
    if projects_client is None:
        from cli.commands.services import ServiceRegistry as services

        projects_client = services.get_projects_client()

    try:
        project = await projects_client.get_current_project(int(ws_config.workspace_id))
        console.print(f"[dim]Using project: {project.name} (ID: {project.id})[/dim]")
        return project.id
    except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error
        # Display user-friendly error for any project resolution failure
        console.print(f"[red]Error:[/red] Failed to determine project: {e}")
        console.print("\n[cyan]Options:[/cyan]")
        console.print("  1. Specify [cyan]--project <ID>[/cyan]")
        console.print("  2. Set current_project_id in .anyt/anyt.json")
        console.print("  3. Run [cyan]anyt project use <project-id>[/cyan]")
        raise typer.Exit(1)


def get_workspace_or_exit(directory: Optional[Path] = None) -> WorkspaceConfig:
    """Get workspace config or exit with error.

    Args:
        directory: Directory to search for config (default: current directory)

    Returns:
        WorkspaceConfig

    Raises:
        typer.Exit: If workspace config not found

    Example:
        ws_config = get_workspace_or_exit()
    """
    target_dir = directory or Path.cwd()
    ws_config = WorkspaceConfig.load(target_dir)

    if not ws_config:
        console.print("[red]Error:[/red] Not in a workspace directory")
        console.print("Run [cyan]anyt init[/cyan] first")
        raise typer.Exit(1)

    return ws_config
