"""Sync commands for filesystem-first task management.

This module provides commands to sync tasks between the local filesystem
and the AnyTask API server, enabling any AI tool to work with tasks
by reading local files.
"""

import typer

from cli.utils.typer_utils import HelpOnErrorGroup

from .converters import _task_to_local_meta
from .open import open_task
from .pull import pull
from .push import push

app = typer.Typer(
    name="sync",
    help="Sync tasks between local filesystem and server",
    cls=HelpOnErrorGroup,
)

# Register commands
app.command("pull")(pull)
app.command("push")(push)
app.command("open")(open_task)

# Export for use by other modules
__all__ = [
    "app",
    "pull",
    "push",
    "open_task",
    "_task_to_local_meta",
]
