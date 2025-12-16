"""Start command for picking a task and creating a git branch."""

import json
import re
import subprocess
from datetime import UTC, datetime
from typing import Optional

import typer
from typing_extensions import Annotated

from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.services import ServiceRegistry as services
from cli.commands.sync.converters import _task_to_local_meta
from cli.config import ActiveTaskConfig
from cli.models.common import AssigneeType, CodingAgentType, Status
from cli.models.task import TaskUpdate
from cli.models.wrappers.task import Task

from .helpers import console, resolve_task_identifier


def _pull_task_to_local(task: Task) -> str:
    """Pull a task to local filesystem and return the local path."""
    local_service = services.get_local_task_service()
    local_service.ensure_tasks_dir()

    meta = _task_to_local_meta(task)
    description = task.description or ""
    local_service.write_task(meta, description)

    return f".anyt/tasks/{task.identifier}/"


def _slugify(text: str, max_length: int = 30) -> str:
    """Convert text to a URL-friendly slug for branch names.

    Args:
        text: Text to convert
        max_length: Maximum length of the slug

    Returns:
        Slugified text (lowercase, hyphenated, alphanumeric only)
    """
    # Convert to lowercase
    slug = text.lower()
    # Replace spaces and underscores with hyphens
    slug = re.sub(r"[\s_]+", "-", slug)
    # Remove non-alphanumeric characters except hyphens
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    # Remove consecutive hyphens
    slug = re.sub(r"-+", "-", slug)
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    # Truncate to max length, avoiding cutting mid-word
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit("-", 1)[0]
    return slug


def _is_git_repo() -> bool:
    """Check if current directory is a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def _get_current_branch() -> Optional[str]:
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except FileNotFoundError:
        return None


def _create_branch(branch_name: str, base_branch: str = "main") -> tuple[bool, str]:
    """Create and checkout a new git branch.

    Args:
        branch_name: Name of the branch to create
        base_branch: Base branch to create from (default: main)

    Returns:
        Tuple of (success, message)
    """
    try:
        # First, try to fetch from origin
        subprocess.run(
            ["git", "fetch", "origin"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Check if branch already exists locally
        result = subprocess.run(
            ["git", "rev-parse", "--verify", branch_name],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            # Branch exists, just checkout
            checkout_result = subprocess.run(
                ["git", "checkout", branch_name],
                capture_output=True,
                text=True,
                check=False,
            )
            if checkout_result.returncode == 0:
                return True, f"Switched to existing branch '{branch_name}'"
            return False, f"Failed to checkout branch: {checkout_result.stderr.strip()}"

        # Try to create from origin/base_branch first, fall back to local base_branch
        for base in [f"origin/{base_branch}", base_branch, "HEAD"]:
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name, base],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                return True, f"Created and switched to branch '{branch_name}'"

        return False, "Failed to create branch from any base"

    except FileNotFoundError:
        return False, "Git not found"


@async_command()
async def start_task(
    identifier: Annotated[
        str,
        typer.Argument(help="Task identifier (e.g., DEV-42, t_1Z for UID) or ID."),
    ],
    branch: Annotated[
        Optional[str],
        typer.Option(
            "--branch", "-b", help="Custom branch name (default: auto-generated)"
        ),
    ] = None,
    base: Annotated[
        str,
        typer.Option("--base", help="Base branch to create from"),
    ] = "main",
    no_branch: Annotated[
        bool,
        typer.Option("--no-branch", help="Skip git branch creation"),
    ] = False,
    no_pull: Annotated[
        bool,
        typer.Option("--no-pull", help="Skip pulling task to local filesystem"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Start working on a task: pick it, set status to active, and create a git branch.

    This command combines several operations:
    - Clears any previously picked task
    - Updates the task status to "active" in the API
    - Pulls the task to local filesystem (.anyt/tasks/{ID}/)
    - Creates a git branch named {IDENTIFIER}-{slug} (unless --no-branch)
    - Saves the task as the active task locally

    Examples:
        anyt task start DEV-42                    # Start task with auto-generated branch
        anyt task start DEV-42 -b feature/auth    # Start with custom branch name
        anyt task start DEV-42 --base develop     # Create branch from develop
        anyt task start DEV-42 --no-branch        # Skip branch creation
    """
    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        service = services.get_task_service()

        try:
            # Resolve identifier
            assert ctx.workspace_config is not None
            resolved_identifier = await resolve_task_identifier(
                identifier, service, ctx.workspace_config.workspace_identifier
            )

            # Fetch task details
            task = await service.get_task(resolved_identifier)

            # Clear any existing active task
            ActiveTaskConfig.clear()

            # Update task status to active
            task_update = TaskUpdate(
                status=Status.ACTIVE,
                assignee_type=AssigneeType.AGENT,
                assigned_coding_agent=CodingAgentType.CLAUDE_CODE,
            )
            task = await service.update_task(resolved_identifier, task_update)

            # Pull task to local filesystem
            local_path: Optional[str] = None
            if not no_pull:
                local_path = _pull_task_to_local(task)

            # Create git branch (unless --no-branch or not in a git repo)
            branch_name: Optional[str] = None
            branch_message: Optional[str] = None

            if not no_branch:
                if _is_git_repo():
                    # Generate branch name if not provided
                    if branch:
                        branch_name = branch
                    else:
                        slug = _slugify(task.title)
                        branch_name = (
                            f"{task.identifier}-{slug}" if slug else task.identifier
                        )

                    current_branch = _get_current_branch()
                    if current_branch == branch_name:
                        branch_message = f"Already on branch '{branch_name}'"
                    else:
                        assert branch_name is not None  # Set above
                        success, msg = _create_branch(branch_name, base)
                        branch_message = msg
                        if not success:
                            branch_name = None  # Indicate failure
                else:
                    branch_message = "Not a git repository, skipping branch creation"

            # Save as active task
            active_task = ActiveTaskConfig(
                identifier=task.identifier,
                title=task.title,
                picked_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                workspace_id=task.workspace_id,
                project_id=task.project_id,
                local_path=local_path,
            )
            active_task.save()

            if json_output:
                data = {
                    "identifier": task.identifier,
                    "title": task.title,
                    "workspace_id": task.workspace_id,
                    "project_id": task.project_id,
                    "picked_at": active_task.picked_at,
                    "status": task.status.value
                    if isinstance(task.status, Status)
                    else task.status,
                }
                if local_path:
                    data["local_path"] = local_path
                if branch_name:
                    data["branch"] = branch_name
                if branch_message:
                    data["branch_message"] = branch_message

                print(
                    json.dumps(
                        {
                            "success": True,
                            "data": data,
                            "message": f"Started working on {task.identifier}",
                        }
                    )
                )
            else:
                console.print(
                    f"[green]✓[/green] Started [cyan]{task.identifier}[/cyan] ({task.title})"
                )
                console.print("  Status set to active")
                if local_path:
                    console.print(f"  Local folder: {local_path}")
                if branch_message:
                    console.print(f"  Branch: {branch_message}")
                console.print("  Saved to .anyt/active_task.json")

        except typer.Exit:
            raise
        except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error
            error_msg = str(e)
            if json_output:
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": "Task not found"
                            if "404" in error_msg
                            else f"Failed to start task: {error_msg}",
                            "message": error_msg,
                        }
                    )
                )
            else:
                if "404" in error_msg:
                    console.print(f"[red]Error:[/red] Task '{identifier}' not found")
                else:
                    console.print(f"[red]Error:[/red] Failed to start task: {e}")
            raise typer.Exit(1)
