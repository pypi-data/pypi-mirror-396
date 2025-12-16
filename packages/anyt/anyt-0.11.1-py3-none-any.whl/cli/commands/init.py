"""Initialize AnyTask workspace in current directory."""

import os
from datetime import datetime
from pathlib import Path

import typer
from typing_extensions import Annotated
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from InquirerPy.base.control import Choice

from cli.commands.console import console
from cli.config import WorkspaceConfig
from cli.services.agent_service import AgentService, AgentType
from cli.utils.shell import detect_shell
from cli.utils.api_key import (
    validate_api_key_format,
    get_api_key_setup_message,
    get_invalid_api_key_message,
)
from cli.utils.gitignore import ensure_anyt_in_gitignore
from cli.utils.global_config import GlobalAuthConfig
from cli.utils.prompts import select_workspace, select_project
from cli.utils.interactive import select_many, is_interactive


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


def save_api_key_to_storage(api_key: str) -> bool:
    """Save API key to global config (~/.anyt/auth.json).

    Args:
        api_key: The API key to save.

    Returns:
        True if saved successfully, False otherwise.
    """
    try:
        GlobalAuthConfig.set_api_key(api_key)
        return True
    except (OSError, RuntimeError, ValueError) as e:
        console.print(f"[yellow]Warning:[/yellow] Could not save to global config: {e}")
        return False


def select_agents(
    preselected: list[str] | None = None,
    non_interactive: bool = False,
) -> list[str]:
    """Interactive prompt for selecting coding agents to install.

    Args:
        preselected: Pre-selected agent types (skips prompt)
        non_interactive: If True, skip interactive prompt

    Returns:
        List of selected agent type strings, or empty list if skipped
    """
    service = AgentService()
    agents = service.get_supported_agents()
    valid_values = [t.value for t in AgentType]

    # If preselected, validate and return
    if preselected:
        validated = []
        for agent_type in preselected:
            if agent_type in valid_values:
                validated.append(agent_type)
            else:
                console.print(
                    f"[yellow]Warning:[/yellow] Invalid agent type '{agent_type}'. "
                    f"Valid options: {', '.join(valid_values)}"
                )
        return validated

    # Non-interactive mode or non-TTY skips agent selection
    if non_interactive or not is_interactive():
        return []

    # Interactive selection with InquirerPy
    console.print()
    console.print(
        Panel(
            "[bold cyan]Coding Agent Integration[/bold cyan]",
            border_style="cyan",
        )
    )
    console.print()

    # Build choices for checkbox selection
    choices: list[Choice] = [
        Choice(value=agent.type.value, name=f"{agent.name} - {agent.description}")
        for agent in agents
    ]

    try:
        selected_types: list[str] = select_many(
            choices=choices,
            message="Select coding agents to install slash commands for:",
            instruction="(Space to toggle, Enter to confirm, or select none to skip)",
        )
    except KeyboardInterrupt:
        console.print("\n[dim]Skipping agent installation[/dim]")
        return []

    if not selected_types:
        console.print("[dim]Skipping agent installation[/dim]")
        return []

    # Show what was selected
    selected_names = [
        agent.name for agent in agents if agent.type.value in selected_types
    ]
    console.print(f"[green]✓[/green] Selected: {', '.join(selected_names)}")
    return selected_types


def install_selected_agents(
    agent_types: list[str],
    base_path: Path,
) -> list[str]:
    """Install selected agents and return list of successfully installed ones.

    Args:
        agent_types: List of agent type strings to install
        base_path: Base path for installation

    Returns:
        List of successfully installed agent type strings
    """
    if not agent_types:
        return []

    service = AgentService(base_path=base_path)
    installed: list[str] = []

    for agent_type in agent_types:
        result = service.install(agent_type, force=True)
        if result.success:
            agent_info = service.get_agent_info(agent_type)
            if agent_info:
                console.print(
                    f"[green]✓[/green] Installed {agent_info.name} commands to {result.target_path}"
                )
                installed.append(agent_type)
        else:
            console.print(
                f"[yellow]Warning:[/yellow] Failed to install {agent_type}: {result.message}"
            )

    return installed


def display_completion_summary(
    workspace_name: str,
    workspace_identifier: str | None,
    project_name: str | None,
    config_path: Path,
    api_url: str,
    installed_agents: list[str] | None = None,
) -> None:
    """Display completion summary after successful init.

    Args:
        workspace_name: Name of the selected workspace
        workspace_identifier: Workspace identifier (e.g., DEV, PROJ)
        project_name: Name of the selected project (if any)
        config_path: Path to saved config file
        api_url: API URL being used
        installed_agents: List of installed agent types (e.g., ["claude", "cursor"])
    """
    console.print()
    console.print("━" * 70)
    console.print("[green]✓ Initialization Complete![/green]")
    console.print("━" * 70)
    console.print()

    console.print(f"Configuration saved to: [cyan]{config_path}[/cyan]")
    console.print()

    # Setup summary table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="dim")
    table.add_column("Value", style="white")

    # Format workspace display
    workspace_display = workspace_name
    if workspace_identifier:
        workspace_display = f"{workspace_name} ({workspace_identifier})"

    table.add_row("Workspace:", workspace_display)
    if project_name:
        table.add_row("Project:", project_name)
    table.add_row("API URL:", api_url)
    if installed_agents:
        # Get agent names from the service
        service = AgentService()
        agent_names = []
        for agent_type in installed_agents:
            agent_info = service.get_agent_info(agent_type)
            if agent_info:
                agent_names.append(agent_info.name)
            else:
                agent_names.append(agent_type)
        table.add_row("Installed Agents:", ", ".join(agent_names))
    table.add_row("Config directory:", str(config_path.parent))

    console.print(table)
    console.print()

    # Next steps
    console.print("[bold]Next Steps:[/bold]")
    console.print()
    console.print("  1. View your tasks:       [cyan]anyt task list[/cyan]")
    console.print('  2. Create a task:         [cyan]anyt task add "Task title"[/cyan]')
    console.print(
        f"  3. Pick a task to work:   [cyan]anyt task pick {workspace_identifier or 'WORK'}-1[/cyan]"
    )
    console.print()
    console.print(
        "Need help? Run [cyan]anyt --help[/cyan] or visit [dim]https://docs.anyt.dev[/dim]"
    )
    console.print()


def init(
    workspace_id: Annotated[
        int | None,
        typer.Option("--workspace-id", "-w", help="Workspace ID to link to"),
    ] = None,
    workspace_name: Annotated[
        str | None,
        typer.Option("--workspace-name", "-n", help="Workspace name (optional)"),
    ] = None,
    identifier: Annotated[
        str | None,
        typer.Option(
            "--identifier", "-i", help="Workspace identifier (e.g., DEV, PROJ)"
        ),
    ] = None,
    project_id: Annotated[
        int | None,
        typer.Option("--project-id", "-p", help="Project ID to use"),
    ] = None,
    directory: Annotated[
        Path | None,
        typer.Option("--dir", "-d", help="Directory to initialize (default: current)"),
    ] = None,
    agents: Annotated[
        str | None,
        typer.Option(
            "--agents",
            help="Comma-separated list of agents to install (e.g., 'claude,codex'). "
            "Available: claude, codex, gemini. Prompts interactively if not specified.",
        ),
    ] = None,
    dev: Annotated[
        bool,
        typer.Option("--dev", help="Use development API (http://localhost:8000)"),
    ] = False,
    non_interactive: Annotated[
        bool,
        typer.Option(
            "--non-interactive",
            "-y",
            help="Non-interactive mode: auto-select first workspace/project",
        ),
    ] = False,
) -> None:
    """Initialize AnyTask in the current directory.

    Requires ANYT_API_KEY environment variable to be set.
    Creates .anyt/ directory structure and anyt.json configuration.

    Examples:
        # Interactive mode (default)
        anyt init

        # With specific agents
        anyt init --agents claude,codex

        # Non-interactive with auto-selection
        anyt init --non-interactive
        anyt init -y

        # Specify workspace and project explicitly
        anyt init --workspace-id 101 --project-id 5

        # Non-interactive with explicit workspace
        anyt init -y --workspace-id 101

        # CI/CD usage
        export ANYT_API_KEY=anyt_agent_...
        anyt init --non-interactive --workspace-id 101 --project-id 5

        # Development API
        anyt init --dev
    """
    try:
        # Show welcome message
        console.print()
        console.print(
            Panel(
                "[bold cyan]Welcome to AnyTask CLI![/bold cyan]\n\n"
                "Let's get you set up with a workspace.",
                border_style="cyan",
            )
        )
        console.print()

        # Determine target directory
        target_dir = directory or Path.cwd()
        target_dir = target_dir.resolve()

        # Create .anyt directory if it doesn't exist
        anyt_dir = target_dir / ".anyt"
        if not anyt_dir.exists():
            anyt_dir.mkdir(parents=True)
            console.print("[green]✓[/green] Created .anyt/ directory")
        else:
            console.print("[dim].anyt/ directory already exists[/dim]")

        # Create subdirectories
        subdirs = ["workflows", "tasks"]
        for subdir in subdirs:
            subdir_path = anyt_dir / subdir
            if not subdir_path.exists():
                subdir_path.mkdir(parents=True)
                console.print(f"[green]✓[/green] Created .anyt/{subdir}/ directory")

        # Add .anyt to .gitignore if this is a git repository
        gitignore_updated, gitignore_message = ensure_anyt_in_gitignore(target_dir)
        if gitignore_updated:
            console.print(f"[green]✓[/green] {gitignore_message}")
        elif "already" in gitignore_message:
            console.print(f"[dim]{gitignore_message}[/dim]")
        # If not a git repo, we stay silent (no message needed)

        # Check if workspace config already exists
        existing_config = WorkspaceConfig.load(target_dir)
        if existing_config:
            console.print(
                f"[yellow]Warning:[/yellow] Workspace config already exists: {existing_config.name}"
            )
            console.print(f"Workspace ID: {existing_config.workspace_id}")
            if existing_config.workspace_identifier:
                console.print(f"Identifier: {existing_config.workspace_identifier}")

            if non_interactive:
                console.print(
                    "[yellow]Non-interactive mode: Skipping existing configuration[/yellow]"
                )
                console.print("[green]✓[/green] Using existing workspace configuration")
                raise typer.Exit(0)

            reset = Prompt.ask(
                "Do you want to reset it?", choices=["y", "N"], default="N"
            )

            if reset.lower() != "y":
                console.print("[green]✓[/green] Using existing workspace configuration")
                raise typer.Exit(0)

        # Get API key from priority chain
        api_key, api_key_source = get_api_key_with_source()

        if not api_key:
            console.print()
            console.print(
                Panel(
                    "[bold yellow]Step 1: Authentication[/bold yellow]",
                    border_style="yellow",
                )
            )
            console.print()

            # Check if interactive mode is available
            if non_interactive or not is_interactive():
                # Non-interactive mode with no API key - fail with instructions
                shell_name, config_path = detect_shell()
                setup_message = get_api_key_setup_message(shell_name, str(config_path))
                console.print(setup_message)
                console.print()
                raise typer.Exit(1)

            # Interactive mode - prompt for API key
            console.print(
                "[cyan]No API key found in environment or global config.[/cyan]"
            )
            console.print()
            console.print(
                "Get your API key from: [link]https://anyt.dev/home/settings/api-keys[/link]"
            )
            console.print()

            api_key = Prompt.ask("Enter your API key", password=True)

            if not api_key or not api_key.strip():
                console.print("[red]Error:[/red] API key cannot be empty")
                raise typer.Exit(1)

            api_key_source = "interactive"

        # Validate API key format
        if not validate_api_key_format(api_key):
            console.print()
            error_message = get_invalid_api_key_message(api_key)
            console.print(error_message)
            console.print()
            raise typer.Exit(1)

        # Display source of API key
        source_display = {
            "env": "environment variable (ANYT_API_KEY)",
            "global": f"global config ({GlobalAuthConfig.get_config_path()})",
            "interactive": "user input",
        }
        console.print(
            f"[green]✓[/green] API key loaded from {source_display.get(api_key_source, 'unknown')}"
        )

        # Determine API URL
        # Priority: ANYT_API_URL env var > --dev flag > production default
        api_url = os.getenv("ANYT_API_URL")
        if not api_url:
            api_url = "http://localhost:8000" if dev else "https://api.anyt.dev"

        # If workspace_id is provided, create workspace config manually
        if workspace_id:
            # Parse agents from comma-separated string
            preselected_agents = None
            if agents:
                preselected_agents = [a.strip() for a in agents.split(",") if a.strip()]

            # Agent selection
            selected_agents = select_agents(
                preselected=preselected_agents, non_interactive=non_interactive
            )

            ws_config = WorkspaceConfig(
                workspace_id=workspace_id,
                name=workspace_name or f"Workspace {workspace_id}",
                api_url=api_url,
                workspace_identifier=identifier,
                current_project_id=None,
                installed_agents=selected_agents if selected_agents else None,
                last_sync=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            ws_config.save(target_dir)

            console.print(f"[green]✓[/green] Linked to workspace ID {workspace_id}")
            console.print(
                f"[green]✓[/green] Saved config to {target_dir}/.anyt/anyt.json"
            )

            # Install selected agents
            installed_agents = install_selected_agents(selected_agents, target_dir)

            # Display completion summary
            display_completion_summary(
                workspace_name=ws_config.name,
                workspace_identifier=ws_config.workspace_identifier,
                project_name=None,  # No project when using manual workspace_id
                config_path=target_dir / ".anyt" / "anyt.json",
                api_url=api_url,
                installed_agents=installed_agents if installed_agents else None,
            )
        else:
            # API key is set - automatically fetch and setup workspace
            console.print(
                "[cyan]ANYT_API_KEY detected - setting up workspace...[/cyan]"
            )

            async def setup_workspace() -> None:
                try:
                    # Initialize API clients directly
                    from cli.client.workspaces import WorkspacesAPIClient
                    from cli.client.projects import ProjectsAPIClient

                    ws_client = WorkspacesAPIClient(base_url=api_url, api_key=api_key)
                    proj_client = ProjectsAPIClient(base_url=api_url, api_key=api_key)

                    # Fetch available workspaces
                    console.print()
                    console.print("[green]✓[/green] Authenticated successfully")
                    console.print("Fetching accessible workspaces...")
                    workspaces = await ws_client.list_workspaces()

                    if not workspaces:
                        console.print(
                            "[red]Error:[/red] No accessible workspaces found for this API key"
                        )
                        console.print(
                            "\nAPI keys require at least one workspace to be created first."
                        )
                        console.print(
                            "Please create a workspace using the web interface at [cyan]https://anyt.dev[/cyan]"
                        )
                        raise typer.Exit(1)

                    # Interactive workspace selection
                    workspace = select_workspace(
                        workspaces,
                        preselected_id=None,  # workspace_id already handled above
                        non_interactive=non_interactive,
                    )

                    # Interactive project selection
                    console.print("Fetching projects...")
                    try:
                        # Fetch existing projects
                        projects = await proj_client.list_projects(workspace.id)

                        # Interactive project selection
                        selected_project = await select_project(
                            projects,
                            preselected_id=project_id,
                            non_interactive=non_interactive,
                            workspace_id=workspace.id,
                            workspace_identifier=workspace.identifier,
                            proj_client=proj_client,
                        )

                        # Create default project if none exist
                        if selected_project is None:
                            console.print(
                                "[yellow]No projects found in workspace.[/yellow]"
                            )
                            console.print(
                                f"Creating default project: [cyan]{workspace.name}[/cyan]..."
                            )

                            from cli.models.project import ProjectCreate

                            selected_project = await proj_client.create_project(
                                workspace.id,
                                ProjectCreate(
                                    name=workspace.name,
                                    description="Default project",
                                ),
                            )
                            console.print(
                                f"[green]✓[/green] Created project: {selected_project.name}"
                            )

                        current_project_id = selected_project.id

                    except Exception as e:  # noqa: BLE001 - Intentionally broad: project setup is optional
                        # Project setup is optional; continue without project on any error
                        console.print(
                            f"[yellow]Warning:[/yellow] Could not fetch or create project: {e}"
                        )
                        current_project_id = None
                        selected_project = None

                    # Parse agents from comma-separated string
                    preselected_agents = None
                    if agents:
                        preselected_agents = [
                            a.strip() for a in agents.split(",") if a.strip()
                        ]

                    # Agent selection
                    selected_agents = select_agents(
                        preselected=preselected_agents, non_interactive=non_interactive
                    )

                    # Create and save workspace config (no api_key stored)
                    ws_config = WorkspaceConfig(
                        workspace_id=workspace.id,
                        name=workspace.name,
                        api_url=api_url,
                        workspace_identifier=workspace.identifier,
                        current_project_id=current_project_id,
                        installed_agents=selected_agents if selected_agents else None,
                        last_sync=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    )
                    ws_config.save(target_dir)

                    console.print(
                        f"[green]✓[/green] Saved config to {target_dir}/.anyt/anyt.json"
                    )

                    # Install selected agents
                    installed_agents = install_selected_agents(
                        selected_agents, target_dir
                    )

                    # Offer to save API key to persistent storage
                    # Only prompt if key came from env var or interactive input
                    if not non_interactive and api_key_source in ("env", "interactive"):
                        # Check if already saved to global config
                        if not GlobalAuthConfig.has_api_key():
                            console.print()
                            console.print(
                                "[cyan]Save API key for future sessions?[/cyan]"
                            )
                            console.print(
                                f"[dim]This will save your API key to {GlobalAuthConfig.get_config_path()}[/dim]"
                            )
                            console.print()

                            save_key = Prompt.ask(
                                "Save to persistent storage?",
                                choices=["y", "N"],
                                default="y",
                            )

                            if save_key.lower() == "y":
                                saved = save_api_key_to_storage(api_key)
                                if saved:
                                    console.print(
                                        f"[green]✓[/green] API key saved to {GlobalAuthConfig.get_config_path()}"
                                    )
                                else:
                                    console.print(
                                        "[yellow]Warning:[/yellow] Could not save API key to persistent storage"
                                    )

                    # Display completion summary
                    display_completion_summary(
                        workspace_name=workspace.name,
                        workspace_identifier=workspace.identifier,
                        project_name=selected_project.name
                        if selected_project
                        else None,
                        config_path=target_dir / ".anyt" / "anyt.json",
                        api_url=api_url,
                        installed_agents=installed_agents if installed_agents else None,
                    )

                except Exception as e:  # noqa: BLE001 - Intentionally broad: top-level error handler
                    # Top-level error handler for workspace setup
                    if not isinstance(e, typer.Exit):
                        console.print(
                            f"[red]Error:[/red] Failed to setup workspace: {e}"
                        )
                        raise typer.Exit(1)
                    raise

            from cli.utils.platform import run_async

            run_async(setup_workspace())

    except Exception as e:  # noqa: BLE001 - Intentionally broad: top-level error handler
        # Top-level error handler for init command
        if not isinstance(e, typer.Exit):
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        raise  # Re-raise typer.Exit to preserve exit code
