"""Reusable output formatters for CLI commands."""

import json
from typing import Any, Callable, Optional, Protocol, TypeVar

import typer
from rich.console import Console
from rich.table import Table

from cli.commands.console import (
    console as _default_console,
    stderr_console,
    stdout_console,
)
from cli.schemas.json_output import (
    error_response,
    success_data_response,
    success_list_response,
    success_message_response,
)

T = TypeVar("T")

# Re-export console for backward compatibility
console = _default_console


def output_json(data: dict[str, Any], success: bool = True) -> None:
    """Output data as JSON to stdout.

    DEPRECATED: Use output_json_data() or output_json_list() instead for consistent schema.

    Args:
        data: The data to output as JSON
        success: Whether this is a success response (affects structure)
    """
    output: dict[str, Any]
    if success:
        output = {"success": True, "data": data}
    else:
        output = {"success": False, **data}

    print(json.dumps(output, indent=2))


def output_json_data(data: Any) -> None:
    """Output single item as JSON using standard schema.

    Args:
        data: Pydantic model or dict to output

    Example:
        >>> task = Task(...)
        >>> output_json_data(task)
        {"success": true, "data": {...}}
    """
    response = success_data_response(data)
    print(json.dumps(response, indent=2))


def output_json_list(
    items: list[Any],
    total: Optional[int] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> None:
    """Output list of items as JSON using standard schema.

    Args:
        items: List of Pydantic models or dicts
        total: Total number of items (for pagination)
        page: Current page number
        page_size: Items per page

    Example:
        >>> tasks = [Task(...), Task(...)]
        >>> output_json_list(tasks, total=100, page=1, page_size=20)
        {"success": true, "items": [...], "count": 2, "total": 100, ...}
    """
    response = success_list_response(items, total=total, page=page, page_size=page_size)
    print(json.dumps(response, indent=2))


def output_json_message(message: str) -> None:
    """Output success message as JSON using standard schema.

    Args:
        message: Success message

    Example:
        >>> output_json_message("Task deleted successfully")
        {"success": true, "message": "Task deleted successfully"}
    """
    response = success_message_response(message)
    print(json.dumps(response, indent=2))


def output_json_error(
    error_code: str, message: str, data: Optional[dict[str, Any]] = None
) -> None:
    """Output error as JSON to stdout using standard schema.

    Args:
        error_code: Error code identifier (e.g., "NOT_FOUND", "VALIDATION_ERROR")
        message: Human-readable error message
        data: Optional additional error details

    Example:
        >>> output_json_error("NOT_FOUND", "Task DEV-42 not found")
        {"success": false, "error": {"code": "NOT_FOUND", "message": "..."}}
    """
    response = error_response(error_code, message, details=data)
    print(json.dumps(response, indent=2))


class OutputManager:
    """Centralized output management with JSON mode support.

    This class handles all CLI output and ensures proper separation of
    stdout (JSON data) and stderr (human messages) in JSON mode.

    In JSON mode:
    - stdout: Only JSON output (parseable data)
    - stderr: Human-readable messages (warnings, errors, info)
    - Exit codes: 0 = success, 1 = error, 130 = cancelled

    In normal mode:
    - stdout: Rich formatted output
    - stderr: Error messages
    """

    def __init__(self, json_mode: bool = False):
        """Initialize OutputManager.

        Args:
            json_mode: Whether to output in JSON mode
        """
        self.json_mode = json_mode

    def success(self, message: str, data: Optional[dict[str, Any]] = None) -> None:
        """Print success message or JSON.

        Args:
            message: Success message for non-JSON mode
            data: Data to output as JSON (if json_mode=True)
        """
        if self.json_mode:
            output_json(data or {"message": message}, success=True)
        else:
            stdout_console.print(f"[green]✓[/green] {message}")

    def info(self, message: str) -> None:
        """Print info message to appropriate stream.

        In JSON mode, info goes to stderr to avoid polluting stdout.
        In normal mode, info goes to stdout.

        Args:
            message: Info message to display
        """
        if self.json_mode:
            stderr_console.print(message)
        else:
            stdout_console.print(message)

    def warning(self, message: str, data: Optional[dict[str, Any]] = None) -> None:
        """Print warning to stderr.

        Warnings always go to stderr in both modes.

        Args:
            message: Warning message
            data: Optional additional warning data (JSON mode)
        """
        if self.json_mode:
            # JSON warnings go to stderr in JSON format
            stderr_console.print(
                json.dumps({"level": "warning", "message": message, **(data or {})})
            )
        else:
            stderr_console.print(f"[yellow]⚠[/yellow] {message}")

    def error(
        self,
        message: str,
        error_code: Optional[str] = None,
        data: Optional[dict[str, Any]] = None,
        exit_code: int = 1,
    ) -> None:
        """Print error and exit.

        In JSON mode: outputs error JSON to stdout and human message to stderr.
        In normal mode: outputs error to stderr only.

        Args:
            message: Error message
            error_code: Error code for JSON output (default: "ERROR")
            data: Optional additional error data
            exit_code: Exit code to use (default: 1)

        Raises:
            typer.Exit: Always exits with specified code
        """
        if self.json_mode:
            # JSON to stdout for parseable errors
            output_json_error(
                error_code=error_code or "ERROR", message=message, data=data
            )
            # Human-readable to stderr
            stderr_console.print(f"Error: {message}")
        else:
            stderr_console.print(f"[red]✗[/red] {message}")

        raise typer.Exit(exit_code)

    def table(self, table: Table) -> None:
        """Print table only in non-JSON mode.

        Tables are skipped in JSON mode since the data should be
        output via the success() method instead.

        Args:
            table: Rich Table to display
        """
        if not self.json_mode:
            stdout_console.print(table)

    def json_output(self, data: dict[str, Any]) -> None:
        """Output JSON to stdout.

        Args:
            data: Data to output as JSON
        """
        print(json.dumps({"success": True, "data": data}, indent=2))


class Formatter(Protocol[T]):
    """Protocol for output formatters."""

    def format_one(self, item: T) -> None:
        """Format a single item."""
        ...

    def format_list(self, items: list[T], title: str = "") -> None:
        """Format a list of items."""
        ...


class JSONFormatter:
    """JSON output formatter with consistent structure using standard schema."""

    @staticmethod
    def format_one(item: Any, success: bool = True) -> None:
        """Print single item as JSON using standard schema.

        Args:
            item: Item to format (Pydantic model or dict)
            success: Whether operation was successful (deprecated, always True)
        """
        output_json_data(item)

    @staticmethod
    def format_list(
        items: list[Any],
        title: str = "",
        total: Optional[int] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> None:
        """Print list as JSON using standard schema.

        Args:
            items: List of items to format
            title: Optional title (deprecated, not used in standard schema)
            total: Total number of items (for pagination)
            page: Current page number
            page_size: Items per page
        """
        output_json_list(items, total=total, page=page, page_size=page_size)


class TableFormatter:
    """Table output formatter with Rich.

    Example:
        formatter = TableFormatter()
        formatter.format_list(
            items=labels,
            columns=[("Name", "cyan"), ("Color", "white")],
            title="Labels",
            row_formatter=lambda l: [l.name, l.color or ""],
        )
    """

    def __init__(self, console: Console | None = None):  # noqa: A002  # Intentional shadow
        self.console = console or _default_console

    def format_list(
        self,
        items: list[Any],
        columns: list[tuple[str, str]],  # (name, style) pairs
        title: str = "",
        row_formatter: Callable[[Any], list[str]] | None = None,
        empty_message: str | None = None,
    ) -> None:
        """Format items as a table.

        Args:
            items: Items to display
            columns: List of (column_name, style) tuples
            title: Table title
            row_formatter: Function to convert item to row values
            empty_message: Custom message for empty results
        """
        if not items:
            msg = empty_message or f"No {title.lower() if title else 'items'} found"
            self.console.print(f"[yellow]{msg}[/yellow]")
            return

        table = Table(title=title, show_header=True, header_style="bold")
        for col_name, col_style in columns:
            table.add_column(col_name, style=col_style)

        for item in items:
            row_values = (
                row_formatter(item) if row_formatter else self._default_row(item)
            )
            table.add_row(*row_values)

        self.console.print(table)
        count_text = "1 item" if len(items) == 1 else f"{len(items)} items"
        self.console.print(f"\n{count_text}")

    def _default_row(self, item: Any) -> list[str]:
        """Default row formatter - converts object to strings."""
        if hasattr(item, "model_dump"):
            data = item.model_dump()
            return [str(v) for v in data.values()]
        return [str(item)]
