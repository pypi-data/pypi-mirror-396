"""Summary visualization command for AnyTask CLI."""

from typing import Optional

import typer
from typing_extensions import Annotated

from cli.commands.board.formatters import (
    format_error_json,
    format_summary_json,
)
from cli.commands.board.renderers import (
    annotate_blocked_tasks_from_graph,
    render_priorities_section,
    render_progress_footer,
    render_summary_header,
    render_summary_section,
)
from cli.commands.console import console
from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.guards import require_workspace_config
from cli.commands.services import ServiceRegistry as services
from cli.models.task import TaskFilters
from cli.utils.typer_utils import HelpOnErrorGroup

app = typer.Typer(help="Summary visualization commands", cls=HelpOnErrorGroup)


@app.command("summary")
@async_command()
async def show_summary(
    period: Annotated[
        str,
        typer.Option("--period", help="Summary period: today, weekly, monthly"),
    ] = "today",
    phase: Annotated[
        Optional[str],
        typer.Option("--phase", help="Filter by phase/milestone"),
    ] = None,
    project: Annotated[
        Optional[int],
        typer.Option("--project", help="Filter by project ID"),
    ] = None,
    all_projects: Annotated[
        bool,
        typer.Option(
            "--all", help="Show tasks from all projects (ignore current_project_id)"
        ),
    ] = False,
    format_output: Annotated[
        str,
        typer.Option("--format", help="Output format: text, markdown, json"),
    ] = "text",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Generate workspace summary with done, active, blocked, and next priorities."""
    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        task_service = services.get_task_service()
        workspaces_client = services.get_workspaces_client()

        # Validate workspace config (guards against -O flag and provides type narrowing)
        workspace_config = require_workspace_config(ctx.workspace_config)

        try:
            # Resolve project_id: --project flag > current_project_id > None (all)
            # --all flag explicitly shows all projects
            project_id = None
            if not all_projects:
                if project:
                    project_id = project
                elif workspace_config.current_project_id:
                    project_id = workspace_config.current_project_id

            # Fetch all tasks
            filters = TaskFilters(
                workspace_id=int(workspace_config.workspace_id),
                project_id=project_id,
                phase=phase,
                limit=100,
                sort_by="updated_at",
                order="desc",
            )
            task_list = await task_service.list_tasks(filters)
            tasks = [task.model_dump() for task in task_list]
            total = len(tasks)

            if not tasks:
                console.print("[yellow]No tasks in workspace[/yellow]")
                return

            # Categorize tasks
            done_tasks = [t for t in tasks if t.get("status") == "done"]
            active_tasks = [t for t in tasks if t.get("status") == "active"]
            backlog_tasks = [t for t in tasks if t.get("status") in ["backlog", "todo"]]

            # Fetch dependency graph and annotate blocked tasks
            graph = await workspaces_client.get_dependency_graph(
                workspace_id=int(workspace_config.workspace_id)
            )
            annotate_blocked_tasks_from_graph(tasks, graph)
            blocked_tasks = [t for t in tasks if "blocked_by" in t]

            use_json = json_output or format_output == "json"

            if use_json:
                print(
                    format_summary_json(
                        period,
                        done_tasks,
                        active_tasks,
                        blocked_tasks,
                        backlog_tasks,
                        total,
                    )
                )
                return

            # Render summary
            render_summary_header(period, console)
            render_summary_section("Done", "✅", "green", done_tasks, 5, console)
            render_summary_section(
                "Active", "🔄", "yellow", active_tasks, 5, console, show_owner=True
            )

            if blocked_tasks:
                render_summary_section(
                    "Blocked", "🚫", "red", blocked_tasks, 10, console
                )

            high_priority_backlog = sorted(
                backlog_tasks, key=lambda t: t.get("priority", 0), reverse=True
            )
            render_priorities_section(high_priority_backlog, console)
            render_progress_footer(len(done_tasks), total, console)

        except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error for any summary generation failure
            use_json = json_output or format_output == "json"
            if use_json:
                print(format_error_json(f"Failed to generate summary: {str(e)}"))
            else:
                console.print(f"[red]Error:[/red] Failed to generate summary: {e}")
            raise typer.Exit(1)
