"""List command for tasks."""

from typing import Optional

import typer
from rich.table import Table
from typing_extensions import Annotated

from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.formatters import output_json
from cli.commands.services import ServiceRegistry as services
from cli.models.common import Priority, Status
from cli.models.task import TaskFilters

from .helpers import (
    console,
    format_priority,
    format_relative_time,
    truncate_text,
)


@async_command()
async def list_tasks(
    status: Annotated[
        Optional[str],
        typer.Option(
            "--status",
            help="Filter by status (backlog, todo, active, blocked, done, canceled, archived). Comma-separated.",
        ),
    ] = None,
    phase: Annotated[
        Optional[str],
        typer.Option("--phase", help="Filter by phase/milestone"),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", help="Max number of tasks to show"),
    ] = 50,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """List tasks with filtering."""
    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        service = services.get_task_service()

        try:
            # Parse filters
            status_list = None
            if status:
                # Convert status strings to Status enums
                status_list = [Status(s.strip()) for s in status.split(",")]

            # Use current_project_id from workspace config
            assert (
                ctx.workspace_config is not None
            )  # Guaranteed by require_workspace=True

            project_id = ctx.workspace_config.current_project_id

            # Create typed filters
            filters = TaskFilters(
                workspace_id=int(ctx.workspace_config.workspace_id),
                project_id=project_id,
                status=status_list,
                phase=phase,
                limit=limit,
            )

            # Fetch tasks using service
            tasks = await service.list_tasks(filters)

            # JSON output mode
            if json_output:
                output_json(
                    {
                        "items": [task.model_dump(mode="json") for task in tasks],
                        "count": len(tasks),
                    }
                )
                return

            # Rich console output mode
            if not tasks:
                console.print("[yellow]No tasks found[/yellow]")
                return

            # Display tasks in table
            table = Table(show_header=True, header_style="bold")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white")
            table.add_column("Status", style="yellow", no_wrap=True)
            table.add_column("Priority", style="magenta", no_wrap=True)
            table.add_column("Updated", style="dim", no_wrap=True)

            for task in tasks:
                title = truncate_text(task.title)
                task_status = (
                    task.status.value
                    if isinstance(task.status, Status)
                    else task.status
                )
                priority_val = (
                    task.priority.value
                    if isinstance(task.priority, Priority)
                    else task.priority
                )
                priority_str = format_priority(priority_val)
                updated = format_relative_time(task.updated_at.isoformat())

                table.add_row(
                    task.identifier, title, task_status, priority_str, updated
                )

            console.print(table)

            # Show count
            count_text = "1 task" if len(tasks) == 1 else f"{len(tasks)} tasks"
            console.print(f"\n{count_text}")

        except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error
            # Display user-friendly error for any task listing failure
            if json_output:
                output_json({"error": "ListError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to list tasks: {e}")
            raise typer.Exit(1)
