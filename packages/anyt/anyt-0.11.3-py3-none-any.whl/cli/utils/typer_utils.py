"""Custom Typer utilities for enhanced CLI behavior.

This module provides custom Typer components that improve the user experience,
such as showing help automatically when command errors occur.
"""

import sys
from typing import Any

import click
import typer.core


class HelpOnErrorGroup(typer.core.TyperGroup):
    """Custom TyperGroup that shows help when a command error occurs.

    Instead of showing "No such command 'X'. Try 'command --help' for help.",
    this group directly displays the help output, making it easier for users
    to discover available commands without an extra step.
    """

    def resolve_command(
        self, ctx: click.Context, args: list[str]
    ) -> tuple[str | None, click.Command | None, list[str]]:
        """Resolve a command name to a command object.

        Overrides the default behavior to show help instead of just an error
        hint when a command is not found.
        """
        try:
            return super().resolve_command(ctx, args)
        except click.UsageError as e:
            # Check if this is a "No such command" error
            error_message = str(e.format_message())
            if "No such command" in error_message:
                # Show the error message first
                click.echo(click.style(f"Error: {error_message}", fg="red"), err=True)
                click.echo(err=True)

                # Then show the help
                click.echo(ctx.get_help())
                sys.exit(2)
            # Re-raise other usage errors
            raise


def create_typer_app(**kwargs: Any) -> typer.Typer:
    """Create a Typer app that shows help on command errors.

    This is a drop-in replacement for typer.Typer() that uses HelpOnErrorGroup
    to provide better error messages.

    Args:
        **kwargs: All arguments passed to typer.Typer()

    Returns:
        A Typer app configured to show help on command errors.
    """
    # Set the custom class as the default for this app
    kwargs.setdefault("cls", HelpOnErrorGroup)
    return typer.Typer(**kwargs)
