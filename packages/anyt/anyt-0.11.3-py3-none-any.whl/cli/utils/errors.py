"""Error handling utilities and domain-specific exceptions for CLI operations.

This module provides:
1. Domain-specific exception hierarchy for CLI operations
2. Error handling utilities for production and development modes

Exception Hierarchy:
    CLIError (base)
    ├── ConfigurationError
    │   ├── AuthenticationError
    │   └── WorkspaceNotConfiguredError
    ├── ResourceNotFoundError
    │   ├── TaskNotFoundError
    │   ├── WorkspaceNotFoundError
    │   └── ProjectNotFoundError
    ├── APIError
    │   └── RateLimitError
    ├── ValidationError
    │   └── DependencyError
    ├── WorkflowExecutionError
    └── WorkerError
"""

import os
from typing import TYPE_CHECKING, NoReturn

import typer
from rich.markup import escape

from cli.commands.console import stderr_console
from cli.commands.formatters import OutputManager

if TYPE_CHECKING:
    pass  # pyright: ignore[reportMissingImports]


# =============================================================================
# Domain-Specific Exception Hierarchy
# =============================================================================


class CLIError(Exception):
    """Base exception for all CLI errors.

    All domain-specific exceptions inherit from this class, enabling
    broad exception handling when needed while still allowing specific
    handling for particular error types.

    Attributes:
        message: Human-readable error message.
    """

    def __init__(self, message: str) -> None:
        """Initialize CLIError.

        Args:
            message: Human-readable error message.
        """
        self.message = message
        super().__init__(message)


# -----------------------------------------------------------------------------
# Configuration Errors
# -----------------------------------------------------------------------------


class ConfigurationError(CLIError):
    """Configuration-related errors.

    Raised when there are issues with CLI configuration, environment setup,
    or missing/invalid settings.
    """

    pass


class AuthenticationError(ConfigurationError):
    """Authentication failures (missing/invalid API key).

    Raised when:
    - ANYT_API_KEY environment variable is not set
    - API key is invalid or expired
    - API returns 401 Unauthorized
    """

    def __init__(self, message: str = "Authentication failed") -> None:
        """Initialize AuthenticationError.

        Args:
            message: Error message describing the authentication failure.
        """
        super().__init__(message)


class WorkspaceNotConfiguredError(ConfigurationError):
    """Workspace not initialized or configured.

    Raised when:
    - No workspace has been initialized (anyt init not run)
    - Workspace configuration file is missing or corrupted
    - Command requires workspace context but none is available
    """

    def __init__(
        self, message: str = "Workspace not configured. Run 'anyt init' first."
    ) -> None:
        """Initialize WorkspaceNotConfiguredError.

        Args:
            message: Error message describing the configuration issue.
        """
        super().__init__(message)


# -----------------------------------------------------------------------------
# Resource Not Found Errors
# -----------------------------------------------------------------------------


class ResourceNotFoundError(CLIError):
    """Base for resource not found errors.

    Raised when a requested resource (task, workspace, project, etc.)
    cannot be found. Subclasses provide more specific error types.
    """

    def __init__(self, resource_type: str, identifier: str) -> None:
        """Initialize ResourceNotFoundError.

        Args:
            resource_type: Type of resource (e.g., "Task", "Workspace").
            identifier: The identifier that was not found.
        """
        self.resource_type = resource_type
        self.identifier = identifier
        super().__init__(f"{resource_type} not found: {identifier}")


class TaskNotFoundError(ResourceNotFoundError):
    """Task not found by identifier.

    Raised when a task lookup by identifier (e.g., "DEV-42") fails.
    """

    def __init__(self, identifier: str) -> None:
        """Initialize TaskNotFoundError.

        Args:
            identifier: The task identifier that was not found.
        """
        super().__init__("Task", identifier)


class WorkspaceNotFoundError(ResourceNotFoundError):
    """Workspace not found.

    Raised when a workspace lookup fails.
    """

    def __init__(self, identifier: str) -> None:
        """Initialize WorkspaceNotFoundError.

        Args:
            identifier: The workspace identifier (name or ID) that was not found.
        """
        super().__init__("Workspace", identifier)


class ProjectNotFoundError(ResourceNotFoundError):
    """Project not found.

    Raised when a project lookup fails.
    """

    def __init__(self, identifier: str) -> None:
        """Initialize ProjectNotFoundError.

        Args:
            identifier: The project identifier (name or ID) that was not found.
        """
        super().__init__("Project", identifier)


class ViewNotFoundError(ResourceNotFoundError):
    """View not found.

    Raised when a view lookup fails.
    """

    def __init__(self, identifier: str) -> None:
        """Initialize ViewNotFoundError.

        Args:
            identifier: The view identifier (name or ID) that was not found.
        """
        super().__init__("View", identifier)


class CommentNotFoundError(ResourceNotFoundError):
    """Comment not found.

    Raised when a comment lookup fails.
    """

    def __init__(self, identifier: str) -> None:
        """Initialize CommentNotFoundError.

        Args:
            identifier: The comment ID that was not found.
        """
        super().__init__("Comment", identifier)


# -----------------------------------------------------------------------------
# API Errors
# -----------------------------------------------------------------------------


class APIError(CLIError):
    """API communication errors.

    Raised when there are issues communicating with the AnyTask API server.
    Captures HTTP status code when available for more specific error handling.
    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize APIError.

        Args:
            message: Error message describing the API failure.
            status_code: HTTP status code if available.
        """
        self.status_code = status_code
        super().__init__(message)


class RateLimitError(APIError):
    """API rate limit exceeded.

    Raised when the API returns 429 Too Many Requests.
    Includes retry information when available.
    """

    def __init__(
        self, message: str = "Rate limit exceeded", retry_after: int | None = None
    ) -> None:
        """Initialize RateLimitError.

        Args:
            message: Error message.
            retry_after: Seconds to wait before retrying, if provided by API.
        """
        self.retry_after = retry_after
        super().__init__(message, status_code=429)


class ConflictError(APIError):
    """Resource conflict (409).

    Raised when an operation conflicts with existing data, such as:
    - Circular dependency creation
    - Duplicate resource creation
    - Concurrent modification conflicts
    """

    def __init__(self, message: str = "Resource conflict") -> None:
        """Initialize ConflictError.

        Args:
            message: Error message describing the conflict.
        """
        super().__init__(message, status_code=409)


# -----------------------------------------------------------------------------
# Validation Errors
# -----------------------------------------------------------------------------


class ValidationError(CLIError):
    """Input validation errors.

    Raised when user input fails validation rules. May include
    field-specific error information for detailed feedback.
    """

    def __init__(self, message: str, field: str | None = None) -> None:
        """Initialize ValidationError.

        Args:
            message: Error message describing the validation failure.
            field: Optional field name that failed validation.
        """
        self.field = field
        super().__init__(message)


class DependencyError(ValidationError):
    """Task dependency validation errors.

    Raised when dependency operations fail validation, such as:
    - Attempting to create circular dependencies
    - Adding self as dependency
    - Completing task with incomplete dependencies
    """

    def __init__(
        self,
        message: str,
        task_identifier: str | None = None,
        dependency_identifier: str | None = None,
    ) -> None:
        """Initialize DependencyError.

        Args:
            message: Error message describing the dependency issue.
            task_identifier: The task that has the dependency issue.
            dependency_identifier: The problematic dependency.
        """
        self.task_identifier = task_identifier
        self.dependency_identifier = dependency_identifier
        super().__init__(message)


# -----------------------------------------------------------------------------
# Worker/Workflow Errors
# -----------------------------------------------------------------------------


class WorkflowExecutionError(CLIError):
    """Workflow execution failures.

    Raised when a workflow fails during execution. Captures the
    workflow name and step for debugging purposes.
    """

    def __init__(
        self, message: str, workflow_name: str | None = None, step: str | None = None
    ) -> None:
        """Initialize WorkflowExecutionError.

        Args:
            message: Error message describing the workflow failure.
            workflow_name: Name of the workflow that failed.
            step: The step that failed within the workflow.
        """
        self.workflow_name = workflow_name
        self.step = step
        super().__init__(message)


class WorkerError(CLIError):
    """Worker-related errors.

    Raised when there are issues with worker operations, such as:
    - Worker configuration errors
    - Worker startup failures
    - Task execution errors within workers
    """

    def __init__(self, message: str, worker_id: str | None = None) -> None:
        """Initialize WorkerError.

        Args:
            message: Error message describing the worker issue.
            worker_id: ID of the worker that encountered the error.
        """
        self.worker_id = worker_id
        super().__init__(message)


# =============================================================================
# Error Handling Utilities
# =============================================================================


def is_debug_mode() -> bool:
    """Check if debug mode is enabled via ANYT_DEBUG environment variable."""
    debug_value = os.getenv("ANYT_DEBUG", "false").lower()
    return debug_value in ("1", "true", "yes", "on")


def install_traceback_handler() -> None:
    """Install rich traceback handler if in debug mode."""
    if is_debug_mode():
        from rich.traceback import install

        install(show_locals=True, width=120, word_wrap=True)


def handle_api_error(
    error: Exception, context: str = "", json_output: bool = False
) -> NoReturn:
    """Handle API errors with user-friendly messages in production mode.

    Args:
        error: The exception that occurred
        context: Optional context about what operation failed (e.g., "adding comment")
        json_output: Whether to output errors in JSON format

    Raises:
        SystemExit: Always exits with code 1 after displaying error
    """
    # Import at runtime to avoid circular imports and missing module errors
    try:
        from sdk.generated.api_config import HTTPException  # pyright: ignore[reportMissingImports]
    except ImportError:
        HTTPException = None  # type: ignore[assignment,misc]

    # In debug mode, let the exception propagate for full stack trace
    if is_debug_mode():
        raise error

    # Create output manager for consistent error formatting
    output = OutputManager(json_mode=json_output)

    if HTTPException is not None and isinstance(error, HTTPException):
        status_code = error.status_code  # pyright: ignore[reportAttributeAccessIssue]

        # Common HTTP error codes with helpful messages
        if status_code == 401:
            message = "Authentication failed. Please check your API key."
            error_code = "UNAUTHORIZED"
            if not json_output:
                stderr_console.print("[red]Error:[/red] Authentication failed")
                stderr_console.print("\nPlease check your API key:")
                stderr_console.print(
                    "  1. Ensure ANYT_API_KEY environment variable is set"
                )
                stderr_console.print("  2. Verify the API key is valid and not expired")
                stderr_console.print(
                    "  3. Check the API URL is correct (ANYT_API_URL or workspace config)"
                )
                stderr_console.print("\nExample:")
                stderr_console.print(
                    "  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]"
                )

        elif status_code == 403:
            message = (
                "Permission denied. You don't have access to perform this operation."
            )
            error_code = "FORBIDDEN"
            if not json_output:
                stderr_console.print("[red]Error:[/red] Permission denied")
                stderr_console.print(
                    "\nYou don't have permission to perform this operation. Please check:"
                )
                stderr_console.print("  - You are using the correct workspace")
                stderr_console.print("  - Your API key has the required permissions")

        elif status_code == 404:
            message = "Resource not found. Please check identifiers and access."
            error_code = "NOT_FOUND"
            if not json_output:
                stderr_console.print("[red]Error:[/red] Resource not found")
                stderr_console.print(
                    "\nThe requested resource could not be found. Please check:"
                )
                stderr_console.print("  - Task/workspace identifiers are correct")
                stderr_console.print("  - You have access to the workspace")

        elif status_code == 409:
            message = "Conflict. The operation conflicts with existing data."
            error_code = "CONFLICT"
            if not json_output:
                stderr_console.print("[red]Error:[/red] Conflict")
                stderr_console.print(
                    "\nThe operation conflicts with existing data (e.g., circular dependency)"
                )

        elif status_code == 422:
            message = "Validation error. The data provided is invalid."
            error_code = "VALIDATION_ERROR"
            if not json_output:
                stderr_console.print("[red]Error:[/red] Validation error")
                stderr_console.print(
                    "\nThe data provided is invalid. Please check your input."
                )

        elif status_code >= 500:
            message = f"Server error (HTTP {status_code}). Please try again later."
            error_code = "SERVER_ERROR"
            if not json_output:
                stderr_console.print(
                    f"[red]Error:[/red] Server error (HTTP {status_code})"
                )
                stderr_console.print("\nThe AnyTask API server encountered an error.")
                stderr_console.print(
                    "Please try again later or contact support if the issue persists."
                )

        else:
            message = f"API request failed (HTTP {status_code}): {str(error)}"
            error_code = f"HTTP_{status_code}"
            if not json_output:
                stderr_console.print(
                    f"[red]Error:[/red] API request failed (HTTP {status_code})"
                )
                stderr_console.print(f"\n{escape(str(error))}")

        # Output error in JSON or exit in normal mode
        if json_output:
            # output.error() always raises typer.Exit
            output.error(
                message, error_code=error_code, data={"status_code": status_code}
            )
        else:
            # Debug mode hint
            stderr_console.print(
                "\n[dim]For detailed error information, run with: export ANYT_DEBUG=true[/dim]"
            )
            raise typer.Exit(1)

    else:
        # Generic error handling
        message = str(error)
        error_code = type(error).__name__.upper()

        if json_output:
            # output.error() always raises typer.Exit
            output.error(message, error_code=error_code)
        else:
            stderr_console.print(f"[red]Error:[/red] {escape(message)}")
            stderr_console.print(
                "\n[dim]For detailed error information, run with: export ANYT_DEBUG=true[/dim]"
            )
            raise typer.Exit(1)

    # This line should never be reached, but satisfies mypy
    raise typer.Exit(1)


def format_validation_error(error: Exception) -> str:
    """Format validation errors in a user-friendly way.

    Args:
        error: Validation exception

    Returns:
        Formatted error message
    """
    # Extract useful information from Pydantic validation errors
    error_str = str(error)

    # If it's a Pydantic error, try to extract field-specific messages
    if "validation error" in error_str.lower():
        return f"Invalid data: {error_str}"

    return error_str
