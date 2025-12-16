"""Self-update commands for the CLI."""

import typer
from typing_extensions import Annotated

from cli.commands.console import console
from cli.commands.formatters import output_json
from cli.services.update_service import InstallMethod, UpdateService
from cli.utils.typer_utils import HelpOnErrorGroup


app = typer.Typer(name="self", help="Manage the CLI installation", cls=HelpOnErrorGroup)


def _get_service() -> UpdateService:
    """Get the update service instance."""
    return UpdateService()


@app.command("check")
def check(
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Check if a newer version is available.

    Queries PyPI for the latest version and compares with the installed version.

    Examples:
        anyt self check          # Check for updates
        anyt self check --json   # Machine-readable output
    """
    from cli.utils.platform import run_async

    service = _get_service()
    version_info = run_async(service.check_version())

    if json_output:
        output_json(
            {
                "current_version": version_info.current,
                "latest_version": version_info.latest,
                "update_available": version_info.update_available,
                "error": version_info.error,
            }
        )
        return

    # Display current version
    console.print(f"Installed: [cyan]{version_info.current}[/cyan]")

    if version_info.error:
        console.print(f"[yellow]Warning:[/yellow] {version_info.error}")
        return

    console.print(f"Latest:    [cyan]{version_info.latest}[/cyan]")

    if version_info.update_available:
        console.print()
        console.print("[green]Update available![/green]")
        console.print("Run [cyan]anyt self update[/cyan] to upgrade.")
    else:
        console.print()
        console.print("[green]You are up to date.[/green]")


@app.command("update")
def update(
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Force reinstall even if up to date"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Update to the latest version.

    Detects the installation method (uv, pipx, or pip) and runs the
    appropriate upgrade command.

    Examples:
        anyt self update          # Upgrade to latest
        anyt self update --force  # Force reinstall
        anyt self update --json   # Machine-readable output
    """
    from cli.utils.platform import run_async

    service = _get_service()

    # Check version first
    version_info = run_async(service.check_version())
    install_info = service.get_install_info()

    if json_output:
        # Check if update needed
        if not force and not version_info.update_available:
            output_json(
                {
                    "updated": False,
                    "current_version": version_info.current,
                    "latest_version": version_info.latest,
                    "message": "Already up to date",
                    "install_method": install_info.method.value,
                }
            )
            return

        # Run update
        success, message = service.run_upgrade(install_info.method, force=force)
        output_json(
            {
                "updated": success,
                "current_version": version_info.current,
                "latest_version": version_info.latest,
                "install_method": install_info.method.value,
                "message": message,
            },
            success=success,
        )
        if not success:
            raise typer.Exit(1)
        return

    # Display version info
    console.print(f"Installed: [cyan]{version_info.current}[/cyan]")

    if version_info.latest:
        console.print(f"Latest:    [cyan]{version_info.latest}[/cyan]")

    if version_info.error:
        console.print(f"[yellow]Warning:[/yellow] {version_info.error}")

    # Check if update needed
    if not force and not version_info.update_available:
        console.print()
        console.print("[green]Already up to date.[/green]")
        return

    # Detect install method
    console.print()
    console.print(f"Install method: [blue]{install_info.method.value}[/blue]")

    if install_info.method == InstallMethod.UNKNOWN:
        console.print()
        console.print("[red]Cannot detect installation method.[/red]")
        console.print("Please update manually using one of:")
        console.print("  [cyan]uv tool upgrade anyt[/cyan]")
        console.print("  [cyan]pipx upgrade anyt[/cyan]")
        console.print("  [cyan]pip install --upgrade anyt[/cyan]")
        raise typer.Exit(1)

    # Get and show the command
    command = service.get_upgrade_command(install_info.method, force=force)
    if command:
        cmd_str = " ".join(command)
        console.print(f"Running: [dim]{cmd_str}[/dim]")

    console.print()

    # Run upgrade
    success, message = service.run_upgrade(install_info.method, force=force)

    if success:
        console.print("[green]Update completed successfully.[/green]")
        # Get new version (will be the old version in this process, but shows intent)
        if version_info.latest:
            console.print(f"Updated to version [cyan]{version_info.latest}[/cyan]")
    else:
        console.print(f"[red]Update failed:[/red] {message}")
        raise typer.Exit(1)


@app.command("info")
def info(
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Show installation details.

    Displays the current version, installation method, executable path,
    and Python version.

    Examples:
        anyt self info          # Show installation details
        anyt self info --json   # Machine-readable output
    """
    service = _get_service()
    install_info = service.get_install_info()
    current_version = service.get_current_version()

    if json_output:
        output_json(
            {
                "version": current_version,
                "install_method": install_info.method.value,
                "executable_path": install_info.executable_path,
                "python_version": install_info.python_version,
            }
        )
        return

    console.print()
    console.print(f"Version:     [cyan]{current_version}[/cyan]")
    console.print(f"Install:     [blue]{install_info.method.value}[/blue]")

    if install_info.executable_path:
        console.print(f"Location:    [dim]{install_info.executable_path}[/dim]")
    else:
        console.print("Location:    [dim]not found in PATH[/dim]")

    console.print(f"Python:      [dim]{install_info.python_version}[/dim]")
    console.print()
