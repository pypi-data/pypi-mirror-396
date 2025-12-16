"""Delete command for tasks (remove)."""

from typing import Any, Optional

import typer
from typing_extensions import Annotated

from cli.commands.context import CommandContext
from cli.utils.interactive import confirm
from cli.commands.decorators import async_command
from cli.commands.formatters import output_json
from cli.commands.guards import require_workspace_config
from cli.commands.services import ServiceRegistry as services
from cli.config import ActiveTaskConfig
from cli.models.wrappers.task import Task

from ..helpers import (
    console,
    get_active_task_id,
    resolve_task_identifier,
    truncate_text,
)


@async_command()
async def remove_task(
    identifiers: Annotated[
        Optional[list[str]],
        typer.Argument(
            help="Task identifier(s) (e.g., DEV-42, t_1Z for UID). Uses active task if not specified."
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation prompt"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Delete one or more tasks (soft delete)."""
    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        service = services.get_task_service()
        workspace_config = require_workspace_config(ctx.workspace_config)

        # Get workspace identifier for task ID normalization
        workspace_identifier = workspace_config.workspace_identifier

        # Determine task identifiers (raw, will be resolved in async function)
        task_identifiers = []
        clear_active = False

        if identifiers:
            # Store raw identifiers
            task_identifiers = identifiers
        else:
            # Use active task
            active_id = get_active_task_id()
            if not active_id:
                if json_output:
                    output_json(
                        {
                            "error": "ValidationError",
                            "message": "No task identifier provided and no active task set",
                            "suggestions": [
                                "Specify a task: anyt task rm DEV-42",
                                "Or pick a task first: anyt task pick DEV-42",
                            ],
                        },
                        success=False,
                    )
                else:
                    console.print(
                        "[red]Error:[/red] No task identifier provided and no active task set"
                    )
                    console.print("Specify a task: [cyan]anyt task rm DEV-42[/cyan]")
                    console.print(
                        "Or pick a task first: [cyan]anyt task pick DEV-42[/cyan]"
                    )
                raise typer.Exit(1)
            task_identifiers = [active_id]
            clear_active = True

        try:
            # Resolve all identifiers (converts UIDs to workspace identifiers)
            task_ids = []
            resolution_errors: list[dict[str, Any]] = []
            for raw_id in task_identifiers:
                try:
                    resolved = await resolve_task_identifier(
                        raw_id, service, workspace_identifier
                    )
                    task_ids.append(resolved)
                except Exception as e:  # noqa: BLE001 - Intentionally broad: gracefully handle task identifier resolution failures during bulk delete
                    error_msg = str(e)
                    resolution_errors.append(
                        {
                            "task_id": raw_id,
                            "error": "ResolutionError",
                            "message": f"Failed to resolve identifier: {error_msg}",
                        }
                    )

            # If all identifiers failed to resolve, exit early
            if len(task_ids) == 0 and len(resolution_errors) > 0:
                if json_output:
                    output_json({"deleted": [], "errors": resolution_errors})
                else:
                    for error in resolution_errors:
                        console.print(
                            f"[red]✗[/red] {error['task_id']}: {error['message']}"
                        )
                raise typer.Exit(1)

            # Fetch tasks for confirmation if not forced
            tasks_to_delete: list[Task] = []
            if not force and not json_output:
                for task_id in task_ids:
                    try:
                        task = await service.get_task(task_id)
                        tasks_to_delete.append(task)
                    except Exception:  # noqa: BLE001 - Intentionally broad: silently skip fetch errors, they'll be caught during actual deletion
                        pass  # Will handle errors during actual deletion

                # Confirm deletion
                if len(tasks_to_delete) == 1:
                    task = tasks_to_delete[0]
                    if not confirm(
                        f"Delete task {task.identifier} ({task.title})?", default=False
                    ):
                        raise typer.Exit(0)
                elif len(tasks_to_delete) > 1:
                    console.print(f"About to delete {len(tasks_to_delete)} tasks:")
                    for task in tasks_to_delete:
                        title = truncate_text(task.title, 40)
                        console.print(f"  - {task.identifier}: {title}")
                    console.print()
                    if not confirm(
                        f"Delete these {len(tasks_to_delete)} tasks?", default=False
                    ):
                        raise typer.Exit(0)

            deleted_tasks: list[dict[str, Any]] = []
            errors: list[dict[str, Any]] = []

            # Delete each task
            for task_id in task_ids:
                try:
                    await service.delete_task(task_id)
                    deleted_tasks.append({"identifier": task_id})
                except Exception as e:  # noqa: BLE001 - Intentionally broad: gracefully handle task deletion failures during bulk operation
                    error_msg = str(e)
                    if "404" in error_msg:
                        errors.append(
                            {
                                "task_id": task_id,
                                "error": "NotFound",
                                "message": f"Task '{task_id}' not found",
                            }
                        )
                    else:
                        errors.append(
                            {
                                "task_id": task_id,
                                "error": "DeleteError",
                                "message": str(e),
                            }
                        )

            # Output results
            if json_output:
                output_json({"deleted": deleted_tasks, "errors": errors})
            else:
                # Show success
                if len(deleted_tasks) == 1:
                    console.print(
                        f"[green]✓[/green] Deleted {deleted_tasks[0]['identifier']}"
                    )
                elif len(deleted_tasks) > 1:
                    console.print(
                        f"[green]✓[/green] Deleted {len(deleted_tasks)} tasks"
                    )

                # Clear active task if applicable
                if clear_active and len(deleted_tasks) > 0:
                    ActiveTaskConfig.clear()
                    console.print("[dim]Cleared active task[/dim]")

                # Show errors
                if errors:
                    console.print()
                    for error in errors:
                        console.print(
                            f"[red]✗[/red] {error['task_id']}: {error['message']}"
                        )

            # Exit with error if all failed
            if len(deleted_tasks) == 0 and len(errors) > 0:
                raise typer.Exit(1)

        except typer.Exit:
            raise
        except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error for any task deletion failure
            if json_output:
                output_json({"error": "DeleteError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to delete task(s): {e}")
            raise typer.Exit(1)
