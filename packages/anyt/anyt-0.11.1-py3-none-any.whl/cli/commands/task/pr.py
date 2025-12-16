"""CLI commands for task pull requests."""

from typing import Optional

import typer
from rich.table import Table
from typing_extensions import Annotated

from cli.client.exceptions import APIError, NotFoundError, ValidationError
from cli.commands.console import console
from cli.commands.context import CommandContext
from cli.commands.decorators import async_command
from cli.commands.formatters import output_json_data, output_json_error
from cli.commands.guards import require_workspace_config
from cli.commands.services import ServiceRegistry as services
from cli.commands.task.helpers import get_active_task_id
from cli.utils.errors import handle_api_error
from cli.utils.typer_utils import HelpOnErrorGroup
from sdk.generated.models.PRStatus import PRStatus

app = typer.Typer(help="Manage task pull requests", cls=HelpOnErrorGroup)


def _format_pr_status(status: PRStatus | str | None) -> str:
    """Format PR status with colors."""
    if not status:
        return "[dim]unknown[/dim]"
    status_str = status.value if isinstance(status, PRStatus) else status
    status_colors = {
        "draft": "[dim]draft[/dim]",
        "open": "[blue]open[/blue]",
        "merged": "[green]merged[/green]",
        "closed": "[red]closed[/red]",
    }
    return status_colors.get(status_str, f"[dim]{status_str}[/dim]")


def _format_review_status(status: str | None) -> str:
    """Format review status with colors."""
    if not status:
        return "[dim]none[/dim]"
    status_colors = {
        "pending": "[yellow]pending[/yellow]",
        "approved": "[green]approved[/green]",
        "changes_requested": "[red]changes_requested[/red]",
    }
    return status_colors.get(status, f"[dim]{status}[/dim]")


def _format_ci_status(status: str | None, conclusion: str | None) -> str:
    """Format CI status with colors."""
    if not status:
        return "[dim]none[/dim]"
    if status == "completed":
        if conclusion == "success":
            return "[green]✓ passed[/green]"
        elif conclusion == "failure":
            return "[red]✗ failed[/red]"
        else:
            return f"[yellow]{conclusion or 'unknown'}[/yellow]"
    elif status == "in_progress":
        return "[yellow]⋯ running[/yellow]"
    elif status == "queued":
        return "[dim]queued[/dim]"
    return f"[dim]{status}[/dim]"


@app.command("list")
@async_command()
async def list_prs(
    identifier: Annotated[
        Optional[str],
        typer.Argument(help="Task identifier. Uses active task if not provided."),
    ] = None,
    status: Annotated[
        Optional[str],
        typer.Option(
            "--status",
            "-s",
            help="Filter by PR status (draft, open, merged, closed).",
        ),
    ] = None,
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            "-l",
            help="Maximum number of PRs to show.",
        ),
    ] = 20,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List pull requests for a task.

    Examples:
        # List PRs for active task
        anyt task pr list

        # List PRs for specific task
        anyt task pr list DEV-42

        # List open PRs for a task
        anyt task pr list DEV-42 --status open

        # JSON output
        anyt task pr list DEV-42 --json
    """
    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        # Validate workspace is configured (needed by PR client)
        require_workspace_config(ctx.workspace_config)

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
            pr_client = services.get_pull_requests_client()

            # Parse status filter
            pr_status: PRStatus | None = None
            if status:
                try:
                    pr_status = PRStatus(status)
                except ValueError:
                    console.print(
                        f"[red]Error:[/red] Invalid status '{status}'. "
                        "Must be one of: draft, open, merged, closed"
                    )
                    raise typer.Exit(1)

            # List PRs for the task
            prs = await pr_client.list_task_prs(identifier)
            # Filter by status if provided
            if pr_status:
                prs = [p for p in prs if p.pr_status == pr_status]

            # Apply limit
            prs = prs[:limit]

            if json_output:
                output_json_data(
                    {
                        "task_identifier": identifier,
                        "pull_requests": [
                            {
                                "id": pr.id,
                                "pr_number": pr.pr_number,
                                "pr_url": pr.pr_url,
                                "head_branch": pr.head_branch,
                                "base_branch": pr.base_branch,
                                "pr_status": pr.pr_status.value
                                if pr.pr_status
                                else None,
                                "review_status": pr.review_status.value
                                if pr.review_status
                                else None,
                                "ci_status": pr.ci_status.value
                                if pr.ci_status
                                else None,
                                "ci_conclusion": pr.ci_conclusion.value
                                if pr.ci_conclusion
                                else None,
                                "mergeable": pr.mergeable,
                                "opened_at": pr.opened_at,
                                "merged_at": pr.merged_at,
                            }
                            for pr in prs
                        ],
                        "count": len(prs),
                    }
                )
            else:
                if not prs:
                    console.print(
                        f"No pull requests found for task [cyan]{identifier}[/cyan]"
                    )
                    return

                # Display PRs in a table
                title = f"Pull Requests for {identifier}"
                table = Table(title=title)
                table.add_column("#", style="dim")
                table.add_column("Branch", style="cyan")
                table.add_column("Status", style="white")
                table.add_column("Review", style="white")
                table.add_column("CI", style="white")
                table.add_column("URL", style="dim")

                for pr in prs:
                    table.add_row(
                        str(pr.pr_number),
                        pr.head_branch,
                        _format_pr_status(pr.pr_status),
                        _format_review_status(
                            pr.review_status.value if pr.review_status else None
                        ),
                        _format_ci_status(
                            pr.ci_status.value if pr.ci_status else None,
                            pr.ci_conclusion.value if pr.ci_conclusion else None,
                        ),
                        pr.pr_url,
                    )

                console.print(table)
                console.print(f"\n[dim]Total: {len(prs)} PR(s)[/dim]")

        except NotFoundError:
            console.print(f"[red]Error:[/red] Task '{identifier}' not found")
            raise typer.Exit(1)
        except APIError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        except Exception as e:  # noqa: BLE001
            handle_api_error(e, "listing pull requests")


@app.command("show")
@async_command()
async def show_pr(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-42). Uses active task if not provided."
        ),
    ] = None,
    pr_number: Annotated[
        Optional[int],
        typer.Option(
            "--pr",
            "-p",
            help="Specific PR number to show. Shows latest if not specified.",
        ),
    ] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show detailed information about a pull request.

    Examples:
        # Show latest PR for active task
        anyt task pr show

        # Show latest PR for specific task
        anyt task pr show DEV-42

        # Show specific PR by number
        anyt task pr show DEV-42 --pr 123
    """
    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        # Validate workspace is configured (needed by PR client)
        require_workspace_config(ctx.workspace_config)

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
            pr_client = services.get_pull_requests_client()

            # Get PRs for task
            prs = await pr_client.list_task_prs(identifier)

            if not prs:
                if json_output:
                    output_json_error(
                        "NOT_FOUND",
                        f"No pull requests found for task '{identifier}'",
                    )
                else:
                    console.print(
                        f"[yellow]No pull requests found for task [cyan]{identifier}[/cyan][/yellow]"
                    )
                raise typer.Exit(1)

            # Find the requested PR
            pr = None
            if pr_number:
                for p in prs:
                    if p.pr_number == pr_number:
                        pr = p
                        break
                if not pr:
                    console.print(
                        f"[red]Error:[/red] PR #{pr_number} not found for task {identifier}"
                    )
                    raise typer.Exit(1)
            else:
                # Get the most recent PR (first in list, usually sorted by created_at desc)
                pr = prs[0]

            if json_output:
                output_json_data(
                    {
                        "id": pr.id,
                        "task_identifier": identifier,
                        "pr_number": pr.pr_number,
                        "pr_url": pr.pr_url,
                        "head_branch": pr.head_branch,
                        "base_branch": pr.base_branch,
                        "head_sha": pr.head_sha,
                        "pr_status": pr.pr_status.value if pr.pr_status else None,
                        "review_status": pr.review_status.value
                        if pr.review_status
                        else None,
                        "review_count": pr.review_count,
                        "approved_count": pr.approved_count,
                        "changes_requested_count": pr.changes_requested_count,
                        "ci_status": pr.ci_status.value if pr.ci_status else None,
                        "ci_conclusion": pr.ci_conclusion.value
                        if pr.ci_conclusion
                        else None,
                        "ci_check_runs_total": pr.ci_check_runs_total,
                        "ci_check_runs_completed": pr.ci_check_runs_completed,
                        "ci_check_runs_failed": pr.ci_check_runs_failed,
                        "mergeable": pr.mergeable,
                        "opened_at": pr.opened_at,
                        "merged_at": pr.merged_at,
                        "closed_at": pr.closed_at,
                        "created_at": pr.created_at,
                        "updated_at": pr.updated_at,
                    }
                )
            else:
                console.print()
                console.print(
                    f"[cyan bold]PR #{pr.pr_number}[/cyan bold] for [cyan]{identifier}[/cyan]"
                )
                console.print("━" * 60)

                # Branch info
                console.print(
                    f"Branch: [green]{pr.head_branch}[/green] → [blue]{pr.base_branch}[/blue]"
                )
                console.print(f"SHA: [dim]{pr.head_sha}[/dim]")
                console.print()

                # Status section
                console.print("[bold]Status:[/bold]")
                console.print(f"  PR: {_format_pr_status(pr.pr_status)}")
                console.print(
                    f"  Review: {_format_review_status(pr.review_status.value if pr.review_status else None)}"
                )
                if pr.review_count:
                    console.print(
                        f"    Reviews: {pr.review_count} "
                        f"([green]{pr.approved_count or 0} approved[/green], "
                        f"[red]{pr.changes_requested_count or 0} changes requested[/red])"
                    )
                console.print(
                    f"  CI: {_format_ci_status(pr.ci_status.value if pr.ci_status else None, pr.ci_conclusion.value if pr.ci_conclusion else None)}"
                )
                if pr.ci_check_runs_total:
                    console.print(
                        f"    Checks: {pr.ci_check_runs_completed or 0}/{pr.ci_check_runs_total} completed"
                        + (
                            f" ([red]{pr.ci_check_runs_failed} failed[/red])"
                            if pr.ci_check_runs_failed
                            else ""
                        )
                    )

                # Mergeable
                if pr.mergeable is not None:
                    mergeable_str = (
                        "[green]✓ mergeable[/green]"
                        if pr.mergeable
                        else "[red]✗ not mergeable[/red]"
                    )
                    console.print(f"  Mergeable: {mergeable_str}")

                console.print()

                # Timestamps
                console.print("[bold]Timeline:[/bold]")
                console.print(f"  Opened: {pr.opened_at}")
                if pr.merged_at:
                    console.print(f"  Merged: [green]{pr.merged_at}[/green]")
                if pr.closed_at and not pr.merged_at:
                    console.print(f"  Closed: [red]{pr.closed_at}[/red]")

                console.print()
                console.print(f"[dim]URL: {pr.pr_url}[/dim]")
                console.print()

        except NotFoundError:
            console.print(f"[red]Error:[/red] Task '{identifier}' not found")
            raise typer.Exit(1)
        except APIError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        except Exception as e:  # noqa: BLE001
            handle_api_error(e, "showing pull request")


@app.command("register")
@async_command()
async def register_pr(
    pr_number: Annotated[
        int,
        typer.Option(
            "--pr-number",
            "-n",
            help="GitHub PR number.",
        ),
    ],
    pr_url: Annotated[
        str,
        typer.Option(
            "--pr-url",
            "-u",
            help="URL to the PR on GitHub.",
        ),
    ],
    head_branch: Annotated[
        str,
        typer.Option(
            "--head-branch",
            help="Source branch name.",
        ),
    ],
    base_branch: Annotated[
        str,
        typer.Option(
            "--base-branch",
            help="Target branch name.",
        ),
    ],
    head_sha: Annotated[
        str,
        typer.Option(
            "--head-sha",
            help="SHA of the head commit.",
        ),
    ],
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-42). Uses active task if not provided."
        ),
    ] = None,
    status: Annotated[
        Optional[str],
        typer.Option(
            "--status",
            help="PR status (draft, open, merged, closed). Defaults to 'open'.",
        ),
    ] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Register a pull request for a task.

    This command is typically used by agents to link a PR to a task after creation.

    Examples:
        # Register a PR for the active task
        anyt task pr register --pr-number 123 --pr-url https://github.com/org/repo/pull/123 \\
            --head-branch feature/DEV-42 --base-branch main --head-sha abc123

        # Register for specific task with draft status
        anyt task pr register DEV-42 -n 123 -u https://... -h feature/DEV-42 -b main -s abc123 --status draft
    """
    with CommandContext(require_auth=True, require_workspace=True) as ctx:
        # Validate workspace is configured (needed by PR client)
        require_workspace_config(ctx.workspace_config)

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

        # Parse PR status
        pr_status: PRStatus | None = None
        if status:
            try:
                pr_status = PRStatus(status)
            except ValueError:
                console.print(
                    f"[red]Error:[/red] Invalid status '{status}'. "
                    "Must be one of: draft, open, merged, closed"
                )
                raise typer.Exit(1)

        try:
            pr_client = services.get_pull_requests_client()

            # Register the PR
            pr = await pr_client.create_pr(
                identifier=identifier,
                pr_number=pr_number,
                pr_url=pr_url,
                head_branch=head_branch,
                base_branch=base_branch,
                head_sha=head_sha,
                pr_status=pr_status,
            )

            if json_output:
                output_json_data(
                    {
                        "id": pr.id,
                        "task_identifier": identifier,
                        "pr_number": pr.pr_number,
                        "pr_url": pr.pr_url,
                        "head_branch": pr.head_branch,
                        "base_branch": pr.base_branch,
                        "pr_status": pr.pr_status.value if pr.pr_status else None,
                    }
                )
            else:
                console.print(
                    f"[green]✓[/green] PR #{pr_number} registered for task [cyan]{identifier}[/cyan]"
                )
                console.print(f"  Branch: {head_branch} → {base_branch}")
                console.print(f"  URL: {pr_url}")

        except NotFoundError:
            console.print(f"[red]Error:[/red] Task '{identifier}' not found")
            raise typer.Exit(1)
        except ValidationError as e:
            console.print(f"[red]Error:[/red] Invalid PR data: {e}")
            raise typer.Exit(1)
        except APIError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        except Exception as e:  # noqa: BLE001
            handle_api_error(e, "registering pull request")
