"""Unpick command for clearing the active task."""

import json

import typer
from typing_extensions import Annotated

from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.config import ActiveTaskConfig

from .helpers import console


@async_command()
async def unpick_task(
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Clear the currently active task.

    This command removes the active task selection without picking a new one.
    The task's status on the server is NOT changed - only the local
    .anyt/active_task.json is cleared.

    Examples:
        anyt task unpick        # Clear active task
        anyt task unpick --json # JSON output
    """
    with CommandContext(require_auth=False, require_workspace=True):
        # Load current active task to show what we're clearing
        active_task = ActiveTaskConfig.load()

        if not active_task:
            if json_output:
                print(
                    json.dumps(
                        {
                            "success": True,
                            "message": "No active task to clear",
                        }
                    )
                )
            else:
                console.print("[yellow]No active task to clear[/yellow]")
            return

        # Remember the identifier before clearing
        cleared_identifier = active_task.identifier
        cleared_title = active_task.title

        # Clear the active task
        ActiveTaskConfig.clear()

        if json_output:
            print(
                json.dumps(
                    {
                        "success": True,
                        "message": f"Cleared active task {cleared_identifier}",
                        "data": {
                            "cleared_identifier": cleared_identifier,
                            "cleared_title": cleared_title,
                        },
                    }
                )
            )
        else:
            console.print(
                f"[green]✓[/green] Cleared active task [cyan]{cleared_identifier}[/cyan] ({cleared_title})"
            )
            console.print("  Pick a new task with: [cyan]anyt task pick <ID>[/cyan]")
