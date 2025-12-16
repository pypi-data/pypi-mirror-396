"""Pull command for syncing tasks from server to local filesystem."""

from datetime import UTC, datetime
from typing import Any, Optional

import typer
from typing_extensions import Annotated

from cli.commands.console import console
from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.formatters import output_json_data, output_json_list
from cli.commands.services import ServiceRegistry as services
from cli.commands.task.crud.edit_helpers import get_task_or_error
from cli.config import ActiveTaskConfig
from cli.models.common import Status
from cli.models.local_task import LocalTaskMeta
from cli.models.task import TaskFilters
from cli.models.wrappers.task import Task
from cli.services.local_task_service import LocalTaskService

from .converters import _format_file_size, _task_to_local_meta


def _show_diff_summary(
    local_service: LocalTaskService,
    identifier: str,
    new_description: str,
    new_meta: LocalTaskMeta,
) -> bool:
    """Show diff summary between local and server versions.

    Args:
        local_service: LocalTaskService instance
        identifier: Task identifier
        new_description: New description from server
        new_meta: New metadata from server

    Returns:
        True if there were differences, False otherwise
    """
    if not local_service.task_exists(identifier):
        return False

    local_task = local_service.read_task(identifier)
    has_diff = False

    # Check for differences
    diffs: list[str] = []

    if local_task.meta.title != new_meta.title:
        diffs.append(f"  title: '{local_task.meta.title}' → '{new_meta.title}'")
        has_diff = True

    if local_task.meta.status != new_meta.status:
        diffs.append(f"  status: {local_task.meta.status} → {new_meta.status}")
        has_diff = True

    if local_task.meta.priority != new_meta.priority:
        diffs.append(f"  priority: {local_task.meta.priority} → {new_meta.priority}")
        has_diff = True

    if local_task.description != new_description:
        old_len = len(local_task.description)
        new_len = len(new_description)
        diffs.append(f"  description: {old_len} chars → {new_len} chars")
        has_diff = True

    if diffs:
        console.print("[dim]Changes from server:[/dim]")
        for diff in diffs:
            console.print(f"[yellow]{diff}[/yellow]")

    return has_diff


async def _pull_single_task(
    task: Task,
    local_service: LocalTaskService,
    pick: bool,
    show_diff: bool,
    json_output: bool,
) -> dict[str, Any]:
    """Pull a single task to local filesystem.

    Args:
        task: Task to pull
        local_service: LocalTaskService instance
        pick: Whether to set as active task
        show_diff: Whether to show diff summary
        json_output: Whether in JSON mode

    Returns:
        Dictionary with pull result details
    """
    # Convert to local format
    meta = _task_to_local_meta(task)
    description = task.description or ""

    # Check for existing task and show diff if requested
    existed = local_service.task_exists(task.identifier)
    had_diff = False
    if existed and show_diff and not json_output:
        had_diff = _show_diff_summary(local_service, task.identifier, description, meta)

    # Write task to local filesystem
    local_task = local_service.write_task(meta, description)

    # Calculate file sizes
    task_dir = local_task.path
    md_path = task_dir / "task.md"
    meta_path = task_dir / ".meta.json"
    context_dir = task_dir / "context"
    plan_path = task_dir / "plan.md"

    md_size = md_path.stat().st_size if md_path.exists() else 0
    meta_size = meta_path.stat().st_size if meta_path.exists() else 0

    # Write plan.md if task has an implementation plan
    plan_size = 0
    has_plan = False
    gen_task = task.to_generated()
    if gen_task.implementation_plan:
        plan_content = f"# Implementation Plan\n\n{gen_task.implementation_plan}"
        plan_path.write_text(plan_content, encoding="utf-8")
        plan_size = plan_path.stat().st_size
        has_plan = True

    # Write checklist.md if task has a checklist
    checklist_path = task_dir / "checklist.md"
    checklist_size = 0
    has_checklist = False
    if gen_task.checklist:
        checklist_content = f"# Checklist\n\n{gen_task.checklist}"
        checklist_path.write_text(checklist_content, encoding="utf-8")
        checklist_size = checklist_path.stat().st_size
        has_checklist = True

    result = {
        "identifier": task.identifier,
        "title": task.title,
        "path": str(task_dir),
        "task_md_size": md_size,
        "meta_json_size": meta_size,
        "plan_md_size": plan_size,
        "has_plan": has_plan,
        "checklist_md_size": checklist_size,
        "has_checklist": has_checklist,
        "context_created": not existed and context_dir.exists(),
        "overwritten": existed,
        "had_diff": had_diff,
        "picked": False,
    }

    # Set as active task if requested
    if pick:
        active_task = ActiveTaskConfig(
            identifier=task.identifier,
            title=task.title,
            picked_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            workspace_id=task.workspace_id,
            project_id=task.project_id,
        )
        active_task.save()
        result["picked"] = True

    return result


def _display_pull_result(result: dict[str, Any], show_details: bool = True) -> None:
    """Display pull result in human-readable format.

    Args:
        result: Pull result dictionary
        show_details: Whether to show file details
    """
    identifier = result["identifier"]
    path = result["path"]
    overwritten = result["overwritten"]

    action = "Updated" if overwritten else "Pulled"
    console.print(f"[green]✓[/green] {action} [cyan]{identifier}[/cyan] to {path}")

    if show_details:
        md_size = _format_file_size(result["task_md_size"])
        console.print(f"  - task.md ({md_size})")
        console.print("  - .meta.json")
        if result.get("has_plan"):
            plan_size = _format_file_size(result.get("plan_md_size", 0))
            console.print(f"  - plan.md ({plan_size})")
        if result.get("has_checklist"):
            checklist_size = _format_file_size(result.get("checklist_md_size", 0))
            console.print(f"  - checklist.md ({checklist_size})")
        if result["context_created"]:
            console.print("  - context/ (created)")

    if result["picked"]:
        console.print("  [yellow]→ Set as active task[/yellow]")


@async_command()
async def pull(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-01) to pull. Leave empty with --mine to pull assigned tasks."
        ),
    ] = None,
    mine: Annotated[
        bool,
        typer.Option("--mine", help="Pull all tasks assigned to you"),
    ] = False,
    status: Annotated[
        Optional[str],
        typer.Option(
            "--status",
            help="Filter by status (backlog, todo, active, done, etc.). Comma-separated.",
        ),
    ] = None,
    pick: Annotated[
        bool,
        typer.Option("--pick", help="Set the pulled task as active (single task only)"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Pull tasks from server to local filesystem.

    Downloads task data to .anyt/tasks/{IDENTIFIER}/ directory with:
    - task.md: Task title and description
    - .meta.json: Task metadata (status, priority, labels, etc.)
    - context/: Directory for local AI context files

    Examples:

        # Pull a single task
        anyt pull DEV-01

        # Pull and set as active task
        anyt pull DEV-01 --pick

        # Pull all tasks assigned to you
        anyt pull --mine

        # Pull assigned tasks with specific status
        anyt pull --mine --status active,todo
    """
    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        # Validate arguments
        if not identifier and not mine:
            if json_output:
                console.print_json(
                    data={
                        "success": False,
                        "error": {
                            "code": "MISSING_ARGUMENT",
                            "message": "Provide a task identifier or use --mine",
                        },
                    }
                )
            else:
                console.print(
                    "[red]Error:[/red] Provide a task identifier or use --mine"
                )
                console.print("Examples:")
                console.print("  anyt pull DEV-01")
                console.print("  anyt pull --mine")
            raise typer.Exit(1)

        if pick and mine:
            if json_output:
                console.print_json(
                    data={
                        "success": False,
                        "error": {
                            "code": "INVALID_ARGUMENT",
                            "message": "--pick can only be used with a single task identifier",
                        },
                    }
                )
            else:
                console.print(
                    "[red]Error:[/red] --pick can only be used with a single task identifier"
                )
            raise typer.Exit(1)

        task_service = services.get_task_service()
        local_service = LocalTaskService()

        # Ensure tasks directory exists
        local_service.ensure_tasks_dir()

        if identifier:
            # Pull single task with standardized error handling
            task = await get_task_or_error(identifier, task_service, json_output)
            if task is None:
                raise typer.Exit(1)

            result = await _pull_single_task(
                task, local_service, pick, show_diff=True, json_output=json_output
            )

            if json_output:
                output_json_data(result)
            else:
                _display_pull_result(result)

        else:
            # Pull multiple tasks (--mine)
            assert ctx.workspace_config is not None  # Guaranteed by require_workspace

            # Build filters
            status_list = None
            if status:
                status_list = [Status(s.strip()) for s in status.split(",")]

            filters = TaskFilters(
                workspace_id=int(ctx.workspace_config.workspace_id),
                status=status_list,
                owner="me",
            )

            tasks = await task_service.list_tasks(filters)

            if not tasks:
                if json_output:
                    output_json_list([])
                else:
                    console.print("[yellow]No tasks found matching filters[/yellow]")
                    if status:
                        console.print(f"  Status filter: {status}")
                raise typer.Exit(0)

            # Pull each task
            results: list[dict[str, Any]] = []
            for task in tasks:
                result = await _pull_single_task(
                    task,
                    local_service,
                    pick=False,
                    show_diff=False,
                    json_output=json_output,
                )
                results.append(result)

                if not json_output:
                    _display_pull_result(result, show_details=False)

            if json_output:
                output_json_list(results)
            else:
                console.print()
                console.print(
                    f"[green]✓[/green] Pulled {len(results)} task(s) to .anyt/tasks/"
                )
