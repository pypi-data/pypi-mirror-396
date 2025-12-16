"""Command context manager for CLI commands.

Provides centralized authentication and workspace checking with
consistent error handling and debug mode support.
"""

from typing import Optional, cast

import typer

from cli.commands.console import stderr_console
from cli.commands.formatters import OutputManager
from cli.config import WorkspaceConfig, get_effective_api_config
from cli.utils.errors import is_debug_mode


class CommandContext:
    """Shared context for CLI commands with auth and workspace validation.

    This context manager eliminates duplicated authentication and workspace
    checking code across commands. It provides:
    - Centralized authentication validation
    - Centralized workspace config validation
    - Debug mode error handling
    - Consistent, user-friendly error messages

    Example:
        @app.command()
        def create_label(name: str):
            '''Create a label.'''
            from cli.commands.services import ServiceRegistry as services
            with CommandContext(require_auth=True, require_workspace=True) as ctx:
                service = services.get_task_service()
                result = asyncio.run(
                    service.create_task(
                        project_id=ctx.workspace_config.current_project_id,
                        task=TaskCreate(title=name)
                    )
                )
                console.print(f"[green]✓[/green] Created task: {result.identifier}")
    """

    def __init__(
        self,
        require_auth: bool = True,
        require_workspace: bool = False,
        json_output: bool = False,
    ):
        """Initialize command context.

        Args:
            require_auth: Whether to require authentication (ANYT_API_KEY)
            require_workspace: Whether to require workspace config (.anyt/anyt.json)
            json_output: Whether to use JSON output mode (affects error formatting)
        """
        self.require_auth = require_auth
        self.require_workspace = require_workspace
        self.json_output = json_output
        self.api_config: dict[str, str] | None = None
        self.workspace_config: WorkspaceConfig | None = None
        self.output = OutputManager(json_mode=json_output)

    def __enter__(self) -> "CommandContext":
        """Validate context requirements on entry.

        Returns:
            Self for context manager protocol

        Raises:
            typer.Exit: If validation fails (in production mode)
            RuntimeError: If validation fails (in debug mode)
        """
        # Check authentication
        if self.require_auth:
            api_config = get_effective_api_config()
            if not api_config.get("api_key"):
                if is_debug_mode():
                    raise RuntimeError(
                        "ANYT_API_KEY environment variable is required. "
                        "Please set it to your agent API key."
                    )

                # Use OutputManager for consistent error output
                if self.json_output:
                    self.output.error(
                        "Not authenticated. Set ANYT_API_KEY environment variable.",
                        error_code="NOT_AUTHENTICATED",
                    )
                else:
                    stderr_console.print("[red]Error:[/red] Not authenticated")
                    stderr_console.print("\nSet the ANYT_API_KEY environment variable:")
                    stderr_console.print(
                        "  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]"
                    )
                    raise typer.Exit(1)

            # Type narrowing: we know api_key is not None here
            self.api_config = cast(
                dict[str, str],
                {"api_url": api_config["api_url"], "api_key": api_config["api_key"]},
            )

        # Check workspace config
        if self.require_workspace:
            self.workspace_config = WorkspaceConfig.load()

            if not self.workspace_config:
                if is_debug_mode():
                    raise RuntimeError("Not in a workspace directory")

                # Use OutputManager for consistent error output
                if self.json_output:
                    self.output.error(
                        "Not in a workspace directory. Run 'anyt init' first.",
                        error_code="NO_WORKSPACE",
                    )
                else:
                    stderr_console.print(
                        "[red]Error:[/red] Not in a workspace directory"
                    )
                    stderr_console.print("Run [cyan]anyt init[/cyan] first")
                    raise typer.Exit(1)

        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        _exc_tb: Optional[object],
    ) -> bool:
        """Handle cleanup and error formatting.

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            _exc_tb: Exception traceback if an error occurred (unused)

        Returns:
            True to suppress exception (production mode), False to propagate (debug mode)
        """
        if exc_type and not isinstance(exc_val, typer.Exit):
            if is_debug_mode():
                return False  # Let exception propagate with full traceback
            # Production mode: friendly error message to stderr
            stderr_console.print(f"[red]Error:[/red] {exc_val}")
            return True  # Suppress traceback

        return False  # No exception or typer.Exit, proceed normally
