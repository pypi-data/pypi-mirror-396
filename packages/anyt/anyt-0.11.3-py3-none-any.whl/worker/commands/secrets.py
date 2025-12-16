"""
Secret management commands for worker workflows.
"""

from typing import Optional

import typer
from keyring.errors import KeyringError

from cli.commands.console import console
from cli.utils.typer_utils import HelpOnErrorGroup
from worker.secrets import SecretsManager

secret_app = typer.Typer(help="Manage workflow secrets", cls=HelpOnErrorGroup)


@secret_app.command("set")
def secret_set(
    name: str = typer.Argument(..., help="Secret name (e.g., API_KEY)"),
    value: Optional[str] = typer.Option(
        None, "--value", "-v", help="Secret value (or will prompt)"
    ),
) -> None:
    """
    Store a secret securely in the system keyring.

    If value is not provided, you will be prompted to enter it securely.

    Example:
        anyt worker secret set PRODUCTION_API_KEY --value abc123
        anyt worker secret set DB_PASSWORD  # Will prompt
    """
    try:
        manager = SecretsManager()

        # Prompt for value if not provided
        if value is None:
            value = typer.prompt(f"Enter value for secret '{name}'", hide_input=True)

        # Value is guaranteed to be a string at this point (either provided or from prompt)
        assert value is not None
        manager.set_secret(name, value)
        console.print(f"[green]✓ Secret '{name}' stored successfully[/green]")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except KeyringError as e:
        console.print(f"[red]Keyring error: {e}[/red]")
        raise typer.Exit(1)


@secret_app.command("get")
def secret_get(
    name: str = typer.Argument(..., help="Secret name to retrieve"),
    show: bool = typer.Option(False, "--show", help="Show the secret value"),
) -> None:
    """
    Retrieve a secret from the keyring.

    By default, the secret value is masked. Use --show to display it.

    Example:
        anyt worker secret get API_KEY
        anyt worker secret get API_KEY --show
    """
    try:
        manager = SecretsManager()
        value = manager.get_secret(name)

        if value is None:
            console.print(f"[yellow]Secret '{name}' not found[/yellow]")
            raise typer.Exit(1)

        if show:
            console.print(f"[cyan]{name}:[/cyan] {value}")
        else:
            masked = manager.mask_secret(value)
            console.print(f"[cyan]{name}:[/cyan] {masked}")
            console.print("[dim]Use --show to display the full value[/dim]")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except KeyringError as e:
        console.print(f"[red]Keyring error: {e}[/red]")
        raise typer.Exit(1)


@secret_app.command("delete")
def secret_delete(
    name: str = typer.Argument(..., help="Secret name to delete"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """
    Delete a secret from the keyring.

    Example:
        anyt worker secret delete OLD_API_KEY
        anyt worker secret delete OLD_API_KEY --yes
    """
    try:
        manager = SecretsManager()

        # Check if secret exists
        if manager.get_secret(name) is None:
            console.print(f"[yellow]Secret '{name}' not found[/yellow]")
            raise typer.Exit(1)

        # Confirm deletion
        if not yes:
            confirm = typer.confirm(f"Delete secret '{name}'?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                return

        manager.delete_secret(name)
        console.print(f"[green]✓ Secret '{name}' deleted[/green]")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except KeyringError as e:
        console.print(f"[red]Keyring error: {e}[/red]")
        raise typer.Exit(1)


@secret_app.command("test")
def secret_test(
    text: str = typer.Argument(..., help="Text with secret placeholders to test"),
) -> None:
    r"""
    Test secret interpolation with a sample text.

    This is useful for verifying your secrets are configured correctly.

    Example:
        anyt worker secret test "API_KEY=\${{ secrets.API_KEY }}"
    """
    try:
        manager = SecretsManager()
        result = manager.interpolate_secrets(text)

        console.print("[green]✓ Interpolation successful[/green]")
        console.print(f"[cyan]Input:[/cyan]  {text}")
        console.print(f"[cyan]Output:[/cyan] {result}")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except KeyringError as e:
        console.print(f"[red]Keyring error: {e}[/red]")
        raise typer.Exit(1)
