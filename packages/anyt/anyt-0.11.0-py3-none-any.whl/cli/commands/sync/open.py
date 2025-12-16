"""Open command for opening task folders in editors or file managers."""

import os
import platform
import subprocess
from typing import Optional

import typer
from typing_extensions import Annotated

from cli.commands.console import console
from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.formatters import output_json_data
from cli.config import ActiveTaskConfig
from cli.models.local_task import get_task_dir
from cli.services.local_task_service import LocalTaskService


def _get_file_manager_command() -> list[str]:
    """Get the command to open a file/folder in the system file manager.

    Returns:
        Command list for the current platform's file manager
    """
    system = platform.system()
    if system == "Darwin":
        return ["open"]
    elif system == "Linux":
        return ["xdg-open"]
    else:
        # Windows
        return ["explorer"]


def _open_with_command(
    cmd: list[str], target: str, wait: bool = False
) -> subprocess.CompletedProcess[bytes]:
    """Open a file/folder with the specified command.

    Args:
        cmd: Command list (e.g., ["code"], ["open"])
        target: Path to open
        wait: Whether to wait for the process to complete

    Returns:
        CompletedProcess result
    """
    from cli.utils.platform import subprocess_run_detached

    full_cmd = cmd + [target]
    if wait:
        return subprocess.run(full_cmd, capture_output=True)
    else:
        # Don't wait for editor to close (cross-platform detached process)
        return subprocess_run_detached(full_cmd, capture_output=True)


@async_command()
async def open_task(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-01) to open. Leave empty for active task."
        ),
    ] = None,
    code: Annotated[
        bool,
        typer.Option("--code", help="Open in VSCode"),
    ] = False,
    finder: Annotated[
        bool,
        typer.Option("--finder", help="Open in file manager (Finder/Explorer)"),
    ] = False,
    file: Annotated[
        Optional[str],
        typer.Option(
            "--file", "-f", help="Open a specific file within the task folder"
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Open a task folder in your preferred editor or file manager.

    Opens the task's local folder in your editor, VSCode, or system file manager.
    If the task isn't available locally, prompts to pull it first.

    Examples:

        # Open task in default $EDITOR
        anyt open DEV-01

        # Open in VSCode
        anyt open DEV-01 --code

        # Open in Finder/Explorer
        anyt open DEV-01 --finder

        # Open a specific file
        anyt open DEV-01 --file task.md

        # Open active task
        anyt open
    """
    with CommandContext(require_auth=True, require_workspace=True):
        local_service = LocalTaskService()

        # Resolve identifier - use active task if not provided
        resolved_identifier = identifier
        if not resolved_identifier:
            active_task = ActiveTaskConfig.load()
            if active_task:
                resolved_identifier = active_task.identifier
            else:
                if json_output:
                    console.print_json(
                        data={
                            "success": False,
                            "error": {
                                "code": "NO_IDENTIFIER",
                                "message": "No task identifier provided and no active task set",
                            },
                        }
                    )
                else:
                    console.print(
                        "[red]Error:[/red] No task identifier provided and no active task set"
                    )
                    console.print("Examples:")
                    console.print("  anyt open DEV-01")
                    console.print("  anyt task pick DEV-01  # then 'anyt open'")
                raise typer.Exit(1)

        # Check if task exists locally
        if not local_service.task_exists(resolved_identifier):
            if json_output:
                console.print_json(
                    data={
                        "success": False,
                        "error": {
                            "code": "NOT_FOUND_LOCALLY",
                            "message": f"Task '{resolved_identifier}' not found locally",
                            "suggestion": f"Run 'anyt pull {resolved_identifier}' first",
                        },
                    }
                )
            else:
                console.print(
                    f"[red]Error:[/red] Task '{resolved_identifier}' not found locally"
                )
                console.print(
                    f"Pull it first with: [cyan]anyt pull {resolved_identifier}[/cyan]"
                )
            raise typer.Exit(1)

        # Get task directory
        task_dir = get_task_dir(resolved_identifier, local_service.directory)

        # Determine target (specific file or directory)
        if file:
            target_path = task_dir / file
            if not target_path.exists():
                if json_output:
                    console.print_json(
                        data={
                            "success": False,
                            "error": {
                                "code": "FILE_NOT_FOUND",
                                "message": f"File '{file}' not found in task folder",
                            },
                        }
                    )
                else:
                    console.print(
                        f"[red]Error:[/red] File '{file}' not found in task folder"
                    )
                    console.print(f"Task folder: {task_dir}")
                raise typer.Exit(1)
        else:
            target_path = task_dir

        target = str(target_path)

        # Determine which opener to use
        result_data = {
            "identifier": resolved_identifier,
            "path": target,
            "opened_with": "",
        }

        try:
            if code:
                # Open in VSCode
                _open_with_command(["code"], target)
                result_data["opened_with"] = "vscode"
                if not json_output:
                    console.print(
                        f"[green]✓[/green] Opening [cyan]{resolved_identifier}[/cyan] in VSCode..."
                    )
            elif finder:
                # Open in system file manager
                cmd = _get_file_manager_command()
                _open_with_command(cmd, target)
                result_data["opened_with"] = "file_manager"
                manager_name = (
                    "Finder" if platform.system() == "Darwin" else "file manager"
                )
                if not json_output:
                    console.print(
                        f"[green]✓[/green] Opening [cyan]{resolved_identifier}[/cyan] in {manager_name}..."
                    )
            else:
                # Open in $EDITOR (default to vim)
                editor = os.environ.get("EDITOR", "vim")
                # Default to opening task.md if opening directory in editor
                editor_target = target
                if target_path.is_dir():
                    editor_target = str(task_dir / "task.md")
                _open_with_command([editor], editor_target)
                result_data["opened_with"] = editor
                if not json_output:
                    console.print(
                        f"[green]✓[/green] Opening [cyan]{resolved_identifier}[/cyan] in {editor}..."
                    )

            if json_output:
                output_json_data(result_data)

        except FileNotFoundError as e:
            if json_output:
                console.print_json(
                    data={
                        "success": False,
                        "error": {
                            "code": "COMMAND_NOT_FOUND",
                            "message": f"Command not found: {e}",
                        },
                    }
                )
            else:
                console.print(f"[red]Error:[/red] Command not found: {e}")
                if code:
                    console.print(
                        "Make sure VSCode is installed and 'code' is in your PATH"
                    )
            raise typer.Exit(1)
