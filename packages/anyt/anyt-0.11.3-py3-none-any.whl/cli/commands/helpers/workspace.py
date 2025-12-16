"""Workspace resolution and caching utilities."""

from datetime import datetime, timedelta
from typing import Optional

import typer

from cli.commands.console import console
from cli.config import WorkspaceConfig, get_effective_api_config
from cli.services.workspace_service import WorkspaceService

__all__ = [
    "clear_workspace_cache",
    "get_workspace_or_exit",
    "resolve_workspace_context",
]

# Workspace resolution cache
# Maps (workspace_identifier_or_id) -> (workspace_id, workspace_identifier, timestamp)
_workspace_cache: dict[str, tuple[int, str, datetime]] = {}
_CACHE_TTL = timedelta(minutes=5)


def clear_workspace_cache() -> None:
    """Clear the workspace resolution cache.

    Call this when switching workspaces or when you want to force
    a fresh lookup from the API.
    """
    global _workspace_cache
    _workspace_cache.clear()


def get_workspace_or_exit() -> WorkspaceConfig:
    """Load workspace config or exit with error.

    Returns:
        WorkspaceConfig

    Raises:
        typer.Exit: If workspace is not initialized or config cannot be loaded
    """
    # Check if workspace is initialized
    ws_config = WorkspaceConfig.load()
    if not ws_config:
        console.print("[red]Error:[/red] Not in a workspace directory")
        console.print("Run [cyan]anyt init[/cyan] first")
        raise typer.Exit(1)

    # Check authentication
    try:
        get_effective_api_config()
    except RuntimeError:
        console.print("[red]Error:[/red] Not authenticated")
        console.print("\nSet the ANYT_API_KEY environment variable:")
        console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
        raise typer.Exit(1)

    return ws_config


async def resolve_workspace_context(
    workspace_arg: Optional[str],
    workspace_service: WorkspaceService,
) -> tuple[int, str]:
    """Resolve workspace context from --workspace flag or local workspace.

    Uses a cache to avoid repeated API calls for workspace resolution.
    Cache expires after 5 minutes.

    Priority order:
    1. --workspace flag (if provided)
    2. Local .anyt/anyt.json workspace

    Args:
        workspace_arg: Workspace identifier or ID from --workspace flag
        workspace_service: WorkspaceService for fetching workspace details

    Returns:
        Tuple of (workspace_id, workspace_identifier)

    Raises:
        typer.Exit: If workspace cannot be resolved or is invalid
    """
    # Priority 1: Explicit --workspace flag
    if workspace_arg:
        # Check cache first
        cache_key = workspace_arg.upper()
        if cache_key in _workspace_cache:
            cached_id, cached_identifier, cached_time = _workspace_cache[cache_key]
            if datetime.now() - cached_time < _CACHE_TTL:
                return cached_id, cached_identifier

        # Fetch all workspaces to resolve identifier or ID
        workspaces = await workspace_service.list_workspaces()
        for ws in workspaces:
            if str(ws.id) == workspace_arg or ws.identifier == workspace_arg.upper():
                # Update cache
                _workspace_cache[cache_key] = (
                    ws.id,
                    ws.identifier,
                    datetime.now(),
                )
                return ws.id, ws.identifier

        console.print(f"[red]Error:[/red] Workspace '{workspace_arg}' not found")
        console.print("\nAvailable workspaces:")
        for ws in workspaces:
            console.print(f"  {ws.identifier} - {ws.name} (ID: {ws.id})")
        raise typer.Exit(1)

    # Priority 2: Local .anyt/anyt.json workspace
    ws_config = WorkspaceConfig.load()
    if ws_config:
        workspace_id = int(ws_config.workspace_id)
        workspace_identifier = ws_config.workspace_identifier or "UNKNOWN"
        return workspace_id, workspace_identifier

    # No workspace found
    console.print("[red]Error:[/red] No workspace context available")
    console.print("\nOptions:")
    console.print("  1. Initialize workspace: [cyan]anyt init[/cyan]")
    console.print("  2. Use --workspace flag: [cyan]--workspace DEV[/cyan]")
    raise typer.Exit(1)
