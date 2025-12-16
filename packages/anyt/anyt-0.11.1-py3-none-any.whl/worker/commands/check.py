"""
Worker check command for validating workflow requirements.
"""

import json
from pathlib import Path
from typing import Optional

import typer

from rich.markup import escape

from cli.commands.console import console
from worker.commands.helpers import resolve_workflow_file


def check(
    workflow: Optional[str] = typer.Argument(
        None,
        help="Workflow name to check (if not provided, checks current/default workflow)",
    ),
    workspace_dir: Optional[Path] = typer.Option(
        None,
        "--workspace",
        "-w",
        help="Workspace directory (default: current directory)",
    ),
    workflows_dir: Optional[Path] = typer.Option(
        None,
        "--workflows",
        help="Custom workflows directory (default: .anyt/workflows)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Bypass cache and force fresh checks",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
) -> None:
    """
    Check workflow requirements and validate the environment.

    This command validates all requirements for a workflow (commands, environment
    variables, git context, file system) and displays results with fix instructions.

    Examples:
        anyt worker check                    # Check default workflow
        anyt worker check local_dev          # Check specific workflow
        anyt worker check --force            # Force fresh checks (bypass cache)
        anyt worker check --json             # JSON output for automation
        anyt worker check --workspace /path  # Check in specific workspace
    """
    import yaml

    from worker.commands.workflow_formatters import (
        display_check_results,
        format_check_results_json,
    )
    from worker.services.workflow_requirements import WorkflowRequirementsService
    from worker.workflow_models import Workflow

    workspace = workspace_dir or Path.cwd()

    # Determine workflow to check
    workflow_name = workflow
    if not workflow_name:
        # Use default workflow
        workflow_name = "local_dev"  # Default workflow

    # Resolve workflow file
    try:
        workflow_file = resolve_workflow_file(workflow_name, workspace, workflows_dir)
    except ValueError as e:
        if json_output:
            error_result = {
                "success": False,
                "error": {"code": "WORKFLOW_NOT_FOUND", "message": str(e)},
            }
            console.print(json.dumps(error_result, indent=2))
        else:
            console.print(f"[red]Error: {escape(str(e))}[/red]")
        raise typer.Exit(1)

    # Load workflow definition
    try:
        with open(workflow_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            # Fix YAML boolean key issue (on: becomes True)
            if True in data:
                data["on"] = data.pop(True)
            workflow_obj = Workflow(**data)
    except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error for any workflow parsing failure
        if json_output:
            error_result = {
                "success": False,
                "error": {
                    "code": "WORKFLOW_PARSE_ERROR",
                    "message": f"Failed to parse workflow: {e}",
                },
            }
            console.print(json.dumps(error_result, indent=2))
        else:
            console.print(f"[red]Error parsing workflow: {escape(str(e))}[/red]")
        raise typer.Exit(1)

    # Check if workflow has requirements
    if (
        not workflow_obj.requirements
        or not workflow_obj.requirements.has_requirements()
    ):
        if json_output:
            result = {
                "success": True,
                "data": {
                    "workflow_name": workflow_obj.name,
                    "message": "No requirements defined for this workflow",
                    "checks": [],
                    "summary": {"passed": 0, "failed": 0, "warnings": 0, "total": 0},
                },
            }
            console.print(json.dumps(result, indent=2))
        else:
            console.print()
            console.print(f"[cyan]Workflow:[/cyan] [bold]{workflow_obj.name}[/bold]")
            console.print("[yellow]No requirements defined for this workflow[/yellow]")
            console.print()
        return

    # Run requirement checks
    from cli.utils.platform import run_async

    service = WorkflowRequirementsService(workspace_dir=workspace)
    try:
        results = run_async(
            service.check_requirements(
                requirements=workflow_obj.requirements,
                workflow_name=workflow_obj.name,
                force=force,
            )
        )
    except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error for any requirement check failure
        if json_output:
            error_result = {
                "success": False,
                "error": {
                    "code": "CHECK_ERROR",
                    "message": f"Failed to check requirements: {e}",
                },
            }
            console.print(json.dumps(error_result, indent=2))
        else:
            console.print(f"[red]Error checking requirements: {escape(str(e))}[/red]")
        raise typer.Exit(1)

    # Display results
    if json_output:
        result = format_check_results_json(results)
        console.print(json.dumps(result, indent=2))
    else:
        display_check_results(results)

    # Exit with error if checks failed
    if not results.is_success():
        raise typer.Exit(1)
