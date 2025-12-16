"""Push command for syncing local task changes to server."""

from datetime import UTC, datetime
from typing import Any, Optional

import typer
from typing_extensions import Annotated

from cli.commands.console import console
from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.formatters import output_json_data, output_json_list
from cli.commands.services import ServiceRegistry as services
from cli.models.local_task import LocalTask, get_task_dir
from cli.services.local_task_service import LocalTaskService

from .converters import (
    _build_update_from_local,
    _detect_local_changes,
    _parse_checklist_md,
    _parse_plan_md,
)


async def _push_single_task(
    local_task: LocalTask,
    local_service: LocalTaskService,
    status_override: Optional[str],
    done_flag: bool,
    dry_run: bool,
    json_output: bool,
) -> dict[str, Any]:
    """Push a single task to the server.

    Args:
        local_task: Local task to push
        local_service: LocalTaskService instance
        status_override: Status to use instead of local status
        done_flag: If True, set status to 'done'
        dry_run: If True, don't actually push
        json_output: Whether in JSON mode

    Returns:
        Dictionary with push result details
    """
    task_service = services.get_task_service()
    identifier = local_task.meta.identifier

    # Get current server state for comparison
    server_task = await task_service.get_task(identifier)

    # Detect what would change
    changes = _detect_local_changes(local_task, server_task)

    # Check for local plan.md
    task_dir = get_task_dir(identifier, local_service.directory)
    plan_path = task_dir / "plan.md"
    local_plan: Optional[str] = None
    if plan_path.exists():
        local_plan = _parse_plan_md(plan_path.read_text(encoding="utf-8"))
        # Compare with server plan
        gen_task = server_task.to_generated()
        server_plan = gen_task.implementation_plan or ""
        if local_plan != server_plan:
            changes["plan"] = (local_plan, server_plan)

    # Check for local checklist.md
    checklist_path = task_dir / "checklist.md"
    local_checklist: Optional[str] = None
    if checklist_path.exists():
        local_checklist = _parse_checklist_md(
            checklist_path.read_text(encoding="utf-8")
        )
        # Compare with server checklist
        gen_task = server_task.to_generated()
        server_checklist = gen_task.checklist or ""
        if local_checklist != server_checklist:
            changes["checklist"] = (local_checklist, server_checklist)

    # Apply overrides to changes
    if done_flag:
        changes["status"] = ("done", server_task.status.value)
    elif status_override:
        changes["status"] = (status_override, server_task.status.value)

    result: dict[str, Any] = {
        "identifier": identifier,
        "title": local_task.meta.title,
        "changes": list(changes.keys()),
        "dry_run": dry_run,
        "pushed": False,
    }

    if not changes:
        result["message"] = "No local changes to push"
        return result

    if dry_run:
        result["would_update"] = {
            field: {"local": local_val, "server": server_val}
            for field, (local_val, server_val) in changes.items()
        }
        return result

    # Build and send update - plan and checklist are now included in regular update
    update = _build_update_from_local(local_task, status_override, done_flag)
    # Add implementation plan if changed
    if "plan" in changes and local_plan:
        update.implementation_plan = local_plan
    # Add checklist if changed
    if "checklist" in changes and local_checklist:
        update.checklist = local_checklist
    updated_task = await task_service.update_task(identifier, update)

    # Update local .meta.json with pushed_at timestamp and new server state
    now = datetime.now(UTC)
    local_service.update_task_meta(
        identifier,
        pushed_at=now,
        server_updated_at=updated_task.updated_at,
        status=updated_task.status.value,
        priority=updated_task.priority.value if updated_task.priority else 0,
    )

    result["pushed"] = True
    result["server_updated_at"] = (
        updated_task.updated_at.isoformat() if updated_task.updated_at else None
    )

    return result


def _display_push_result(result: dict[str, Any]) -> None:
    """Display push result in human-readable format.

    Args:
        result: Push result dictionary
    """
    identifier = result["identifier"]

    if result.get("dry_run"):
        if result.get("would_update"):
            console.print(
                f"[yellow]Would push[/yellow] [cyan]{identifier}[/cyan] with changes:"
            )
            for field, values in result["would_update"].items():
                local_val = values["local"]
                server_val = values["server"]
                # Truncate long values
                if isinstance(local_val, str) and len(local_val) > 50:
                    local_val = f"{local_val[:50]}..."
                if isinstance(server_val, str) and len(server_val) > 50:
                    server_val = f"{server_val[:50]}..."
                console.print(
                    f"  {field}: [red]{server_val}[/red] → [green]{local_val}[/green]"
                )
        else:
            console.print(f"[dim]{identifier}: No local changes to push[/dim]")
        return

    if not result.get("changes"):
        console.print(f"[dim]{identifier}: No local changes to push[/dim]")
        return

    if result.get("pushed"):
        changes_str = ", ".join(result["changes"])
        console.print(f"[green]✓[/green] Pushed [cyan]{identifier}[/cyan] to server")
        console.print(f"  Updated: {changes_str}")
        if result.get("server_updated_at"):
            console.print(f"  Server updated_at: {result['server_updated_at']}")


@async_command()
async def push(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-01) to push. Leave empty to push all modified tasks."
        ),
    ] = None,
    status: Annotated[
        Optional[str],
        typer.Option(
            "--status",
            help="Override local status (backlog, todo, active, done, etc.)",
        ),
    ] = None,
    done: Annotated[
        bool,
        typer.Option("--done", help="Push and mark task as done"),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be pushed without pushing"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Push local task changes to server.

    Uploads local task.md and .meta.json changes back to the AnyTask server.
    Title is extracted from the first '# ' line in task.md.
    Description is the remaining content.

    Examples:

        # Push a single task
        anyt push DEV-01

        # Push and mark as done
        anyt push DEV-01 --done

        # Push with status override
        anyt push DEV-01 --status active

        # See what would be pushed
        anyt push DEV-01 --dry-run

        # Push all modified local tasks
        anyt push
    """
    with CommandContext(require_auth=True, require_workspace=True):
        local_service = LocalTaskService()

        # Check if tasks directory exists
        if not local_service.tasks_dir.exists():
            if json_output:
                console.print_json(
                    data={
                        "success": False,
                        "error": {
                            "code": "NO_LOCAL_TASKS",
                            "message": "No local tasks directory found. Run 'anyt pull' first.",
                        },
                    }
                )
            else:
                console.print(
                    "[red]Error:[/red] No local tasks directory found. Run 'anyt pull' first."
                )
            raise typer.Exit(1)

        if identifier:
            # Push single task
            if not local_service.task_exists(identifier):
                if json_output:
                    console.print_json(
                        data={
                            "success": False,
                            "error": {
                                "code": "NOT_FOUND",
                                "message": f"Task '{identifier}' not found locally",
                            },
                        }
                    )
                else:
                    console.print(
                        f"[red]Error:[/red] Task '{identifier}' not found locally"
                    )
                    console.print(f"Run 'anyt pull {identifier}' first.")
                raise typer.Exit(1)

            local_task = local_service.read_task(identifier)
            result = await _push_single_task(
                local_task,
                local_service,
                status,
                done,
                dry_run,
                json_output,
            )

            if json_output:
                output_json_data(result)
            else:
                _display_push_result(result)

        else:
            # Push all modified local tasks
            local_tasks = local_service.list_local_tasks()

            if not local_tasks:
                if json_output:
                    output_json_list([])
                else:
                    console.print("[yellow]No local tasks found[/yellow]")
                raise typer.Exit(0)

            results: list[dict[str, Any]] = []
            pushed_count = 0

            for local_task in local_tasks:
                result = await _push_single_task(
                    local_task,
                    local_service,
                    status,
                    done,
                    dry_run,
                    json_output,
                )
                results.append(result)

                if not json_output:
                    _display_push_result(result)

                if result.get("pushed"):
                    pushed_count += 1

            if json_output:
                output_json_list(results)
            else:
                console.print()
                if dry_run:
                    changes_count = sum(1 for r in results if r.get("would_update"))
                    console.print(
                        f"[yellow]Dry run:[/yellow] {changes_count} task(s) would be pushed"
                    )
                else:
                    console.print(
                        f"[green]✓[/green] Pushed {pushed_count} task(s) to server"
                    )
