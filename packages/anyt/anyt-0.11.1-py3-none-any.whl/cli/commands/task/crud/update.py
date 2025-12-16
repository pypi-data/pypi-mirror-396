"""Update commands for tasks (edit, mark done, add note)."""

from datetime import datetime
from typing import Any, Optional

import typer
from rich.prompt import Prompt
from typing_extensions import Annotated

from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.formatters import output_json
from cli.commands.guards import require_workspace_config
from cli.commands.services import ServiceRegistry as services
from cli.config import ActiveTaskConfig
from cli.models.common import Priority, Status
from cli.models.task import TaskUpdate
from cli.models.wrappers.task import Task

from cli.commands.validators import validate_priority, validate_status

from ..helpers import (
    console,
    get_active_task_id,
    normalize_identifier,
    resolve_plan_content,
)
from .edit_helpers import (
    display_no_task_error,
    format_error_result,
    get_task_or_error,
    resolve_task_identifiers,
)


@async_command()
async def edit_task(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-42, t_1Z for UID) or ID. Uses active task if not specified."
        ),
    ] = None,
    title: Annotated[
        Optional[str],
        typer.Option("--title", help="New title"),
    ] = None,
    description: Annotated[
        Optional[str],
        typer.Option("-d", "--description", help="New description"),
    ] = None,
    status: Annotated[
        Optional[str],
        typer.Option(
            "--status",
            help="New status (backlog, todo, active, blocked, done, canceled, archived)",
        ),
    ] = None,
    priority: Annotated[
        Optional[int],
        typer.Option(
            "-p",
            "--priority",
            help="New priority: -2 (lowest), -1 (low), 0 (normal), 1 (high), 2 (highest)",
        ),
    ] = None,
    owner: Annotated[
        Optional[str],
        typer.Option("--owner", help="New owner ID"),
    ] = None,
    plan: Annotated[
        Optional[str],
        typer.Option(
            "--plan",
            help="Implementation plan content. Use '-' to read from stdin.",
        ),
    ] = None,
    plan_file: Annotated[
        Optional[str],
        typer.Option(
            "--plan-file",
            help="Read implementation plan from file.",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Edit a task's fields."""
    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        service = services.get_task_service()

        # Get workspace identifier for task ID normalization
        workspace_config = require_workspace_config(ctx.workspace_config)
        workspace_identifier = workspace_config.workspace_identifier

        # Determine task identifier to edit
        task_id = identifier
        if not task_id:
            task_id = get_active_task_id()
            if not task_id:
                display_no_task_error(
                    json_output,
                    "anyt task edit DEV-42 --status done",
                    "anyt task pick DEV-42",
                )
                raise typer.Exit(1)

        # Validate priority if provided
        if not validate_priority(priority, json_output):
            raise typer.Exit(1)

        # Validate status if provided
        is_valid, status_enum = validate_status(status, json_output)
        if not is_valid:
            raise typer.Exit(1)

        try:
            # Convert priority to enum if provided (already validated)
            priority_enum = None
            if priority is not None:
                priority_enum = Priority(priority)

            # Handle plan content - validate options and read content
            plan_content = resolve_plan_content(plan, plan_file, json_output)

            # Resolve identifier (converts UIDs to workspace identifiers)
            resolved_ids, errors = await resolve_task_identifiers(
                [task_id], service, workspace_identifier, json_output
            )

            if not resolved_ids:
                if json_output:
                    output_json(
                        {"error": "NotFound", "message": f"Task '{task_id}' not found"},
                        success=False,
                    )
                else:
                    console.print(f"[red]Error:[/red] Task '{task_id}' not found")
                raise typer.Exit(1)

            resolved_id = resolved_ids[0]

            # Create update model
            task_update = TaskUpdate(
                title=title,
                description=description,
                status=status_enum,
                priority=priority_enum,
                owner_id=owner,
                implementation_plan=plan_content,
            )

            # Update the task
            updated_task = await service.update_task(resolved_id, task_update)

            # Output results
            if json_output:
                output_json(updated_task.model_dump(mode="json"))
            else:
                console.print(f"[green]✓[/green] Updated {updated_task.identifier}")

        except typer.Exit:
            raise
        except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error for any task edit failure
            if json_output:
                output_json({"error": "UpdateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to update task: {e}")
            raise typer.Exit(1)


@async_command()
async def mark_done(
    identifiers: Annotated[
        Optional[list[str]],
        typer.Argument(
            help="Task identifier(s) (e.g., DEV-42 DEV-43). Uses active task if not specified."
        ),
    ] = None,
    note: Annotated[
        Optional[str],
        typer.Option("--note", "-n", help="Add a completion note to the task"),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Mark one or more tasks as done.

    Optionally add a completion note to the task's Events section.
    """
    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        service = services.get_task_service()

        # Get workspace identifier for task ID normalization
        workspace_config = require_workspace_config(ctx.workspace_config)
        workspace_identifier = workspace_config.workspace_identifier

        # Determine task IDs
        task_ids = []
        clear_active = False

        if identifiers:
            task_ids = [
                normalize_identifier(tid, workspace_identifier) for tid in identifiers
            ]
        else:
            active_id = get_active_task_id()
            if not active_id:
                display_no_task_error(
                    json_output,
                    "anyt task done DEV-42",
                    "anyt task pick DEV-42",
                )
                raise typer.Exit(1)
            task_ids = [normalize_identifier(active_id, workspace_identifier)]
            clear_active = True

        try:
            updated_tasks: list[Task] = []
            errors: list[dict[str, Any]] = []

            # Mark each task as done
            for task_id in task_ids:
                try:
                    # If note is provided, fetch task to append note to description
                    description_update = None
                    if note:
                        task_data = await service.get_task(task_id)
                        current_description = task_data.description or ""
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                        note_text = f"\n### {timestamp} - Completed\n- {note}\n"

                        if "## Events" in current_description:
                            description_update = current_description + note_text
                        else:
                            description_update = (
                                current_description + f"\n## Events\n{note_text}"
                            )

                    # Update task status and description using typed model
                    if description_update:
                        task_update = TaskUpdate(
                            status=Status.DONE,
                            description=description_update,
                        )
                        task = await service.update_task(task_id, task_update)
                    else:
                        task_update = TaskUpdate(status=Status.DONE)
                        task = await service.update_task(task_id, task_update)

                    updated_tasks.append(task)
                except Exception as e:  # noqa: BLE001 - Intentionally broad: gracefully handle task completion failures during bulk operation
                    error_msg = str(e)
                    if "404" in error_msg:
                        errors.append(
                            format_error_result(
                                task_id, "NotFound", f"Task '{task_id}' not found"
                            )
                        )
                    else:
                        errors.append(
                            format_error_result(task_id, "UpdateError", str(e))
                        )

            # Output results
            if json_output:
                output_json(
                    {
                        "updated": [t.model_dump(mode="json") for t in updated_tasks],
                        "errors": errors,
                    }
                )
            else:
                # Show success
                if len(updated_tasks) == 1:
                    console.print(
                        f"[green]✓[/green] Marked {updated_tasks[0].identifier} as done"
                    )
                elif len(updated_tasks) > 1:
                    console.print(
                        f"[green]✓[/green] Marked {len(updated_tasks)} tasks as done"
                    )

                # Clear active task if applicable
                if clear_active and len(updated_tasks) > 0:
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
            if len(updated_tasks) == 0 and len(errors) > 0:
                raise typer.Exit(1)

        except typer.Exit:
            raise
        except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error for any task done operation failure
            if json_output:
                output_json({"error": "UpdateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to mark task(s) as done: {e}")
            raise typer.Exit(1)


@async_command()
async def add_note_to_task(
    identifier: Annotated[
        Optional[str],
        typer.Argument(help="Task identifier (e.g., DEV-42) or use active task"),
    ] = None,
    message: Annotated[
        str,
        typer.Option("--message", "-m", help="Note message to append"),
    ] = "",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Add a timestamped note/event to a task's description.

    DEPRECATED: Use 'anyt comment add' instead for better structure and timestamps.

    The note will be appended to the Events section of the task description
    with a timestamp.
    """
    # Show deprecation warning
    if not json_output:
        console.print(
            "[yellow]Warning:[/yellow] 'anyt task note' is deprecated. "
            "Use [cyan]anyt comment add[/cyan] instead."
        )
        console.print("[dim]This command will be removed in a future release.[/dim]\n")

    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        workspace_config = require_workspace_config(ctx.workspace_config)
        task_service = services.get_task_service()

        try:
            # Get task identifier
            task_id = identifier
            if not task_id:
                task_id = get_active_task_id()
                if not task_id:
                    if json_output:
                        output_json(
                            {
                                "error": "NoActiveTask",
                                "message": "No active task set",
                                "hint": "Specify task identifier or run 'anyt task pick'",
                            },
                            success=False,
                        )
                    else:
                        console.print("[red]Error:[/red] No active task set")
                        console.print(
                            "Specify task identifier or run [cyan]anyt task pick[/cyan]"
                        )
                    raise typer.Exit(1)

            # Normalize identifier
            task_id = normalize_identifier(
                task_id, workspace_config.workspace_identifier
            )

            # Get current task to retrieve description with standardized error handling
            task = await get_task_or_error(task_id, task_service, json_output)
            if task is None:
                raise typer.Exit(1)
            current_description = task.description or ""

            # Get message from parameter or prompt
            note_message = message
            if not note_message:
                if json_output:
                    console.print("[red]Error:[/red] Message is required")
                    raise typer.Exit(1)
                note_message = Prompt.ask("[cyan]Note message[/cyan]")
                if not note_message:
                    console.print("[yellow]Cancelled[/yellow]")
                    raise typer.Exit(0)

            # Create timestamped note
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            note = f"\n### {timestamp} - Note\n- {note_message}\n"

            # Append note to description
            # If description has an Events section, append there
            # Otherwise, create Events section and append
            if "## Events" in current_description:
                new_description = current_description + note
            else:
                new_description = current_description + f"\n## Events\n{note}"

            # Update task with new description
            updates = TaskUpdate(description=new_description)
            updated_task = await task_service.update_task(
                identifier=task_id,
                updates=updates,
            )

            # Display success
            if json_output:
                output_json(updated_task.model_dump(mode="json"))
            else:
                console.print(
                    f"[green]✓[/green] Note added to [cyan]{updated_task.identifier}[/cyan]"
                )
                console.print(f"  {note_message}")

        except typer.Exit:
            raise
        except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error for any note addition failure
            if json_output:
                output_json({"error": "UpdateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to add note: {e}")
            raise typer.Exit(1)
