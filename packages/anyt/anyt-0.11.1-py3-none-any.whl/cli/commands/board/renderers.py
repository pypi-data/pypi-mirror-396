"""Task rendering utilities for summary visualization."""

from typing import Any

from rich.console import Console

from cli.commands.task.helpers import (
    format_priority,
    format_relative_time,
    truncate_text,
)
from cli.models.wrappers.dependency_graph import DependencyGraphResponse


def annotate_blocked_tasks_from_graph(
    tasks: list[dict[str, Any]], graph: DependencyGraphResponse
) -> None:
    """Annotate tasks with blocked status using dependency graph data.

    This function modifies tasks in-place, adding "blocked_by" field to blocked tasks.
    Uses pre-fetched dependency graph data instead of N+1 API calls.

    Args:
        tasks: List of tasks to annotate (modified in-place)
        graph: Complete dependency graph with all tasks and dependencies
    """
    # Get set of blocked task IDs from graph
    blocked_ids = graph.get_blocked_tasks()

    # Annotate each task
    for task in tasks:
        identifier = task.get("identifier", str(task.get("id")))

        if identifier in blocked_ids:
            # Task is blocked - get blocking tasks
            blocking_nodes = graph.get_blocking_tasks(identifier)

            # Convert nodes to dict format for display
            task["blocked_by"] = [
                {
                    "identifier": node.id,
                    "title": node.title,
                    "status": node.status,
                    "priority": node.priority,
                }
                for node in blocking_nodes
            ]


def render_summary_section(
    title: str,
    icon: str,
    style: str,
    tasks: list[dict[str, Any]],
    max_display: int,
    console: Console,
    show_owner: bool = False,
) -> None:
    """Render a section of the summary (done, active, etc.)."""
    console.print(f"[{style}]{icon} {title} ({len(tasks)} tasks)[/{style}]")
    for task in tasks[:max_display]:
        task_id = task.get("identifier", str(task.get("id", "")))
        title_text = truncate_text(task.get("title", ""), 60 if not show_owner else 50)

        if show_owner:
            owner_id = task.get("owner_id", "—")
            if owner_id:
                owner_display = owner_id[:15] if len(owner_id) > 15 else owner_id
            else:
                owner_display = "unassigned"
            updated = format_relative_time(task.get("updated_at"))
            console.print(f"   • {task_id} {title_text} ({owner_display}, {updated})")
        else:
            console.print(f"   • {task_id} {title_text}")

    if len(tasks) > max_display:
        console.print(f"   [dim]... and {len(tasks) - max_display} more[/dim]")
    console.print()


def render_priorities_section(
    tasks: list[dict[str, Any]],
    console: Console,
) -> None:
    """Render the next priorities section of the summary."""
    console.print("[bold]📅 Next Priorities[/bold]")

    for i, task in enumerate(tasks[:3], 1):
        task_id = task.get("identifier", str(task.get("id", "")))
        title = truncate_text(task.get("title", ""), 60)
        priority = format_priority(task.get("priority", 0))
        console.print(f"   {i}. {task_id} {title} {priority}")
    console.print()


def render_summary_header(
    period: str,
    console: Console,
) -> None:
    """Render the summary header."""
    console.print()
    console.print("━" * 80)
    title_text = f"Workspace Summary - {period.capitalize()}"
    console.print(f"  [cyan bold]{title_text}[/cyan bold]")
    console.print("━" * 80)
    console.print()


def render_progress_footer(
    done_count: int,
    total: int,
    console: Console,
) -> None:
    """Render the progress footer."""
    console.print("━" * 80)
    progress_pct = int((done_count / total) * 100) if total > 0 else 0
    console.print(f"Progress: {done_count}/{total} tasks complete ({progress_pct}%)")
    console.print()
