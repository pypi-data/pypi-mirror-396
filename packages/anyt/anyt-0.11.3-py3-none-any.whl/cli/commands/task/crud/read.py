"""Read commands for tasks (show)."""

from typing import Optional

import typer
from rich.markdown import Markdown
from rich.panel import Panel
from typing_extensions import Annotated

from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.formatters import output_json
from cli.commands.services import ServiceRegistry as services
from cli.models.common import Priority, Status

from ..helpers import (
    console,
    find_similar_tasks,
    format_priority,
    format_relative_time,
    get_active_task_id,
    normalize_identifier,
    resolve_workspace_context,
    truncate_text,
)


def _format_pr_status(status: str | None) -> str:
    """Format PR status with colors."""
    if not status:
        return "[dim]unknown[/dim]"
    status_colors = {
        "draft": "[dim]draft[/dim]",
        "open": "[blue]open[/blue]",
        "merged": "[green]merged[/green]",
        "closed": "[red]closed[/red]",
    }
    return status_colors.get(status, f"[dim]{status}[/dim]")


@async_command()
async def show_task(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-42, t_1Z for UID). Uses active task if not specified."
        ),
    ] = None,
    workspace: Annotated[
        Optional[str],
        typer.Option(
            "--workspace",
            "-w",
            help="Workspace identifier or ID (uses current workspace if not specified)",
        ),
    ] = None,
    full: Annotated[
        bool,
        typer.Option(
            "--full",
            "-f",
            help="Show full details: complete plan, all PRs, dependencies, and comments",
        ),
    ] = False,
    show_metadata: Annotated[
        bool,
        typer.Option("--show-metadata", help="Display workflow execution metadata"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Show detailed information about a task.

    Supports both workspace-scoped identifiers (DEV-42) and UIDs (t_1Z).
    """
    with CommandContext(require_auth=True, require_workspace=True):
        service = services.get_task_service()
        workspace_service = services.get_workspace_service()

    # Use active task if no identifier provided
    if not identifier:
        identifier = get_active_task_id()
        if not identifier:
            if json_output:
                output_json(
                    {
                        "error": "ValidationError",
                        "message": "No task identifier provided and no active task set",
                        "suggestions": [
                            "Specify a task: anyt task show DEV-42",
                            "Or pick a task first: anyt task pick DEV-42",
                        ],
                    },
                    success=False,
                )
            else:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print("Specify a task: [cyan]anyt task show DEV-42[/cyan]")
                console.print(
                    "Or pick a task first: [cyan]anyt task pick DEV-42[/cyan]"
                )
            raise typer.Exit(1)

    # Initialize normalized_id with the original identifier
    # (will be updated if we go through workspace-scoped path)
    normalized_id = identifier

    try:
        # Check if identifier is a UID (starts with 't_')
        if identifier.startswith("t_"):
            # Use UID endpoint (no workspace context needed)
            task = await service.get_task_by_uid(identifier)
        else:
            # Resolve workspace context for workspace-scoped identifiers
            workspace_id, workspace_identifier = await resolve_workspace_context(
                workspace, workspace_service
            )

            # Normalize identifier for fuzzy matching with workspace prefix
            normalized_id = normalize_identifier(identifier, workspace_identifier)

            # Fetch task using service
            task = await service.get_task(normalized_id)

        # JSON output mode
        if json_output:
            output_json(task.model_dump(mode="json"))
            return

        # Rich console output mode
        console.print()
        console.print(f"[cyan bold]{task.identifier}:[/cyan bold] {task.title}")
        console.print(f"[dim]UID: {task.uid}[/dim]")
        console.print("━" * 60)

        # Status and priority line
        priority_str = format_priority(
            task.priority.value
            if isinstance(task.priority, Priority)
            else task.priority
        )
        console.print(
            f"Status: [yellow]{task.status.value if isinstance(task.status, Status) else task.status}[/yellow]    "
            f"Priority: {priority_str} ({task.priority.value if isinstance(task.priority, Priority) else task.priority})"
        )

        # Owner
        if task.owner_id:
            console.print(f"Owner: {task.owner_id}")
        else:
            console.print("Owner: [dim]unassigned[/dim]")

        # Project
        console.print(f"Project: {task.project_id}")

        # Description
        if task.description:
            console.print()
            console.print("[bold]Description:[/bold]")
            console.print()
            # Render description as markdown
            markdown = Markdown(task.description)
            console.print(markdown)

        # Implementation Plan section (if exists)
        # Access the underlying generated task for plan fields
        gen_task = task.to_generated()
        if gen_task.implementation_plan:
            console.print()
            console.print("[bold]Implementation Plan:[/bold]")
            if full:
                # Show full plan content
                console.print()
                console.print(
                    Panel(
                        Markdown(gen_task.implementation_plan),
                        title="Implementation Plan",
                        border_style="blue",
                    )
                )
            else:
                # Show truncated preview of plan
                plan_preview = gen_task.implementation_plan
                if len(plan_preview) > 200:
                    plan_preview = plan_preview[:200] + "..."
                console.print()
                console.print(
                    Panel(
                        Markdown(plan_preview),
                        title="Plan Preview",
                        border_style="blue",
                        subtitle="[dim]Use --full for full plan[/dim]",
                    )
                )

        # Pull Requests section (fetch from API)
        try:
            pr_client = services.get_pull_requests_client()
            prs = await pr_client.list_task_prs(task.identifier)
            if prs:
                console.print()
                console.print("[bold]Pull Requests:[/bold]")
                # Show all PRs if --full, otherwise limit to 3
                display_prs = prs if full else prs[:3]
                for pr in display_prs:
                    pr_status_str = _format_pr_status(
                        pr.pr_status.value if pr.pr_status else None
                    )
                    console.print(
                        f"  [cyan]#{pr.pr_number}[/cyan] {pr.head_branch} → {pr.base_branch}  {pr_status_str}"
                    )
                    console.print(f"    [dim]{pr.pr_url}[/dim]")
                if not full and len(prs) > 3:
                    console.print(
                        f"  [dim]... and {len(prs) - 3} more. Use --full or 'anyt task pr list' to see all.[/dim]"
                    )
        except Exception:  # noqa: BLE001 - Gracefully skip PR section on errors
            pass  # Don't fail task show if PR fetch fails

        # Dependencies section (only with --full flag)
        if full:
            try:
                dependencies = await service.get_task_dependencies(task.identifier)
                dependents = await service.get_task_dependents(task.identifier)

                if dependencies or dependents:
                    console.print()
                    console.print("[bold]Dependencies:[/bold]")

                    if dependencies:
                        console.print("  [dim]This task depends on:[/dim]")
                        for dep in dependencies:
                            dep_status = (
                                dep.status.value
                                if isinstance(dep.status, Status)
                                else dep.status
                            )
                            status_symbol = (
                                "[green]✓[/green]"
                                if dep_status == "done"
                                else "[yellow]⬤[/yellow]"
                                if dep_status == "active"
                                else "[dim]○[/dim]"
                            )
                            console.print(
                                f"    → [cyan]{dep.identifier}[/cyan] {truncate_text(dep.title, 40)} {status_symbol}"
                            )
                    else:
                        console.print("  [dim]No dependencies[/dim]")

                    if dependents:
                        console.print("  [dim]Blocks these tasks:[/dim]")
                        for dept in dependents:
                            dept_status = (
                                dept.status.value
                                if isinstance(dept.status, Status)
                                else dept.status
                            )
                            status_symbol = (
                                "[green]✓[/green]"
                                if dept_status == "done"
                                else "[yellow]⬤[/yellow]"
                                if dept_status == "active"
                                else "[dim]○[/dim]"
                            )
                            console.print(
                                f"    ← [cyan]{dept.identifier}[/cyan] {truncate_text(dept.title, 40)} {status_symbol}"
                            )
                    else:
                        console.print("  [dim]Not blocking any tasks[/dim]")
            except Exception:  # noqa: BLE001 - Gracefully skip dependencies on errors
                pass

        # Comments section (only with --full flag)
        if full:
            try:
                comments_client = services.get_comments_client()
                comments = await comments_client.list_comments(task.identifier)
                if comments:
                    console.print()
                    console.print("[bold]Comments:[/bold]")
                    for comment in comments:
                        # Format timestamp
                        comment_time = (
                            format_relative_time(comment.created_at.isoformat())
                            if comment.created_at
                            else "unknown"
                        )
                        author = (
                            f"user {comment.user_id}" if comment.user_id else "unknown"
                        )
                        console.print(f"  [dim]{comment_time} by {author}[/dim]")
                        # Show comment content (truncate if very long)
                        content = comment.content or ""
                        if len(content) > 200:
                            content = content[:200] + "..."
                        console.print(f"    {content}")
                        console.print()
            except Exception:  # noqa: BLE001 - Gracefully skip comments on errors
                pass

        # Workflow Execution Metadata (if requested)
        if show_metadata:
            workflow_metadata = await service.get_workflow_metadata(task.identifier)
            if workflow_metadata:
                console.print()
                console.print("[bold]Workflow Executions:[/bold]")
                console.print()
                for exec_meta in workflow_metadata:
                    # Status with emoji
                    status_emoji = {
                        "success": "✅",
                        "running": "🔄",
                        "failure": "❌",
                        "cancelled": "⏹️",
                    }.get(exec_meta.status, "❓")

                    console.print(
                        f"  {status_emoji} [bold]{exec_meta.workflow_execution_id}[/bold]"
                    )
                    console.print(
                        f"      Workflow: [cyan]{exec_meta.workflow_name}[/cyan]"
                    )
                    console.print(
                        f"      Coding Agent: [dim]{exec_meta.agent_id}[/dim]"
                    )
                    console.print(f"      Status: {exec_meta.status}")
                    console.print(f"      Started: {exec_meta.started_at}")

                    if exec_meta.completed_at:
                        console.print(f"      Completed: {exec_meta.completed_at}")

                    if exec_meta.duration_seconds is not None:
                        # Format duration nicely
                        duration = exec_meta.duration_seconds
                        if duration < 60:
                            duration_str = f"{duration:.1f}s"
                        elif duration < 3600:
                            duration_str = f"{duration / 60:.1f}m"
                        else:
                            duration_str = f"{duration / 3600:.1f}h"
                        console.print(f"      Duration: {duration_str}")

                    console.print()

        # Metadata
        console.print()
        created = format_relative_time(task.created_at.isoformat())
        updated = format_relative_time(task.updated_at.isoformat())
        console.print(f"Created: {created}")
        console.print(f"Updated: {updated}")
        console.print(f"Version: {task.version}")
        console.print()

    except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error for any task fetch failure
        error_msg = str(e)
        if "404" in error_msg:
            # Resolve workspace for error messages
            try:
                workspace_id, _ = await resolve_workspace_context(
                    workspace, workspace_service
                )
            except Exception:  # noqa: BLE001 - Intentionally broad: gracefully handle workspace context resolution failure for error messages
                workspace_id = None

            # Try to find similar tasks for suggestions
            similar_tasks = []
            if workspace_id:
                similar_tasks = await find_similar_tasks(
                    service, workspace_id, normalized_id
                )

            if json_output:
                output_json(
                    {
                        "error": "NotFoundError",
                        "message": f"Task '{normalized_id}' not found"
                        + (f" in workspace {workspace_id}" if workspace_id else ""),
                        "suggestions": [
                            {
                                "identifier": t.get("identifier"),
                                "title": t.get("title"),
                            }
                            for t in similar_tasks
                        ],
                    },
                    success=False,
                )
            else:
                workspace_info = f" in workspace {workspace_id}" if workspace_id else ""
                console.print(
                    f"[red]✗ Error:[/red] Task '{normalized_id}' not found{workspace_info}"
                )

                if similar_tasks:
                    console.print()
                    console.print("  Did you mean:")
                    for task_dict in similar_tasks:
                        task_id = task_dict.get(
                            "identifier", str(task_dict.get("id", ""))
                        )
                        title = truncate_text(task_dict.get("title", ""), 40)
                        console.print(f"    [cyan]{task_id}[/cyan]  {title}")

                console.print()
                console.print("  List all tasks: [cyan]anyt task list[/cyan]")
        else:
            if json_output:
                output_json({"error": "FetchError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to fetch task: {e}")
        raise typer.Exit(1)
