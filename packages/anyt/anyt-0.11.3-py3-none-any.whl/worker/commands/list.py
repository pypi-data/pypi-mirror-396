"""
Worker list and validate workflow commands.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from rich.markup import escape

from cli.commands.console import console
from worker.workflows import BUILT_IN_WORKFLOWS


def list_workflows(
    workflows_dir: Optional[Path] = typer.Option(
        None,
        "--workflows",
        help="Workflows directory (default: .anyt/workflows)",
    ),
    show_requirements: bool = typer.Option(
        False,
        "--show-requirements",
        "-r",
        help="Show detailed requirements for each workflow",
    ),
) -> None:
    """List available workflows with their requirements.

    This command displays all workflows found in the workflows directory,
    including both custom workflows and built-in workflows.

    Examples:
        anyt worker list                          # List workflows
        anyt worker list --show-requirements      # Show detailed requirements
        anyt worker list --workflows /custom/path # Use custom directory
    """
    from worker.services.workflow_manifest import WorkflowManifestLoader

    workflows_path = workflows_dir or Path.cwd() / ".anyt" / "workflows"

    # Show built-in workflows
    console.print()
    console.print("[bold cyan]Built-in Workflows:[/bold cyan]")
    console.print()

    builtin_table = Table(show_header=True, header_style="bold cyan")
    builtin_table.add_column("Name", style="cyan", width=25)
    builtin_table.add_column("Description", style="white")

    workflow_descriptions = {
        "local_dev": "Quick iterations on current branch (no branch management)",
        "remote_dev": "Clone remote repo, implement task, create PR (for linked GitHub repos)",
    }

    for workflow_name in sorted(BUILT_IN_WORKFLOWS):
        description = workflow_descriptions.get(workflow_name, "")
        builtin_table.add_row(workflow_name, description)

    console.print(builtin_table)
    console.print()

    # Check for custom workflows
    if not workflows_path.exists():
        console.print(
            f"[dim]No custom workflows directory found at: {workflows_path}[/dim]"
        )
        console.print(
            "[dim]Create .anyt/workflows/ directory to add custom workflows[/dim]"
        )
        return

    # Load custom workflows using manifest loader
    loader = WorkflowManifestLoader(workflows_dir=workflows_path)
    workflow_names = loader.list_workflows()

    if not workflow_names:
        console.print(f"[dim]No custom workflows found in: {workflows_path}[/dim]")
        return

    console.print("[bold cyan]Custom Workflows:[/bold cyan]")
    console.print()

    # Display custom workflows
    for workflow_name in workflow_names:
        try:
            manifest = loader.load(workflow_name)

            # Basic info
            console.print(f"[cyan]* {manifest.name}[/cyan]")
            console.print(f"  [dim]{manifest.description}[/dim]")
            console.print(f"  [dim]Version: {manifest.version}[/dim]")

            # Show requirements if requested
            if show_requirements and manifest.requirements.has_requirements():
                req_count = manifest.requirements.count_requirements()
                console.print(f"  [yellow]Requirements ({req_count}):[/yellow]")

                if manifest.requirements.commands:
                    console.print("    Commands:")
                    for cmd in manifest.requirements.commands:
                        req_mark = "✓" if cmd.required else "○"
                        console.print(f"      {req_mark} {cmd.name}")

                if manifest.requirements.env_vars:
                    console.print("    Environment Variables:")
                    for env in manifest.requirements.env_vars:
                        req_mark = "✓" if env.required else "○"
                        console.print(f"      {req_mark} {env.name}")

                if manifest.requirements.git_context:
                    console.print("    Git Context:")
                    for ctx in manifest.requirements.git_context:
                        req_mark = "✓" if ctx.required else "○"
                        console.print(f"      {req_mark} {ctx.context_type.value}")

            console.print()

        except Exception as e:  # noqa: BLE001 - Intentionally broad: gracefully handle any workflow loading failure and continue with other workflows
            console.print(
                f"[red]✗ Error loading workflow '{escape(workflow_name)}': {escape(str(e))}[/red]"
            )
            console.print()


def validate_workflow(
    workflow_file: Path = typer.Argument(..., help="Workflow file to validate"),
) -> None:
    """Validate a workflow definition."""
    import yaml
    from pydantic import ValidationError

    from worker.workflow_models import Workflow

    if not workflow_file.exists():
        console.print(f"[red]Error: Workflow file not found: {workflow_file}[/red]")
        raise typer.Exit(1)

    try:
        with open(workflow_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        workflow = Workflow(**data)

        console.print(f"[green]✓ Workflow is valid:[/green] {workflow.name}")
        console.print(f"  Description: {workflow.description or 'N/A'}")
        console.print(f"  Jobs: {len(workflow.jobs)}")
        for job_name, job in workflow.jobs.items():
            console.print(f"    - {job.name}: {len(job.steps)} steps")

    except ValidationError as e:
        console.print("[red]✗ Workflow validation failed:[/red]")
        console.print(e)
        raise typer.Exit(1)
    except Exception as e:  # noqa: BLE001 - Intentionally broad: display user-friendly error for any workflow validation failure
        console.print(f"[red]Error: {escape(str(e))}[/red]")
        raise typer.Exit(1)
