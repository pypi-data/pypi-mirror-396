"""
Worker commands for running automated task processing.
"""

import asyncio  # Re-exported for test patch compatibility
from pathlib import Path  # Re-exported for test patch compatibility

import typer

from worker.commands.check import check
from worker.commands.helpers import resolve_workflow_file
from worker.commands.list import list_workflows, validate_workflow
from worker.commands.secrets import secret_app
from worker.commands.start import start
from cli.utils.typer_utils import HelpOnErrorGroup
from worker.coordinator import (
    TaskCoordinator,
)  # Re-exported for test patch compatibility

app = typer.Typer(help="Automated task worker commands", cls=HelpOnErrorGroup)

# Add secret subcommand
app.add_typer(secret_app, name="secret")

# Register commands
app.command()(start)
app.command("list-workflows")(list_workflows)
app.command("validate-workflow")(validate_workflow)
app.command()(check)

__all__ = ["app", "resolve_workflow_file", "TaskCoordinator", "asyncio", "Path"]
