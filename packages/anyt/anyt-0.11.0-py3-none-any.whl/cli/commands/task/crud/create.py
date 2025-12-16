"""Create commands for tasks (add)."""

from typing import Optional

import typer
from typing_extensions import Annotated

from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.formatters import output_json
from cli.commands.guards import require_workspace_config
from cli.commands.services import ServiceRegistry as services
from cli.commands.validators import validate_priority_for_create, validate_status
from cli.models.common import Priority
from cli.models.task import TaskCreate

from cli.commands.utils import get_project_id
from ..helpers import console, resolve_plan_content


@async_command()
async def add_task(
    title: Annotated[str, typer.Argument(help="Task title")],
    description: Annotated[
        Optional[str],
        typer.Option("-d", "--description", help="Task description"),
    ] = None,
    phase: Annotated[
        Optional[str],
        typer.Option("--phase", help="Phase/milestone identifier (e.g., T3, Phase 1)"),
    ] = None,
    priority: Annotated[
        int,
        typer.Option(
            "-p",
            "--priority",
            help="Priority level: -2 (lowest), -1 (low), 0 (normal), 1 (high), 2 (highest). Default: 0",
        ),
    ] = 0,
    status: Annotated[
        str,
        typer.Option(
            "--status",
            help="Task status (backlog, todo, active, blocked, done, canceled, archived). Default: backlog",
        ),
    ] = "backlog",
    owner: Annotated[
        Optional[str],
        typer.Option("--owner", help="Assign to user or agent ID"),
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
    """Create a new task."""
    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        workspace_config = require_workspace_config(ctx.workspace_config)

        service = services.get_task_service()
        projects_client = services.get_projects_client()

        try:
            # Validate priority range
            if not validate_priority_for_create(priority, json_output):
                raise typer.Exit(1)

            # Validate status (always has a default value, so status_enum is guaranteed non-None)
            is_valid, status_enum = validate_status(status, json_output)
            if not is_valid:
                raise typer.Exit(1)
            assert status_enum is not None  # status always has default value

            # Get project ID from config or API
            project_id = await get_project_id(
                project_arg=None,
                ws_config=workspace_config,
                projects_client=projects_client,
            )

            # Ensure project_id is set
            if project_id is None:
                raise ValueError("Project ID is required but not set")

            # Convert priority to enum (already validated)
            priority_enum = Priority(priority)

            # Handle plan content - validate options and read content
            plan_content = resolve_plan_content(plan, plan_file, json_output)

            # Create task using typed model
            task_create = TaskCreate(
                title=title,
                description=description,
                phase=phase,
                status=status_enum,
                priority=priority_enum,
                owner_id=owner,
                project_id=project_id,
                implementation_plan=plan_content,
            )

            # Create task via service
            task = await service.create_task_with_validation(
                project_id=project_id,
                task=task_create,
            )

            # Display success
            if json_output:
                output_json(task.model_dump(mode="json"))
            else:
                console.print(
                    f"[green]✓[/green] Created: [cyan]{task.identifier}[/cyan] ({task.title})"
                )
                if plan_content:
                    console.print("  Implementation plan saved")

        except typer.Exit:
            raise
        except ValueError as e:
            # Handle enum conversion errors
            if json_output:
                output_json(
                    {"error": "ValidationError", "message": str(e)}, success=False
                )
            else:
                console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error
            # Display user-friendly error for any task creation failure
            if json_output:
                output_json({"error": "CreateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to create task: {e}")
            raise typer.Exit(1)
