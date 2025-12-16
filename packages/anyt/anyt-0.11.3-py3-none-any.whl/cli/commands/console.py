"""Shared console instance for CLI output.

This module provides centralized console instances for consistent output
across all CLI commands and services. All CLI components should import
from this module rather than creating their own Console instances.

Usage:
    from cli.commands.console import console
    console.print("[green]Success![/green]")

For error output that should go to stderr:
    from cli.commands.console import stderr_console
    stderr_console.print("[red]Error![/red]")
"""

from rich.console import Console

__all__ = ["console", "stderr_console", "stdout_console"]

# Standard console for normal output to stdout
console = Console()

# Console for errors/warnings/info to stderr
stderr_console = Console(stderr=True)

# Alias for explicit stdout usage
stdout_console = console
