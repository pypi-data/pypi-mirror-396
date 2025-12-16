"""Service context helpers for resolving workspace, project, and user context.

These helpers provide utilities for commands and services to resolve
context information like current workspace, project, or user preferences.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Optional

import typer

from cli.commands.console import console
from cli.config import WorkspaceConfig

if TYPE_CHECKING:
    from cli.models.workspace import Workspace
    from cli.services.workspace_service import WorkspaceService


class ServiceContext:
    """Context manager for service operations.

    Provides helper methods to resolve workspace, project, and other
    contextual information needed by services and commands.

    Uses the new config system that loads from:
    1. Environment variables (ANYT_API_KEY, ANYT_API_URL)
    2. Workspace config file (.anyt/anyt.json) if available

    Example:
        ```python
        context = ServiceContext.from_config()
        workspace_id = context.get_workspace_id()
        project_id = context.get_project_id()
        ```
    """

    def __init__(self) -> None:
        """Initialize ServiceContext.

        Loads workspace config (if available) for context resolution.
        """
        from cli.config import get_workspace_config_or_none

        self.workspace_config: "WorkspaceConfig | None" = get_workspace_config_or_none()

    @classmethod
    def from_config(cls) -> "ServiceContext":
        """Create context from configuration.

        The context will automatically load config from:
        1. Environment variables (ANYT_API_KEY, ANYT_API_URL)
        2. Workspace config file (.anyt/anyt.json) if available

        Returns:
            ServiceContext instance
        """
        return cls()

    def get_workspace_id(self) -> int | None:
        """Get workspace ID from config/context.

        Resolution order:
        1. Workspace config file (.anyt/anyt.json)
        2. None if not configured

        Returns:
            Workspace ID if available, None otherwise
        """
        if self.workspace_config and self.workspace_config.workspace_id:
            return self.workspace_config.workspace_id

        return None

    def get_project_id(self) -> int | None:
        """Get project ID from config/context.

        Resolution order:
        1. .anyt/anyt.json workspace config for current_project_id
        2. None if not configured

        Returns:
            Project ID if available, None otherwise
        """
        if self.workspace_config and self.workspace_config.current_project_id:
            return self.workspace_config.current_project_id

        return None

    def get_api_url(self) -> str:
        """Get API URL for current environment.

        Returns:
            API base URL from workspace config or ANYT_API_URL env var

        Raises:
            RuntimeError: If API URL is not configured
        """
        from cli.config import get_effective_api_config

        api_config = get_effective_api_config()
        api_url = api_config.get("api_url")
        if not api_url:
            raise RuntimeError("No API URL configured")
        return api_url

    def is_authenticated(self) -> bool:
        """Check if user is authenticated.

        Returns:
            True if ANYT_API_KEY environment variable is set
        """
        import os

        return bool(os.getenv("ANYT_API_KEY"))


async def resolve_workspace(
    workspace_arg: Optional[str] = None,
    directory: Optional[Path] = None,
    workspace_service: Optional["WorkspaceService"] = None,
) -> tuple["Workspace", "WorkspaceConfig"]:
    """Resolve workspace from --workspace flag or local config.

    This utility provides consistent workspace resolution logic across commands,
    eliminating ~180 lines of duplicated code. It supports both explicit workspace
    specification via flag and automatic resolution from local config.

    Args:
        workspace_arg: Workspace ID or identifier from --workspace flag
        directory: Directory to search for config (default: current directory)
        workspace_service: Optional workspace service (lazy-created if needed)

    Returns:
        Tuple of (Workspace model, WorkspaceConfig)

    Raises:
        typer.Exit: If workspace cannot be resolved

    Example:
        ```python
        # With explicit workspace flag
        workspace, ws_config = await resolve_workspace(workspace="DEV")

        # From local config
        workspace, ws_config = await resolve_workspace()

        # workspace: Workspace model from API
        # ws_config: WorkspaceConfig for local persistence
        ```
    """
    from cli.config import WorkspaceConfig

    # Lazy-create workspace service if not provided
    if workspace_service is None:
        from cli.commands.services import ServiceRegistry as services

        workspace_service = services.get_workspace_service()

    target_dir = directory or Path.cwd()

    if workspace_arg:
        # Explicit --workspace flag: search by ID or identifier
        workspaces = await workspace_service.list_workspaces()

        for ws in workspaces:
            if str(ws.id) == workspace_arg or ws.identifier == workspace_arg.upper():
                # Create temporary config for consistency
                from cli.config import get_effective_api_config

                api_config = get_effective_api_config()
                api_url = api_config.get("api_url") or "https://api.anyt.dev"
                ws_config = WorkspaceConfig(
                    workspace_id=ws.id,
                    name=ws.name,
                    api_url=api_url,
                    workspace_identifier=ws.identifier,
                )
                return ws, ws_config

        # Workspace not found - show suggestions
        console.print(f"[red]Error:[/red] Workspace '{workspace_arg}' not found")
        console.print("\n[cyan]Available workspaces:[/cyan]")
        for ws in workspaces:
            console.print(f"  {ws.identifier} - {ws.name} (ID: {ws.id})")
        raise typer.Exit(1)

    # Use local workspace config
    loaded_config = WorkspaceConfig.load(target_dir)
    if not loaded_config:
        console.print("[red]Error:[/red] No workspace configured in this directory")
        console.print("\nOptions:")
        console.print("  1. Run [cyan]anyt init[/cyan] to set up workspace")
        console.print("  2. Use [cyan]--workspace <id-or-identifier>[/cyan] flag")
        raise typer.Exit(1)

    workspace = await workspace_service.get_workspace(loaded_config.workspace_id)
    return workspace, loaded_config
