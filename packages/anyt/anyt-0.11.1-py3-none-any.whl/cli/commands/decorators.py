"""Command decorators for async execution with error handling."""

import asyncio
import functools
from typing import Any, Awaitable, Callable, ParamSpec

import typer

from cli.commands.console import stderr_console
from cli.commands.formatters import OutputManager, output_json
from cli.utils.errors import handle_api_error, is_debug_mode

P = ParamSpec("P")


def async_command(
    json_arg_name: str = "json_output",
    timeout: int | None = None,
) -> Callable[[Callable[P, Awaitable[Any]]], Callable[P, None]]:
    """Decorator to handle async command execution with error handling.

    This decorator provides:
    - Automatic async execution via asyncio.run()
    - Optional timeout support for long-running operations
    - Graceful CTRL+C (KeyboardInterrupt) handling with proper exit code
    - Consistent error handling in production mode
    - Debug mode support (full tracebacks)
    - Automatic JSON output formatting

    Args:
        json_arg_name: Name of the JSON output argument (default: "json_output")
        timeout: Optional timeout in seconds for the command

    Example:
        @app.command()
        @async_command(timeout=30)
        async def list_tasks(status: str, json_output: bool = False):
            from cli.commands.services import ServiceRegistry as services
            service = services.get_task_service()
            tasks = await service.list_tasks(...)

            if json_output:
                return {"items": [t.model_dump(mode="json") for t in tasks]}
            else:
                render_task_table(tasks)

    Returns:
        Decorated function that handles async execution and errors
    """

    def decorator(func: Callable[P, Awaitable[Any]]) -> Callable[P, None]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
            # Extract json_output flag
            json_output = bool(kwargs.get(json_arg_name, False))
            output_mgr = OutputManager(json_mode=json_output)

            async def _run() -> Any:
                try:
                    if timeout:
                        return await asyncio.wait_for(
                            func(*args, **kwargs), timeout=timeout
                        )
                    else:
                        return await func(*args, **kwargs)
                except asyncio.TimeoutError:
                    # Use OutputManager for consistent error handling
                    output_mgr.error(
                        f"Command timed out after {timeout}s",
                        error_code="TIMEOUT",
                        exit_code=1,
                    )
                except typer.Exit:
                    # Let typer.Exit propagate unchanged
                    raise
                except Exception as e:  # noqa: BLE001 - Intentionally broad: universal error handler for commands
                    # Universal error handler for all async commands
                    # In debug mode, propagate the exception for full traceback
                    if is_debug_mode():
                        raise

                    # Production mode - show user-friendly error
                    if json_output:
                        output_mgr.error(
                            str(e),
                            error_code=type(e).__name__.upper(),
                            exit_code=1,
                        )
                    else:
                        handle_api_error(e, json_output=False)

            try:
                # On Windows with Python 3.8+, ProactorEventLoop is the default
                # and supports both HTTP clients (httpx) and subprocesses.
                # We do NOT change to SelectorEventLoop as that breaks subprocesses.
                result = asyncio.run(_run())

                # Auto-format result if provided
                if result is not None and json_output:
                    if isinstance(result, dict):
                        output_json(result)
                    else:
                        output_json({"data": result})

            except KeyboardInterrupt:
                # Handle CTRL+C gracefully
                if not json_output:
                    stderr_console.print("\n[yellow]Cancelled[/yellow]")
                raise typer.Exit(130)  # Standard SIGINT exit code

        return wrapper

    return decorator
