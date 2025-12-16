"""CLI commands for task implementation plans."""

from typing import Optional

import typer
from rich.markdown import Markdown
from rich.panel import Panel
from typing_extensions import Annotated

from cli.client.exceptions import APIError, NotFoundError
from cli.commands.console import console
from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.formatters import output_json_data
from cli.commands.guards import require_workspace_config
from cli.commands.services import ServiceRegistry as services
from cli.commands.task.helpers import get_active_task_id
from cli.utils.errors import handle_api_error
from cli.utils.typer_utils import HelpOnErrorGroup

app = typer.Typer(help="Manage task implementation plans", cls=HelpOnErrorGroup)


@app.command("show")
@async_command()
async def show_plan(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-42). Uses active task if not provided."
        ),
    ] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show the implementation plan for a task.

    Examples:
        # Show plan for active task
        anyt task plan show

        # Show plan for specific task
        anyt task plan show DEV-42

        # JSON output
        anyt task plan show DEV-42 --json
    """
    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        workspace_config = require_workspace_config(ctx.workspace_config)

        # Resolve task identifier
        if not identifier:
            identifier = get_active_task_id()
            if not identifier:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print(
                    "Use [cyan]anyt task pick <task-id>[/cyan] to set active task"
                )
                raise typer.Exit(1)

        try:
            tasks_client = services.get_tasks_client()
            task = await tasks_client.get_task_by_workspace(
                workspace_config.workspace_id, identifier
            )

            if json_output:
                output_json_data(
                    {
                        "identifier": task.identifier,
                        "implementation_plan": task.implementation_plan,
                    }
                )
            else:
                console.print()
                console.print(f"[cyan bold]{task.identifier}:[/cyan bold] {task.title}")
                console.print("━" * 60)

                console.print()

                # Plan content
                if task.implementation_plan:
                    console.print(
                        Panel(
                            Markdown(task.implementation_plan),
                            title="Implementation Plan",
                            border_style="blue",
                        )
                    )
                else:
                    console.print("[dim]No implementation plan set yet.[/dim]")
                    console.print()
                    console.print(
                        "[dim]Set a plan with:[/dim] "
                        f"[cyan]anyt task edit {identifier} --plan-file plan.md[/cyan]"
                    )

                console.print()

        except NotFoundError:
            console.print(f"[red]Error:[/red] Task '{identifier}' not found")
            raise typer.Exit(1)
        except APIError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        except Exception as e:  # noqa: BLE001
            handle_api_error(e, "fetching plan")
