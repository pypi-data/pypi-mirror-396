"""Main entry point for the AnyTask CLI."""

import sys
import typer
from typing_extensions import Annotated

from cli.commands.console import console
from cli.utils.errors import install_traceback_handler, handle_api_error
from cli.utils.typer_utils import HelpOnErrorGroup
from cli.commands import task as task_commands
from cli.commands import init as init_command
from cli.commands import login as login_command
from cli.commands import health as health_commands
from cli.commands import comment as comment_commands
from cli.commands import config_commands
from cli.commands import sync as sync_commands
from cli.commands import self_update as self_commands
from cli.commands import agent as agent_commands
from cli.commands.board.commands import show_summary
from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.formatters import output_json
from cli.commands.services import ServiceRegistry as services
from cli.config import ActiveTaskConfig


app = typer.Typer(
    name="anyt",
    help="AnyTask - AI-native task management from the command line",
    add_completion=False,
    cls=HelpOnErrorGroup,
)

# Register command groups
app.add_typer(config_commands.app, name="config")
app.add_typer(task_commands.app, name="task")
app.add_typer(health_commands.app, name="health")
app.add_typer(comment_commands.app, name="comment")
app.add_typer(self_commands.app, name="self")
app.add_typer(agent_commands.app, name="agent")

# Register summary command as top-level command
app.command("summary")(show_summary)

# Register init and login commands as top-level commands
app.command("init")(init_command.init)
app.command("login")(login_command.login)

# Register sync commands as top-level commands
app.command("pull")(sync_commands.pull)
app.command("push")(sync_commands.push)


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", "-v", help="Show version and exit"),
    ] = False,
):
    """AnyTask CLI - Manage tasks, projects, and workflows."""
    if version:
        from cli import __version__

        typer.echo(f"anyt version {__version__}")
        raise typer.Exit()

    # If no command and no version flag, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command("active")
@async_command()
async def show_active(
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
):
    """Show the currently active task."""
    with CommandContext(require_auth=True, require_workspace=True):
        # Load active task
        active_task = ActiveTaskConfig.load()
        if not active_task:
            if json_output:
                output_json(
                    {
                        "error": "NoActiveTask",
                        "message": "No active task set",
                        "suggestions": ["Pick a task with: anyt task pick"],
                    },
                    success=False,
                )
            else:
                console.print("[yellow]No active task[/yellow]")
                console.print("Pick one with: [cyan]anyt task pick[/cyan]")
            raise typer.Exit(0)

        # Fetch task details
        service = services.get_task_service()
        try:
            task = await service.get_task(active_task.identifier)

            if json_output:
                # Output JSON with task details and active task metadata
                output_json(
                    {
                        "task": task.model_dump(mode="json"),
                        "active_task_metadata": {
                            "identifier": active_task.identifier,
                            "title": active_task.title,
                            "picked_at": active_task.picked_at,
                            "workspace_id": active_task.workspace_id,
                            "project_id": active_task.project_id,
                        },
                    }
                )
            else:
                # Display formatted output
                from cli.commands.task.helpers import (
                    format_priority,
                    format_relative_time,
                )

                task_id = task.identifier
                title = task.title

                console.print()
                console.print(f"[cyan bold]{task_id}:[/cyan bold] {title}")
                console.print("━" * 60)

                # Status and priority
                status = task.status.value
                priority_val = task.priority
                priority_str = format_priority(priority_val)
                console.print(
                    f"Status: [yellow]{status}[/yellow]    Priority: {priority_str} ({priority_val})"
                )

                # Owner
                owner_id = task.owner_id
                if owner_id:
                    console.print(f"Owner: {owner_id}")
                else:
                    console.print("Owner: [dim]unassigned[/dim]")

                # Dependencies status (simplified)
                console.print()
                console.print(
                    "[dim]Dependencies: (use 'anyt dep list' for details)[/dim]"
                )

                # Timestamps
                console.print()
                updated = (
                    format_relative_time(task.updated_at.isoformat())
                    if task.updated_at
                    else "never"
                )
                console.print(f"Last updated: {updated}")

                # Show when task was picked
                picked_time = format_relative_time(active_task.picked_at)
                console.print(f"Picked: {picked_time}")

                console.print()

        except Exception as e:  # noqa: BLE001 - Intentionally broad: gracefully handle task display errors
            # Gracefully handle task display errors and show helpful message
            error_msg = str(e)
            if "404" in error_msg:
                if json_output:
                    output_json(
                        {
                            "error": "TaskNotFound",
                            "message": f"Active task '{active_task.identifier}' not found",
                            "suggestions": [
                                "The task may have been deleted",
                                "Clear active task with: rm .anyt/active_task.json",
                            ],
                        },
                        success=False,
                    )
                else:
                    console.print(
                        f"[red]Error:[/red] Active task '{active_task.identifier}' not found"
                    )
                    console.print(
                        "It may have been deleted. Clear with: [cyan]rm .anyt/active_task.json[/cyan]"
                    )
            else:
                if json_output:
                    output_json(
                        {
                            "error": "FetchError",
                            "message": f"Failed to fetch task: {str(e)}",
                            "suggestions": [
                                "Check your network connection",
                                "Verify API authentication",
                            ],
                        },
                        success=False,
                    )
                else:
                    console.print(f"[red]Error:[/red] Failed to fetch task: {e}")
            raise typer.Exit(1)


def main():
    """Entry point for the CLI."""
    # Install rich traceback handler if in debug mode
    install_traceback_handler()

    try:
        app()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        console.print("\n[yellow]Cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:  # noqa: BLE001 - Intentionally broad: top-level error handler
        # Top-level error handler for unhandled exceptions
        handle_api_error(e, "running command")


if __name__ == "__main__":
    main()
