"""
Worker start command for running automated task processing.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from worker.workflow_models import Workflow

import typer
from rich.markup import escape
from InquirerPy.base.control import Choice

from cli.commands.console import console
from cli.utils.interactive import select_one, is_interactive
from worker.commands.helpers import resolve_workflow_file
from worker.coordinator import TaskCoordinator
from worker.workflow_models import ProjectScope


def start(
    workspace_dir: Optional[Path] = typer.Option(
        None,
        "--workspace",
        "-w",
        help="Workspace directory (default: current directory)",
    ),
    workflow: Optional[str] = typer.Option(
        None,
        "--workflow",
        help="Workflow to run (local_dev, remote_dev). If not specified, shows interactive selection with remote_dev as default.",
    ),
    workflows_dir: Optional[Path] = typer.Option(
        None,
        "--workflows",
        help="Workflows directory (default: .anyt/workflows). If --workflow is specified, loads from this directory.",
    ),
    poll_interval: int = typer.Option(
        5,
        "--poll-interval",
        "-i",
        help="Polling interval in seconds",
    ),
    max_backoff: int = typer.Option(
        60,
        "--max-backoff",
        help="Maximum backoff interval in seconds",
    ),
    project_id: Optional[int] = typer.Option(
        None,
        "--project-id",
        "-p",
        help="Project ID to scope task suggestions. If not provided, loads from .anyt/anyt.json (current_project_id field).",
    ),
    skip_checks: bool = typer.Option(
        False,
        "--skip-checks",
        help="Skip workflow requirement validation before starting",
    ),
    force_check: bool = typer.Option(
        False,
        "--force-check",
        help="Force fresh requirement checks (bypass cache)",
    ),
    clone_repos: bool = typer.Option(
        False,
        "--clone-repos",
        help="Force clone project repos for all workflows (overrides workflow settings.clone_repo)",
    ),
    no_cleanup: bool = typer.Option(
        False,
        "--no-cleanup",
        help="Keep task workspaces after execution (overrides workflow settings.cleanup_workspace)",
    ),
    agents: Optional[str] = typer.Option(
        None,
        "--agents",
        help="Comma-separated list of coding agents to use (e.g., 'claude,codex'). If not specified, runs interactive agent detection.",
    ),
    skip_detection: bool = typer.Option(
        False,
        "--skip-detection",
        help="Skip interactive agent detection and filter by all known agent types.",
    ),
) -> None:
    """
    Start the Claude task worker.

    The worker continuously polls for tasks and executes workflows automatically.

    Setup:
    1. Set ANYT_API_KEY environment variable for API authentication
    2. Run 'anyt worker start' and select workflow

    Workflow Selection:
    - If --workflow is NOT provided: Shows interactive workflow selector (default: remote_dev)
    - If --workflow is provided: Uses that specific workflow directly

    Workflow Options:
    - No options: Interactive workflow selection (default: remote_dev)
    - --workflow remote_dev: Runs ONLY remote_dev workflow (skips interactive selection)
    - --workflows-dir /custom: Custom workflows directory

    Agent Detection:
    - By default, runs interactive agent detection to discover installed coding agents
    - Use --agents to specify agents explicitly (e.g., --agents claude,codex)
    - Use --skip-detection to skip detection and use all known agent types

    Built-in workflows (bundled with CLI, no setup required):
    - remote_dev (default): Clone remote GitHub repo, implement task, create PR
    - local_dev: Quick iterations on current branch, no branch management

    Workflow Comparison:
    | Workflow    | Clone Repo | Branch Mgmt | PR Creation | Best For           |
    |-------------|------------|-------------|-------------|--------------------|
    | remote_dev  | Yes        | Yes         | Yes         | Remote GitHub repos|
    | local_dev   | -          | -           | -           | Quick development  |

    Example:
        export ANYT_API_KEY=anyt_agent_...  # API key for authentication
        anyt worker start  # Interactive workflow selection + agent detection
        anyt worker start --workflow local_dev  # Direct workflow selection
        anyt worker start --agents claude,codex  # Explicit agent list
        anyt worker start --skip-detection  # Skip agent detection
        anyt worker start --project-id 123
        anyt worker start --poll-interval 10 --workspace /path/to/project
    """
    workspace = workspace_dir or Path.cwd()

    if not workspace.exists():
        console.print(
            f"[red]Error: Workspace directory does not exist: {workspace}[/red]"
        )
        raise typer.Exit(1)

    # Load workspace config if available (optional)
    from cli.config import WorkspaceConfig

    workspace_config = WorkspaceConfig.load(workspace)

    # Use config defaults if not provided via CLI
    effective_project_id = project_id
    if workspace_config and workspace_config.current_project_id:
        effective_project_id = (
            effective_project_id or workspace_config.current_project_id
        )

    if effective_project_id:
        console.print(f"[dim]Using project_id: {effective_project_id}[/dim]")

    # Prompt for workflow selection if not specified
    resolved_workflow = _resolve_workflow(workflow)

    # Resolve workflow file if --workflow is specified
    workflow_file: Optional[Path] = None
    if resolved_workflow:
        try:
            workflow_file = resolve_workflow_file(
                resolved_workflow, workspace, workflows_dir
            )
            console.print(
                f"[green]Using workflow:[/green] {resolved_workflow} (from {workflow_file.parent})"
            )
        except ValueError as e:
            console.print(f"[red]Error: {escape(str(e))}[/red]")
            raise typer.Exit(1)

    # Check workflow requirements before starting (unless skipped)
    if not skip_checks and workflow_file:
        _check_workflow_requirements(
            workflow_file, resolved_workflow, workspace, force_check
        )

    # Load workflow to get project_scope setting
    workflow_obj = _load_workflow(workflow_file) if workflow_file else None
    project_scope = (
        workflow_obj.settings.project_scope
        if workflow_obj and workflow_obj.settings
        else ProjectScope.WORKSPACE
    )

    # Resolve workspace_id: from config, or discover dynamically
    workspace_id: int
    if workspace_config:
        workspace_id = workspace_config.workspace_id
        console.print(f"[dim]Using workspace from config: {workspace_id}[/dim]")
    else:
        # Dynamic workspace discovery
        from cli.utils.platform import run_async

        discovered_workspace_id = run_async(
            _discover_workspace_interactive(project_scope)
        )
        if discovered_workspace_id is None:
            console.print("[red]Error: Could not determine workspace[/red]")
            console.print(
                "[yellow]Hint: Initialize workspace with 'anyt init' "
                "or ensure ANYT_API_KEY is set[/yellow]"
            )
            raise typer.Exit(1)
        workspace_id = discovered_workspace_id

    # Resolve project_id based on workflow's project_scope setting
    if project_scope == ProjectScope.PROJECT and effective_project_id is None:
        # Project scope workflow requires a project selection
        from cli.utils.platform import run_async

        discovered_project_id = run_async(
            _discover_project_interactive(workspace_id, project_scope)
        )
        if discovered_project_id is not None:
            effective_project_id = discovered_project_id
            console.print(f"[dim]Using project_id: {effective_project_id}[/dim]")

    # Resolve coding agents
    coding_agents = _resolve_coding_agents(agents, skip_detection)

    # Create coordinator and run
    coordinator = TaskCoordinator(
        workspace_dir=workspace,
        workspace_id=workspace_id,
        workflows_dir=workflows_dir,
        workflow_file=workflow_file,
        poll_interval=poll_interval,
        max_backoff=max_backoff,
        project_id=effective_project_id,
        clone_repos=clone_repos,
        cleanup_workspaces=not no_cleanup,
        coding_agents=coding_agents,
    )

    try:
        from cli.utils.platform import run_async

        run_async(coordinator.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Worker stopped by user[/yellow]")


def _resolve_workflow(workflow: Optional[str]) -> str:
    """Resolve workflow from option or interactive selection."""
    if workflow:
        return workflow

    # Define workflow options
    workflows_list = [
        (
            "remote_dev",
            "Clone remote repo, implement task, create PR (for linked GitHub repos)",
        ),
        (
            "local_dev",
            "Quick iterations on current branch (no branch management, commits directly)",
        ),
    ]

    default_workflow = "remote_dev"

    # Non-interactive mode: use default
    if not is_interactive():
        console.print(f"[green]Using default workflow: {default_workflow}[/green]")
        return default_workflow

    # Build choices for InquirerPy select
    choices: list[Choice] = []
    for wf_name, wf_desc in workflows_list:
        # Mark default with indicator
        if wf_name == default_workflow:
            display_name = f"{wf_name} [DEFAULT] - {wf_desc}"
        else:
            display_name = f"{wf_name} - {wf_desc}"
        choices.append(Choice(value=wf_name, name=display_name))

    console.print()

    try:
        selected_workflow: str = select_one(
            choices=choices,
            message="Select a workflow to run:",
            default=default_workflow,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
        raise typer.Exit(0)

    console.print(f"[green]✓[/green] Selected workflow: {selected_workflow}")
    return selected_workflow


def _check_workflow_requirements(
    workflow_file: Path,
    workflow_name: str,
    workspace: Path,
    force_check: bool,
) -> None:
    """Check workflow requirements before starting."""
    import yaml

    from worker.commands.workflow_formatters import display_check_results
    from worker.services.workflow_requirements import WorkflowRequirementsService
    from worker.workflow_models import Workflow

    try:
        # Load workflow definition
        with open(workflow_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            # Fix YAML boolean key issue (on: becomes True)
            if True in data:
                data["on"] = data.pop(True)
            workflow_obj = Workflow(**data)

        # Check if workflow has requirements
        if workflow_obj.requirements and workflow_obj.requirements.has_requirements():
            console.print()
            console.print("[cyan]Checking workflow requirements...[/cyan]")

            # Run requirement checks
            from cli.utils.platform import run_async

            service = WorkflowRequirementsService(workspace_dir=workspace)
            results = run_async(
                service.check_requirements(
                    requirements=workflow_obj.requirements,
                    workflow_name=workflow_obj.name,
                    force=force_check,
                )
            )

            if results.is_success():
                # All checks passed - show what was validated
                for req_name, check_result in results.results:
                    if check_result.success:
                        console.print(
                            f"[green]✓[/green] {req_name}: {check_result.message}"
                        )
                    elif check_result.warning:
                        console.print(
                            f"[yellow]⚠[/yellow]  {req_name}: {check_result.message}"
                        )

                console.print()
                cache_status = " (cached)" if results.from_cache else ""
                console.print(f"[green]✓ All requirements met{cache_status}[/green]")
            else:
                # Some checks failed
                console.print()
                display_check_results(results)
                console.print()
                console.print(
                    "[yellow]Run [cyan]anyt worker check[/cyan] for detailed instructions[/yellow]"
                )
                raise typer.Exit(1)

    except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error for any workflow requirement check failure
        console.print(f"[red]Error checking requirements: {escape(str(e))}[/red]")
        raise typer.Exit(1)


def _load_workflow(workflow_file: Path) -> Optional["Workflow"]:
    """Load workflow definition from file.

    Args:
        workflow_file: Path to workflow YAML file

    Returns:
        Workflow object if loaded successfully, None otherwise
    """
    import yaml

    from worker.workflow_models import Workflow

    try:
        with open(workflow_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            # Fix YAML boolean key issue (on: becomes True)
            if True in data:
                data["on"] = data.pop(True)
            return Workflow(**data)
    except (OSError, yaml.YAMLError, TypeError, ValueError):
        return None


async def _discover_workspace_interactive(
    project_scope: ProjectScope,
) -> Optional[int]:
    """Discover and select workspace dynamically.

    Uses WorkspaceService to fetch accessible workspaces and:
    - Auto-selects if only one workspace exists
    - Prompts for selection if multiple workspaces (interactive mode)
    - Returns first workspace in non-interactive mode

    Args:
        project_scope: The workflow's project scope setting (for logging)

    Returns:
        Selected workspace ID, or None if discovery failed
    """
    from cli.services.workspace_service import WorkspaceService

    console.print("[cyan]Discovering workspaces...[/cyan]")

    try:
        service = WorkspaceService.from_config()
        workspaces = await service.get_accessible_workspaces()

        if not workspaces:
            console.print("[red]No workspaces found for this account[/red]")
            return None

        if len(workspaces) == 1:
            # Auto-select single workspace
            ws = workspaces[0]
            console.print(
                f"[green]✓[/green] Using workspace: {ws.name} ({ws.identifier})"
            )
            return ws.id

        # Multiple workspaces - use interactive selection
        selected = service.select_workspace_interactive(
            workspaces,
            message="Select a workspace for the worker:",
        )

        if selected is None:
            # Non-interactive mode or user cancelled - use first workspace
            ws = workspaces[0]
            console.print(
                f"[green]Using workspace: {ws.name} ({ws.identifier})[/green]"
            )
            return ws.id

        console.print(
            f"[green]✓[/green] Selected workspace: {selected.name} ({selected.identifier})"
        )
        return selected.id

    except Exception as e:  # noqa: BLE001 - Intentionally broad: workspace discovery is best-effort
        console.print(f"[red]Error discovering workspaces: {escape(str(e))}[/red]")
        return None


async def _discover_project_interactive(
    workspace_id: int,
    project_scope: ProjectScope,
) -> Optional[int]:
    """Discover and select project dynamically.

    Uses ProjectService to fetch workspace projects and:
    - Auto-selects if only one project exists
    - Prompts for selection if multiple projects (interactive mode)
    - Returns first project in non-interactive mode

    Only called when project_scope is PROJECT (not WORKSPACE).

    Args:
        workspace_id: The workspace ID to fetch projects from
        project_scope: The workflow's project scope setting

    Returns:
        Selected project ID, or None if discovery failed or skipped
    """
    from cli.services.project_service import ProjectService

    console.print("[cyan]Discovering projects...[/cyan]")

    try:
        service = ProjectService.from_config()
        projects = await service.list_projects(workspace_id)

        if not projects:
            console.print(
                "[yellow]No projects found in workspace. "
                "Worker will operate at workspace level.[/yellow]"
            )
            return None

        if len(projects) == 1:
            # Auto-select single project
            proj = projects[0]
            console.print(f"[green]✓[/green] Using project: {proj.name}")
            return proj.id

        # Multiple projects - use interactive selection
        selected = service.select_project_interactive(
            projects,
            message="Select a project for the worker:",
            allow_create=False,  # Don't allow creating projects during worker start
        )

        if selected is None:
            # Non-interactive mode or user cancelled - use first project
            proj = projects[0]
            console.print(f"[green]Using project: {proj.name}[/green]")
            return proj.id

        console.print(f"[green]✓[/green] Selected project: {selected.name}")
        return selected.id

    except Exception as e:  # noqa: BLE001 - Intentionally broad: project discovery is best-effort
        console.print(
            f"[yellow]Warning: Could not discover projects: {escape(str(e))}[/yellow]"
        )
        console.print("[yellow]Worker will operate at workspace level.[/yellow]")
        return None


def _resolve_coding_agents(
    agents_option: Optional[str],
    skip_detection: bool,
) -> Optional[List[str]]:
    """Resolve coding agents from CLI options or interactive detection.

    Args:
        agents_option: Comma-separated agent list from --agents option
        skip_detection: If True, skip interactive detection

    Returns:
        List of coding agent identifiers, or None to skip agent filtering
    """
    # If explicit agents list provided, use it directly
    if agents_option:
        agent_list = [a.strip() for a in agents_option.split(",") if a.strip()]
        if agent_list:
            console.print(f"[dim]Using specified agents: {', '.join(agent_list)}[/dim]")
            return agent_list

    # If skip_detection is set, return None (no agent filtering)
    if skip_detection:
        console.print("[dim]Agent detection skipped - no agent filtering[/dim]")
        return None

    # Run interactive agent detection
    try:
        from worker.agents import interactive_agent_setup

        console.print("[cyan]Detecting installed coding agents...[/cyan]")
        detected_agents = interactive_agent_setup(console)

        if detected_agents:
            return detected_agents

        # No agents detected but user didn't cancel - continue without filtering
        return None

    except SystemExit:
        # User cancelled or no agents installed
        raise typer.Exit(1)
    except ImportError:
        # Agent detection module not available, continue without filtering
        console.print(
            "[yellow]Warning: Agent detection not available. "
            "Continuing without agent filtering.[/yellow]"
        )
        return None
