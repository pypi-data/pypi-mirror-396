"""
Helper functions for worker commands.
"""

import tempfile
from importlib import resources
from pathlib import Path
from typing import Optional

import typer

from cli.commands.console import stderr_console
from cli.config import get_effective_api_config
from worker.workflows import BUILT_IN_WORKFLOWS


def ensure_authenticated() -> str:
    """Check authentication and return API key.

    Uses get_effective_api_config() which checks:
    1. ANYT_API_KEY environment variable (highest priority)
    2. ~/.anyt/auth.json (global config - persistent storage)

    Returns:
        API key string on success

    Raises:
        typer.Exit(1): If not authenticated, with helpful message
    """
    api_config = get_effective_api_config()
    api_key = api_config.get("api_key")

    if not api_key:
        stderr_console.print("[red]Error:[/red] Not authenticated")
        stderr_console.print()
        stderr_console.print("Authenticate using one of these methods:")
        stderr_console.print("  1. Run [cyan]anyt login[/cyan] (persistent)")
        stderr_console.print(
            "  2. Set [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan] (session)"
        )
        raise typer.Exit(1)

    return api_key


def resolve_workflow_file(
    workflow_name: str,
    workspace: Path,
    custom_dir: Optional[Path] = None,
) -> Path:
    """
    Resolve workflow file with priority:
    1. Custom directory (if specified)
    2. Workspace .anyt/workflows/ (user override)
    3. Package built-in workflows

    Args:
        workflow_name: Name of the workflow (without .yaml extension)
        workspace: Workspace directory path
        custom_dir: Optional custom workflows directory

    Returns:
        Path to the workflow file

    Raises:
        ValueError: If workflow file is not found in any location
    """
    workflow_filename = f"{workflow_name}.yaml"

    # Priority 1: Custom directory (highest priority)
    if custom_dir:
        workflow_path = custom_dir / workflow_filename
        if workflow_path.exists():
            return workflow_path
        raise ValueError(f"Workflow file not found: {workflow_path}")

    # Priority 2: Workspace override (user can override built-ins)
    workspace_path = workspace / ".anyt" / "workflows" / workflow_filename
    if workspace_path.exists():
        return workspace_path

    # Priority 3: Package built-in workflows
    if workflow_name in BUILT_IN_WORKFLOWS:
        # Read from package resources and write to temp file
        # TaskCoordinator needs a file path to load the workflow
        try:
            workflow_content = (
                resources.files("worker.workflows")
                .joinpath(workflow_filename)
                .read_text(encoding="utf-8")
            )

            # Write to temp file for TaskCoordinator to load
            temp_dir = Path(tempfile.mkdtemp())
            temp_file = temp_dir / workflow_filename
            temp_file.write_text(workflow_content, encoding="utf-8")
            return temp_file
        except (FileNotFoundError, AttributeError) as e:
            raise ValueError(
                f"Built-in workflow '{workflow_name}' not found in package: {e}"
            ) from e

    # Not found anywhere
    available = ", ".join(BUILT_IN_WORKFLOWS)
    raise ValueError(
        f"Workflow '{workflow_name}' not found. "
        f"Available built-in workflows: {available}"
    )
