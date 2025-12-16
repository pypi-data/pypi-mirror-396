"""Agent commands for managing coding agent integrations."""

import typer
from typing_extensions import Annotated
from rich.table import Table
from InquirerPy.base.control import Choice

from cli.commands.console import console
from cli.commands.formatters import output_json
from cli.services.agent_service import AgentService, AgentType, AgentInfo
from cli.utils.interactive import select_many, is_interactive, confirm
from cli.utils.typer_utils import HelpOnErrorGroup

app = typer.Typer(
    name="agent",
    help="Manage coding agent integrations (Claude Code, Cursor, Codex, Gemini, etc.)",
    cls=HelpOnErrorGroup,
)


def _select_agents_interactive(
    agents: list[AgentInfo], installed_types: set[str]
) -> list[str]:
    """Show interactive multi-select for agents.

    Args:
        agents: List of available agents
        installed_types: Set of already installed agent types

    Returns:
        List of selected agent type strings
    """
    # Check for TTY
    if not is_interactive():
        console.print(
            "[yellow]Non-interactive mode: Cannot display agent selection[/yellow]"
        )
        return []

    console.print()

    # Build choices for checkbox selection
    choices: list[Choice] = []
    for agent in agents:
        status = " (installed)" if agent.type.value in installed_types else ""
        name = f"{agent.name}{status} - {agent.description}"
        choices.append(Choice(value=agent.type.value, name=name))

    try:
        selected_types: list[str] = select_many(
            choices=choices,
            message="Select agents to install:",
            instruction="(Space to toggle, Enter to confirm)",
        )
    except KeyboardInterrupt:
        console.print("\n[dim]Agent selection cancelled[/dim]")
        return []

    if not selected_types:
        # Default to first agent if none selected
        console.print("[dim]No agents selected, defaulting to first agent[/dim]")
        return [agents[0].type.value]

    return selected_types


def _install_single_agent(
    service: AgentService,
    agent_type: str,
    force: bool,
    json_output: bool,
) -> bool:
    """Install a single agent's commands.

    Returns:
        True if installation succeeded, False otherwise
    """
    agent_info = service.get_agent_info(agent_type)
    if not agent_info:
        return False

    # Check if commands already exist
    if service.check_existing(agent_type) and not force:
        integration = service.get_integration(agent_type)
        if integration:
            existing = integration.get_installed_commands()
            if json_output:
                # In JSON mode with multiple agents, we skip prompts
                return False
            else:
                console.print(
                    f"[yellow]Commands already exist at:[/yellow] {integration.target_path}"
                )
                console.print(f"Existing commands: {', '.join(existing)}")
                console.print()

                # Prompt user
                if confirm("Override existing commands?", default=False):
                    force = True
                else:
                    console.print("[dim]Skipped[/dim]")
                    return False

    # Perform installation
    result = service.install(agent_type, force=force)

    if result.success:
        if not json_output:
            console.print(
                f"[green]✓[/green] Installed {agent_info.name} commands to {result.target_path}"
            )
            console.print()
            console.print("[bold]Installed commands:[/bold]")
            for cmd in result.installed_commands:
                cmd_name = cmd.replace(".md", "")
                console.print(f"  • /{cmd_name}")
            console.print()
        return True
    else:
        if not json_output:
            console.print(f"[red]Error:[/red] {result.message}")
        return False


@app.command("install")
def install_agent(
    agent_type: Annotated[
        str | None,
        typer.Argument(
            help="Agent type to install (e.g., 'claude'). Interactive if omitted."
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force", "-f", help="Override existing commands without prompting"
        ),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Install slash commands for a coding agent.

    Installs AnyTask workflow commands to the agent's commands directory.
    For Claude Code, this installs to .claude/commands/anyt/.

    If no agent type is specified, shows an interactive selection menu.

    Examples:
        anyt agent install           # Interactive selection
        anyt agent install claude    # Install Claude Code commands
        anyt agent install --force   # Override existing commands
    """
    service = AgentService.from_config()

    # Get list of installed agents for display
    statuses = service.list_agents()
    installed_types = {s.agent.type.value for s in statuses if s.installed}

    # If no agent type specified, show interactive selection
    if agent_type is None:
        if json_output:
            output_json(
                {
                    "error": "AgentTypeRequired",
                    "message": "Agent type is required for JSON output mode",
                    "supported_agents": [t.value for t in AgentType],
                },
                success=False,
            )
            raise typer.Exit(1)

        agents = service.get_supported_agents()
        selected_types = _select_agents_interactive(agents, installed_types)

        if not selected_types:
            console.print("[dim]No agents selected[/dim]")
            raise typer.Exit(0)

        # Install selected agents
        results: list[dict[str, object]] = []
        for selected_type in selected_types:
            success = _install_single_agent(service, selected_type, force, json_output)
            agent_info = service.get_agent_info(selected_type)
            if agent_info:
                results.append(
                    {
                        "agent": selected_type,
                        "agent_name": agent_info.name,
                        "success": success,
                    }
                )

        console.print()
        successful = sum(1 for r in results if r["success"])
        console.print(
            f"[green]✓[/green] Installed {successful}/{len(results)} agent(s)"
        )
        return

    # Validate agent type
    agent_info = service.get_agent_info(agent_type)
    if not agent_info:
        supported = ", ".join(t.value for t in AgentType)
        if json_output:
            output_json(
                {
                    "error": "InvalidAgentType",
                    "message": f"Unknown agent type: {agent_type}",
                    "supported_agents": supported.split(", "),
                },
                success=False,
            )
        else:
            console.print(f"[red]Error:[/red] Unknown agent type: {agent_type}")
            console.print(f"Supported agents: [cyan]{supported}[/cyan]")
        raise typer.Exit(1)

    # Check if commands already exist
    if service.check_existing(agent_type) and not force:
        integration = service.get_integration(agent_type)
        if integration:
            existing = integration.get_installed_commands()
            if json_output:
                output_json(
                    {
                        "error": "CommandsExist",
                        "message": f"Commands already exist at {integration.target_path}",
                        "existing_commands": existing,
                        "suggestion": "Use --force to override",
                    },
                    success=False,
                )
                raise typer.Exit(1)
            else:
                console.print(
                    f"[yellow]Commands already exist at:[/yellow] {integration.target_path}"
                )
                console.print(f"Existing commands: {', '.join(existing)}")
                console.print()

                # Prompt user
                if confirm("Override existing commands?", default=False):
                    force = True
                else:
                    console.print("[dim]Installation cancelled[/dim]")
                    raise typer.Exit(0)

    # Perform installation
    result = service.install(agent_type, force=force)

    if result.success:
        if json_output:
            output_json(
                {
                    "agent": agent_type,
                    "agent_name": agent_info.name,
                    "installed_commands": result.installed_commands,
                    "target_path": str(result.target_path),
                    "was_override": result.was_override,
                }
            )
        else:
            console.print(
                f"[green]✓[/green] Installed {agent_info.name} commands to {result.target_path}"
            )
            console.print()
            console.print("[bold]Installed commands:[/bold]")
            for cmd in result.installed_commands:
                cmd_name = cmd.replace(".md", "")
                console.print(f"  • /{cmd_name}")
            console.print()
            console.print(
                f"[dim]Use these commands in {agent_info.name} with /{cmd_name}[/dim]"
            )
    else:
        if json_output:
            output_json(
                {
                    "error": "InstallFailed",
                    "message": result.message,
                },
                success=False,
            )
        else:
            console.print(f"[red]Error:[/red] {result.message}")
        raise typer.Exit(1)


@app.command("uninstall")
def uninstall_agent(
    agent_type: Annotated[
        str,
        typer.Argument(help="Agent type to uninstall (e.g., 'claude')"),
    ],
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Uninstall without prompting"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Uninstall slash commands for a coding agent.

    Removes AnyTask workflow commands from the agent's commands directory.

    Examples:
        anyt agent uninstall claude
        anyt agent uninstall claude --force
    """
    service = AgentService.from_config()

    # Validate agent type
    agent_info = service.get_agent_info(agent_type)
    if not agent_info:
        supported = ", ".join(t.value for t in AgentType)
        if json_output:
            output_json(
                {
                    "error": "InvalidAgentType",
                    "message": f"Unknown agent type: {agent_type}",
                    "supported_agents": supported.split(", "),
                },
                success=False,
            )
        else:
            console.print(f"[red]Error:[/red] Unknown agent type: {agent_type}")
            console.print(f"Supported agents: [cyan]{supported}[/cyan]")
        raise typer.Exit(1)

    # Check if commands exist
    if not service.check_existing(agent_type):
        if json_output:
            output_json(
                {
                    "error": "NotInstalled",
                    "message": f"No {agent_info.name} commands installed",
                },
                success=False,
            )
        else:
            console.print(f"[yellow]No {agent_info.name} commands installed[/yellow]")
        raise typer.Exit(0)

    # Confirm uninstall
    integration = service.get_integration(agent_type)
    if integration and not force and not json_output:
        existing = integration.get_installed_commands()
        console.print(f"[yellow]Commands to remove:[/yellow] {', '.join(existing)}")
        console.print(f"[yellow]Location:[/yellow] {integration.target_path}")
        console.print()

        if not confirm("Remove these commands?", default=False):
            console.print("[dim]Uninstall cancelled[/dim]")
            raise typer.Exit(0)

    # Perform uninstallation
    result = service.uninstall(agent_type)

    if result.success:
        if json_output:
            output_json(
                {
                    "agent": agent_type,
                    "agent_name": agent_info.name,
                    "removed_commands": result.removed_commands,
                }
            )
        else:
            console.print(f"[green]✓[/green] Removed {agent_info.name} commands")
            for cmd in result.removed_commands:
                console.print(f"  • {cmd}")
    else:
        if json_output:
            output_json(
                {
                    "error": "UninstallFailed",
                    "message": result.message,
                },
                success=False,
            )
        else:
            console.print(f"[red]Error:[/red] {result.message}")
        raise typer.Exit(1)


@app.command("list")
def list_agents(
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """List available coding agents and their installation status.

    Examples:
        anyt agent list
        anyt agent list --json
    """
    service = AgentService.from_config()
    statuses = service.list_agents()

    if json_output:
        output_json(
            {
                "agents": [
                    {
                        "type": status.agent.type.value,
                        "name": status.agent.name,
                        "description": status.agent.description,
                        "installed": status.installed,
                        "installed_commands": status.installed_commands,
                        "target_path": str(status.target_path)
                        if status.target_path
                        else None,
                    }
                    for status in statuses
                ]
            }
        )
    else:
        console.print()
        console.print("[bold]Available Coding Agents[/bold]")
        console.print()

        table = Table(show_header=True, box=None, padding=(0, 2))
        table.add_column("Agent", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Commands", style="dim")
        table.add_column("Path", style="dim")

        for status in statuses:
            status_str = (
                "[green]installed[/green]"
                if status.installed
                else "[dim]not installed[/dim]"
            )
            commands_str = (
                ", ".join(status.installed_commands)
                if status.installed_commands
                else "-"
            )
            path_str = str(status.target_path) if status.target_path else "-"

            table.add_row(
                status.agent.name,
                status_str,
                commands_str,
                path_str,
            )

        console.print(table)
        console.print()

        # Show install hint for agents that aren't installed
        not_installed = [s for s in statuses if not s.installed]
        if not_installed:
            console.print("[dim]Install with:[/dim]")
            for status in not_installed:
                console.print(f"  anyt agent install {status.agent.type.value}")
            console.print()
