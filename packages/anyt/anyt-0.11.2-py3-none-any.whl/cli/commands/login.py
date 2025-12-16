"""Login command for AnyTask CLI."""

import os
from typing import Any

import typer
from rich.panel import Panel

from cli.commands.console import console
from cli.commands.decorators import async_command
from cli.utils.api_key import (
    get_api_key_setup_message,
    mask_api_key,
    validate_api_key_format,
)
from cli.utils.global_config import GlobalAuthConfig
from cli.utils.interactive import confirm, is_interactive, secret_input
from cli.utils.shell import detect_shell
from cli.utils.typer_utils import HelpOnErrorGroup

app = typer.Typer(help="Login to AnyTask", cls=HelpOnErrorGroup)


def get_api_key_with_source() -> tuple[str | None, str]:
    """Get API key from priority chain with source tracking.

    Priority order:
    1. ANYT_API_KEY environment variable
    2. ~/.anyt/auth.json (global config)

    Returns:
        Tuple of (api_key, source) where source is one of:
        - "env": From ANYT_API_KEY environment variable
        - "global": From ~/.anyt/auth.json
        - "none": Not found
    """
    # Priority 1: Environment variable
    api_key = os.getenv("ANYT_API_KEY")
    if api_key:
        return api_key, "env"

    # Priority 2: Global config (~/.anyt/auth.json)
    try:
        api_key = GlobalAuthConfig.get_api_key()
        if api_key:
            return api_key, "global"
    except (OSError, RuntimeError):
        pass

    return None, "none"


@app.command()
@async_command()
async def login(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing global config with environment variable",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output as JSON",
    ),
) -> dict[str, Any] | None:
    """Login to AnyTask using API key.

    Authentication priority:
    1. ANYT_API_KEY environment variable
    2. ~/.anyt/auth.json global config file

    If both exist and differ, uses environment variable.
    Use --force to update global config with environment variable.

    Examples:
        # Login with environment variable
        export ANYT_API_KEY=anyt_agent_...
        anyt login

        # Login with saved config
        anyt login

        # Update saved config with current env var
        anyt login --force
    """
    env_api_key = os.getenv("ANYT_API_KEY")
    global_api_key = GlobalAuthConfig.get_api_key()

    api_key: str | None = None
    source: str = "none"

    # Determine which API key to use
    if env_api_key and global_api_key:
        # Both exist
        if env_api_key == global_api_key:
            api_key = env_api_key
            source = "both"
        else:
            # Different - use env var
            api_key = env_api_key
            source = "env"
            if force:
                GlobalAuthConfig.set_api_key(env_api_key)
                if not json_output:
                    console.print(
                        "[dim]Updated global config with environment variable[/dim]"
                    )
            elif not json_output:
                console.print(
                    "[yellow]Note:[/yellow] Environment variable differs from global config. "
                    "Using environment variable. Use --force to update global config."
                )
    elif env_api_key:
        # Only env var exists
        api_key = env_api_key
        source = "env"
        # Ask if user wants to save to global config
        if not json_output and is_interactive():
            save = confirm(
                message="Save API key to ~/.anyt/auth.json for persistence?",
                default=True,
            )
            if save:
                GlobalAuthConfig.set_api_key(env_api_key)
                console.print("[green]✓[/green] Saved to global config")
    elif global_api_key:
        # Only global config exists
        api_key = global_api_key
        source = "global"
    else:
        # Neither exists - prompt for API key in interactive mode
        if json_output:
            return {
                "success": False,
                "error": {
                    "code": "NO_API_KEY",
                    "message": "No API key found. Set ANYT_API_KEY or run: anyt login interactively",
                },
            }

        if not is_interactive():
            shell_name, config_path = detect_shell()
            console.print(
                Panel(
                    get_api_key_setup_message(shell_name, str(config_path)),
                    title="[yellow]API Key Required[/yellow]",
                    border_style="yellow",
                )
            )
            raise typer.Exit(1)

        # Interactive mode - prompt for API key
        console.print(
            "[cyan]No API key found.[/cyan] Get your API key from "
            "[link=https://app.anyt.dev/settings/api-keys]https://app.anyt.dev/settings/api-keys[/link]"
        )
        console.print()

        try:
            api_key = secret_input(
                message="Paste your API key:",
                instruction="(input is hidden)",
                validate=lambda x: len(x.strip()) > 0 or "API key cannot be empty",
            )
            api_key = api_key.strip()
            source = "prompt"
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled[/yellow]")
            raise typer.Exit(1)

    # Validate format
    if not validate_api_key_format(api_key):
        if json_output:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_FORMAT",
                    "message": "API key format invalid. Must start with 'anyt_agent_' and be >20 chars",
                },
            }
        console.print("[red]✗[/red] Invalid API key format")
        console.print(
            "[dim]API key must start with 'anyt_agent_' and be at least 20 characters[/dim]"
        )
        raise typer.Exit(1)

    # Validate with backend by listing workspaces
    try:
        from cli.client.workspaces import WorkspacesAPIClient

        # Get API URL from env or default
        api_url = os.getenv("ANYT_API_URL", "https://api.anyt.dev")

        client = WorkspacesAPIClient(base_url=api_url, api_key=api_key)
        workspaces = await client.list_workspaces()

        if json_output:
            return {
                "success": True,
                "data": {
                    "workspaces_count": len(workspaces),
                    "source": source,
                    "api_key_masked": mask_api_key(api_key),
                    "api_url": api_url,
                },
            }

        console.print("[green]✓[/green] Login successful!")
        console.print(f"  [dim]API Key:[/dim] {mask_api_key(api_key)}")
        console.print(f"  [dim]Source:[/dim] {source}")
        console.print(f"  [dim]API URL:[/dim] {api_url}")
        console.print(f"  [dim]Workspaces:[/dim] {len(workspaces)} accessible")

        # Save to global config if API key was entered via prompt
        if source == "prompt":
            GlobalAuthConfig.set_api_key(api_key)
            console.print()
            console.print("[green]✓[/green] API key saved to ~/.anyt/auth.json")

        if source == "env" and not GlobalAuthConfig.has_api_key():
            console.print()
            console.print(
                "[dim]Tip: Run 'anyt login --force' to save the API key for future sessions[/dim]"
            )

        return None

    except Exception as e:
        if json_output:
            return {
                "success": False,
                "error": {"code": "AUTH_FAILED", "message": str(e)},
            }
        console.print(f"[red]✗[/red] Authentication failed: {e}")
        raise typer.Exit(1)
