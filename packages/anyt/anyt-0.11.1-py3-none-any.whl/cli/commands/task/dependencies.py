"""Dependency management commands for tasks."""

from typing import Any, Optional

import typer
from typing_extensions import Annotated

from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.formatters import output_json_data, output_json_error
from cli.commands.services import ServiceRegistry as services
from cli.models.common import Status

from .helpers import (
    console,
    get_active_task_id,
    truncate_text,
)


@async_command()
async def add_dependency(
    on: Annotated[
        str,
        typer.Option(
            "--on", help="Task(s) this depends on (comma-separated identifiers)"
        ),
    ],
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-43) or ID. Uses active task if not specified."
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Add dependency/dependencies to a task."""
    with CommandContext(require_auth=True, require_workspace=True):
        service = services.get_task_service()

        # Use active task if no identifier provided
        if not identifier:
            identifier = get_active_task_id()
            if not identifier:
                if json_output:
                    output_json_error(
                        "NO_ACTIVE_TASK",
                        "No task identifier provided and no active task set",
                    )
                else:
                    console.print(
                        "[red]Error:[/red] No task identifier provided and no active task set"
                    )
                    console.print(
                        "Specify a task: [cyan]anyt dep add DEV-43 --on DEV-42[/cyan]"
                    )
                    console.print(
                        "Or pick a task first: [cyan]anyt task pick DEV-43[/cyan]"
                    )
                raise typer.Exit(1)

        try:
            # Parse the dependencies - can be comma-separated
            depends_on_list = [dep.strip() for dep in on.split(",")]

            # Validate: task cannot depend on itself
            for dep_id in depends_on_list:
                if dep_id == identifier:
                    if json_output:
                        output_json_error(
                            "SELF_DEPENDENCY",
                            f"Task {identifier} cannot depend on itself",
                        )
                    else:
                        console.print(
                            "[red]✗ Error:[/red] Task cannot depend on itself"
                        )
                    raise typer.Exit(1)

            # Add each dependency
            added_count = 0
            errors: list[str] = []

            for dep_id in depends_on_list:
                try:
                    await service.add_dependency(identifier, dep_id)
                    added_count += 1
                except Exception as e:  # noqa: BLE001 - Intentionally broad: gracefully handle dependency addition failures during bulk operation
                    error_msg = str(e)
                    if "circular" in error_msg.lower():
                        errors.append(f"{dep_id}: Would create circular dependency")
                    elif "404" in error_msg:
                        errors.append(f"{dep_id}: Task not found")
                    elif "409" in error_msg:
                        errors.append(f"{dep_id}: Dependency already exists")
                    else:
                        errors.append(f"{dep_id}: {error_msg}")

            # Display results
            if json_output:
                if added_count > 0:
                    data: dict[str, Any] = {
                        "identifier": identifier,
                        "dependencies_added": depends_on_list[:added_count],
                        "added_count": added_count,
                        "total_count": len(depends_on_list),
                    }
                    if errors:
                        data["warnings"] = errors
                    output_json_data(data)
                else:
                    output_json_error(
                        "ADD_FAILED",
                        "Failed to add dependencies",
                        {"warnings": errors} if errors else None,
                    )
            else:
                if added_count == 1 and len(depends_on_list) == 1:
                    console.print(
                        f"[green]✓[/green] {identifier} now depends on {depends_on_list[0]}"
                    )
                elif added_count > 0:
                    dep_str = ", ".join(depends_on_list[:added_count])
                    console.print(
                        f"[green]✓[/green] {identifier} now depends on {dep_str}"
                    )

                # Display errors
                if errors:
                    console.print()
                    console.print("[yellow]Warnings:[/yellow]")
                    for error in errors:
                        console.print(f"  [red]✗[/red] {error}")

            # Exit with error if all failed
            if added_count == 0:
                raise typer.Exit(1)

        except typer.Exit:
            raise
        except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error for any dependency addition failure
            error_msg = str(e)
            if json_output:
                if "404" in error_msg:
                    output_json_error("NOT_FOUND", f"Task '{identifier}' not found")
                elif "circular" in error_msg.lower():
                    output_json_error(
                        "CIRCULAR_DEPENDENCY",
                        "Adding this dependency would create a circular dependency",
                    )
                else:
                    output_json_error(
                        "ADD_FAILED", f"Failed to add dependency: {error_msg}"
                    )
            else:
                if "404" in error_msg:
                    console.print(f"[red]✗ Error:[/red] Task '{identifier}' not found")
                elif "circular" in error_msg.lower():
                    console.print(
                        "[red]✗ Error:[/red] Adding this dependency would create a circular dependency"
                    )
                else:
                    console.print(f"[red]✗ Error:[/red] Failed to add dependency: {e}")
            raise typer.Exit(1)


@async_command()
async def remove_dependency(
    on: Annotated[
        str,
        typer.Option(
            "--on", help="Task(s) to remove dependency on (comma-separated identifiers)"
        ),
    ],
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-43) or ID. Uses active task if not specified."
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Remove dependency/dependencies from a task."""
    with CommandContext(require_auth=True, require_workspace=True):
        service = services.get_task_service()

        # Use active task if no identifier provided
        if not identifier:
            identifier = get_active_task_id()
            if not identifier:
                if json_output:
                    output_json_error(
                        "NO_ACTIVE_TASK",
                        "No task identifier provided and no active task set",
                    )
                else:
                    console.print(
                        "[red]Error:[/red] No task identifier provided and no active task set"
                    )
                    console.print(
                        "Specify a task: [cyan]anyt dep rm DEV-43 --on DEV-42[/cyan]"
                    )
                    console.print(
                        "Or pick a task first: [cyan]anyt task pick DEV-43[/cyan]"
                    )
                raise typer.Exit(1)

        try:
            # Parse the dependencies - can be comma-separated
            depends_on_list = [dep.strip() for dep in on.split(",")]

            # Remove each dependency
            removed_count = 0
            errors: list[str] = []

            for dep_id in depends_on_list:
                try:
                    await service.remove_dependency(identifier, dep_id)
                    removed_count += 1
                except Exception as e:  # noqa: BLE001 - Intentionally broad: gracefully handle dependency removal failures during bulk operation
                    error_msg = str(e)
                    if "404" in error_msg:
                        errors.append(f"{dep_id}: Dependency not found")
                    else:
                        errors.append(f"{dep_id}: {error_msg}")

            # Display results
            if json_output:
                if removed_count > 0:
                    data: dict[str, Any] = {
                        "identifier": identifier,
                        "dependencies_removed": depends_on_list[:removed_count],
                        "removed_count": removed_count,
                        "total_count": len(depends_on_list),
                    }
                    if errors:
                        data["warnings"] = errors
                    output_json_data(data)
                else:
                    output_json_error(
                        "REMOVE_FAILED",
                        "Failed to remove dependencies",
                        {"warnings": errors} if errors else None,
                    )
            else:
                if removed_count == 1 and len(depends_on_list) == 1:
                    console.print(
                        f"[green]✓[/green] Removed dependency: {identifier} → {depends_on_list[0]}"
                    )
                elif removed_count > 0:
                    console.print(
                        f"[green]✓[/green] Removed {removed_count} dependencies from {identifier}"
                    )

                # Display errors
                if errors:
                    console.print()
                    console.print("[yellow]Warnings:[/yellow]")
                    for error in errors:
                        console.print(f"  [red]✗[/red] {error}")

            # Exit with error if all failed
            if removed_count == 0:
                raise typer.Exit(1)

        except typer.Exit:
            raise
        except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error for any dependency removal failure
            error_msg = str(e)
            if json_output:
                if "404" in error_msg:
                    output_json_error("NOT_FOUND", f"Task '{identifier}' not found")
                else:
                    output_json_error(
                        "REMOVE_FAILED", f"Failed to remove dependency: {error_msg}"
                    )
            else:
                if "404" in error_msg:
                    console.print(f"[red]✗ Error:[/red] Task '{identifier}' not found")
                else:
                    console.print(
                        f"[red]✗ Error:[/red] Failed to remove dependency: {e}"
                    )
            raise typer.Exit(1)


@async_command()
async def list_dependencies(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-43) or ID. Uses active task if not specified."
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """List task dependencies and dependents."""
    with CommandContext(require_auth=True, require_workspace=True):
        service = services.get_task_service()

        # Use active task if no identifier provided
        if not identifier:
            identifier = get_active_task_id()
            if not identifier:
                if json_output:
                    output_json_error(
                        "NO_ACTIVE_TASK",
                        "No task identifier provided and no active task set",
                    )
                else:
                    console.print(
                        "[red]Error:[/red] No task identifier provided and no active task set"
                    )
                    console.print("Specify a task: [cyan]anyt dep list DEV-43[/cyan]")
                    console.print(
                        "Or pick a task first: [cyan]anyt task pick DEV-43[/cyan]"
                    )
                raise typer.Exit(1)

        try:
            # Fetch task details
            task = await service.get_task(identifier)

            # Fetch dependencies (tasks this depends on)
            dependencies = await service.get_task_dependencies(identifier)

            # Fetch dependents (tasks that depend on this)
            dependents = await service.get_task_dependents(identifier)

            if json_output:
                output_json_data(
                    {
                        "task": {
                            "identifier": task.identifier,
                            "title": task.title,
                        },
                        "dependencies": [
                            dep.model_dump(mode="json") for dep in dependencies
                        ],
                        "dependents": [
                            dept.model_dump(mode="json") for dept in dependents
                        ],
                    }
                )
            else:
                # Display header
                console.print()
                console.print(f"[cyan bold]{task.identifier}:[/cyan bold] {task.title}")
                console.print("━" * 60)
                console.print()

                # Display dependencies
                console.print("[bold]Dependencies[/bold] (tasks this depends on):")
                if dependencies:
                    for dep in dependencies:
                        dep_title = truncate_text(dep.title, 50)
                        dep_status = (
                            dep.status.value
                            if isinstance(dep.status, Status)
                            else dep.status
                        )

                        # Status symbol
                        if dep_status == "done":
                            status_symbol = "[green]✓[/green]"
                        elif dep_status == "active":
                            status_symbol = "[yellow]⬤[/yellow]"
                        elif dep_status == "backlog":
                            status_symbol = "[dim]⬜[/dim]"
                        else:
                            status_symbol = "[dim]○[/dim]"

                        console.print(
                            f"  → [cyan]{dep.identifier}[/cyan]  {dep_title}  {status_symbol} {dep_status}"
                        )
                else:
                    console.print("  [dim]No dependencies[/dim]")

                console.print()

                # Display dependents
                console.print("[bold]Blocks[/bold] (tasks that depend on this):")
                if dependents:
                    for dependent in dependents:
                        dept_title = truncate_text(dependent.title, 50)
                        dept_status = (
                            dependent.status.value
                            if isinstance(dependent.status, Status)
                            else dependent.status
                        )

                        # Status symbol
                        if dept_status == "done":
                            status_symbol = "[green]✓[/green]"
                        elif dept_status == "active":
                            status_symbol = "[yellow]⬤[/yellow]"
                        elif dept_status == "backlog":
                            status_symbol = "[dim]⬜[/dim]"
                        else:
                            status_symbol = "[dim]○[/dim]"

                        console.print(
                            f"  ← [cyan]{dependent.identifier}[/cyan]  {dept_title}  {status_symbol} {dept_status}"
                        )
                else:
                    console.print("  [dim]No dependents[/dim]")

                console.print()

        except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error for any dependency listing failure
            error_msg = str(e)
            if json_output:
                if "404" in error_msg:
                    output_json_error("NOT_FOUND", f"Task '{identifier}' not found")
                else:
                    output_json_error(
                        "LIST_FAILED", f"Failed to fetch dependencies: {error_msg}"
                    )
            else:
                if "404" in error_msg:
                    console.print(f"[red]✗ Error:[/red] Task '{identifier}' not found")
                else:
                    console.print(
                        f"[red]✗ Error:[/red] Failed to fetch dependencies: {e}"
                    )
            raise typer.Exit(1)
