"""Task commands for AnyTask CLI."""

import typer

from cli.utils.typer_utils import HelpOnErrorGroup

from .crud.create import add_task
from .crud.delete import remove_task
from .crud.read import show_task
from .crud.update import add_note_to_task, edit_task, mark_done
from .dependencies import add_dependency, list_dependencies, remove_dependency
from .list import list_tasks
from .pick import pick_task
from .start import start_task
from .suggest import suggest_tasks
from .unpick import unpick_task

# Import subcommand modules
from cli.commands import sync as sync_commands
from cli.commands.task import plan as plan_commands
from cli.commands.task import pr as pr_commands

# Main task command app
app = typer.Typer(help="Manage tasks", cls=HelpOnErrorGroup)

# Register CRUD commands
app.command("add")(add_task)
app.command("list")(list_tasks)
app.command("show")(show_task)
app.command("edit")(edit_task)
app.command("done")(mark_done)
app.command("note")(add_note_to_task)
app.command("rm")(remove_task)
app.command("pick")(pick_task)
app.command("unpick")(unpick_task)
app.command("start")(start_task)
app.command("suggest")(suggest_tasks)

# Register open command (from sync module)
app.command("open")(sync_commands.open_task)

# Dependency management subcommands
dep_app = typer.Typer(help="Manage task dependencies", cls=HelpOnErrorGroup)
dep_app.command("add")(add_dependency)
dep_app.command("rm")(remove_dependency)
dep_app.command("list")(list_dependencies)

# Add dependency subcommand to main app
app.add_typer(dep_app, name="dep")

# Add plan and pr subcommands
app.add_typer(plan_commands.app, name="plan")
app.add_typer(pr_commands.app, name="pr")
