"""Configuration management commands."""

import os
import typer
from rich.prompt import Prompt

from cli.commands.console import console
from cli.utils.api_key import validate_api_key_format, mask_api_key
from cli.utils.global_config import GlobalAuthConfig
from cli.utils.shell import detect_shell
from cli.utils.typer_utils import HelpOnErrorGroup

app = typer.Typer(help="Manage CLI configuration", cls=HelpOnErrorGroup)


@app.command(name="set-api-key")
def set_api_key(
    api_key: str = typer.Option(
        None,
        "--key",
        "-k",
        help="API key to store (will prompt if not provided)",
    ),
) -> None:
    """Store API key in global config file (~/.anyt/auth.json).

    This saves your API key so you don't need to export
    ANYT_API_KEY in every shell session.

    The API key will be automatically loaded by all anyt commands.

    Example:
        anyt config set-api-key --key anyt_agent_...
        anyt config set-api-key  # Interactive prompt
    """
    # If key not provided, prompt for it
    if not api_key:
        console.print()
        console.print("[cyan]Enter your AnyTask API key[/cyan]")
        console.print("(Get your API key from: https://anyt.dev/home/settings)")
        console.print()
        api_key = Prompt.ask("API Key", password=True)

    # Validate API key format
    if not validate_api_key_format(api_key):
        console.print()
        console.print(
            "[red]Error:[/red] Invalid API key format. Expected format: anyt_agent_..."
        )
        raise typer.Exit(1)

    # Store in global config
    try:
        GlobalAuthConfig.set_api_key(api_key)
        masked_key = mask_api_key(api_key)
        console.print()
        console.print(f"[green]✓[/green] API key saved: {masked_key}")
        console.print()
        console.print(
            f"[dim]The API key is now stored in {GlobalAuthConfig.get_config_path()}[/dim]"
        )
        console.print("[dim]It will be automatically used by all anyt commands.[/dim]")
        console.print()

        # Check if ANYT_API_KEY is also set in environment
        if os.getenv("ANYT_API_KEY"):
            console.print(
                "[yellow]Note:[/yellow] ANYT_API_KEY environment variable is also set."
            )
            console.print(
                "[dim]The environment variable will take precedence over saved config.[/dim]"
            )
    except (OSError, RuntimeError, ValueError) as e:
        console.print(f"[red]Error:[/red] Failed to store API key: {e}")
        console.print()
        console.print("[yellow]Alternative:[/yellow] Set environment variable instead:")
        shell_name, config_path = detect_shell()
        console.print(f"  echo 'export ANYT_API_KEY={api_key}' >> {config_path}")
        console.print(f"  source {config_path}")
        raise typer.Exit(1)


@app.command(name="get-api-key")
def get_api_key() -> None:
    """Show currently configured API key (masked).

    Checks both environment variable and global config file.
    """
    env_key = os.getenv("ANYT_API_KEY")
    global_key = GlobalAuthConfig.get_api_key()

    console.print()

    if env_key:
        masked = mask_api_key(env_key)
        console.print(f"[green]Environment variable:[/green] {masked}")
        console.print("[dim](ANYT_API_KEY)[/dim]")
        console.print()

    if global_key:
        masked = mask_api_key(global_key)
        console.print(f"[green]Global config:[/green] {masked}")
        console.print(f"[dim]({GlobalAuthConfig.get_config_path()})[/dim]")
        console.print()

    if not env_key and not global_key:
        console.print("[yellow]No API key configured[/yellow]")
        console.print()
        console.print("Configure your API key:")
        console.print("  [cyan]anyt config set-api-key[/cyan]")
        console.print()
        raise typer.Exit(1)

    if env_key and global_key:
        console.print(
            "[dim]Note: Environment variable takes precedence over global config.[/dim]"
        )


@app.command(name="clear-api-key")
def clear_api_key(
    confirm: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Remove API key from global config file (~/.anyt/auth.json).

    This only removes the API key from the config file.
    If you have ANYT_API_KEY set as an environment variable,
    you'll need to manually remove it from your shell configuration.
    """
    # Check if API key exists in global config
    if not GlobalAuthConfig.has_api_key():
        console.print("[yellow]No API key stored in global config[/yellow]")
        raise typer.Exit(0)

    # Confirm deletion
    if not confirm:
        console.print()
        console.print(
            "[yellow]This will remove your API key from the global config.[/yellow]"
        )
        console.print(
            "You will need to set it again using [cyan]anyt config set-api-key[/cyan]"
        )
        console.print()

        confirm_delete = Prompt.ask("Are you sure?", choices=["y", "N"], default="N")

        if confirm_delete.lower() != "y":
            console.print("Cancelled")
            raise typer.Exit(0)

    # Delete from global config
    deleted = GlobalAuthConfig.delete_api_key()
    if deleted:
        console.print()
        console.print("[green]✓[/green] API key removed from global config")
        console.print()

        # Check if environment variable is still set
        if os.getenv("ANYT_API_KEY"):
            console.print(
                "[yellow]Note:[/yellow] ANYT_API_KEY environment variable is still set."
            )
            console.print("Remove it from your shell configuration if needed:")
            shell_name, config_path = detect_shell()
            console.print(f"  # Edit {config_path}")
            console.print("  # Remove the line: export ANYT_API_KEY=...")
            console.print()
    else:
        console.print("[yellow]No API key was stored[/yellow]")


@app.command(name="status")
def config_status() -> None:
    """Show current configuration status.

    Displays API key sources and workspace configuration.
    """
    from cli.config import WorkspaceConfig, get_effective_api_config

    console.print()
    console.print("[bold cyan]Configuration Status[/bold cyan]")
    console.print("─" * 50)
    console.print()

    # Check API key sources
    env_key = os.getenv("ANYT_API_KEY")
    global_key = GlobalAuthConfig.get_api_key()

    # Show API key status
    console.print("[bold]Authentication:[/bold]")
    if env_key:
        masked = mask_api_key(env_key)
        console.print(f"  Environment: {masked} [green]✓[/green]")
    else:
        console.print("  Environment: [dim]not set[/dim]")

    if global_key:
        masked = mask_api_key(global_key)
        console.print(f"  Global config: {masked} [green]✓[/green]")
    else:
        console.print("  Global config: [dim]not set[/dim]")

    console.print()

    # Show effective config
    effective_config = get_effective_api_config()
    console.print("[bold]Effective Configuration:[/bold]")
    console.print(f"  API URL: {effective_config['api_url']}")

    if effective_config["api_key"]:
        masked = mask_api_key(effective_config["api_key"])
        console.print(f"  API Key: {masked} [green]✓[/green]")
    else:
        console.print("  API Key: [red]not configured[/red]")

    console.print()

    # Show workspace config
    workspace_config = WorkspaceConfig.load()
    if workspace_config:
        console.print("[bold]Workspace:[/bold]")
        console.print(f"  Name: {workspace_config.name}")
        console.print(f"  ID: {workspace_config.workspace_id}")
        if workspace_config.workspace_identifier:
            console.print(f"  Identifier: {workspace_config.workspace_identifier}")
        if workspace_config.current_project_id:
            console.print(f"  Project ID: {workspace_config.current_project_id}")
    else:
        console.print("[bold]Workspace:[/bold] [dim]not initialized[/dim]")

    console.print()
