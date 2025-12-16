"""Pick command for setting the active task."""

import json
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

from .crud.edit_helpers import get_task_or_error
from .helpers import console, resolve_task_identifier


def _pull_task_to_local(task: Task) -> str:
    """Pull a task to local filesystem and return the local path.

    Args:
        task: Task to pull

    Returns:
        Relative path to the local task folder (e.g., ".anyt/tasks/DEV-01/")
    """
    local_service = services.get_local_task_service()
    local_service.ensure_tasks_dir()

    # Convert task to local format
    meta = _task_to_local_meta(task)
    description = task.description or ""

    # Write task to local filesystem
    local_service.write_task(meta, description)

    # Return relative path
    return f".anyt/tasks/{task.identifier}/"


@async_command()
async def pick_task(
    identifier: Annotated[
        str,
        typer.Argument(help="Task identifier (e.g., DEV-42, t_1Z for UID) or ID."),
    ],
    no_pull: Annotated[
        bool,
        typer.Option("--no-pull", help="Skip pulling task to local filesystem"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Pick a task to work on (sets as active task and updates status to active).

    This command:
    - Clears any previously picked task
    - Updates the task status to "active" in the API
    - Pulls the task to local filesystem (.anyt/tasks/{ID}/)
    - Saves the task as the active task locally in .anyt/active_task.json
    """
    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        service = services.get_task_service()

        try:
            # Resolve identifier (converts UIDs to workspace identifiers)
            assert (
                ctx.workspace_config is not None
            )  # Guaranteed by require_workspace=True
            resolved_identifier = await resolve_task_identifier(
                identifier, service, ctx.workspace_config.workspace_identifier
            )

            # Fetch task details with standardized error handling
            task = await get_task_or_error(resolved_identifier, service, json_output)
            if task is None:
                raise typer.Exit(1)

            # Clear any existing active task
            ActiveTaskConfig.clear()

            # Update task status to active and set assignee to Claude Code agent
            task_update = TaskUpdate(
                status=Status.ACTIVE,
                assignee_type=AssigneeType.AGENT,
                assigned_coding_agent=CodingAgentType.CLAUDE_CODE,
            )
            task = await service.update_task(resolved_identifier, task_update)

            # Pull task to local filesystem (unless --no-pull)
            local_path: Optional[str] = None
            if not no_pull:
                local_path = _pull_task_to_local(task)

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
                print(
                    json.dumps(
                        {
                            "success": True,
                            "data": data,
                            "message": "Task picked and set to active",
                        }
                    )
                )
            else:
                console.print(
                    f"[green]✓[/green] Picked [cyan]{task.identifier}[/cyan] ({task.title})"
                )
                console.print("  Status set to active")
                if local_path:
                    console.print(f"  Local folder: {local_path}")
                console.print("  Saved to .anyt/active_task.json")

        except typer.Exit:
            raise
        except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error
            # Display user-friendly error for any task pick failure
            error_msg = str(e)
            if json_output:
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": f"Failed to pick task: {error_msg}",
                            "message": error_msg,
                        }
                    )
                )
            else:
                console.print(f"[red]Error:[/red] Failed to pick task: {e}")
            raise typer.Exit(1)
