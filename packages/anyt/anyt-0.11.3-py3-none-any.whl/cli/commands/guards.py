"""Type guard functions for command validation.

These functions ensure runtime validation while providing type narrowing for mypy.
Unlike assert statements, guards always execute regardless of Python optimization flags.
"""

from typing import Any

from cli.config import WorkspaceConfig
from cli.utils.errors import AuthenticationError, WorkspaceNotConfiguredError


def require_workspace_config(config: WorkspaceConfig | None) -> WorkspaceConfig:
    """Ensure workspace config exists, raise if not.

    Use this instead of `assert ctx.workspace_config is not None` to ensure
    validation runs regardless of Python optimization flags (-O).

    Args:
        config: Workspace configuration that may be None

    Returns:
        The workspace configuration (type-narrowed to non-None)

    Raises:
        WorkspaceNotConfiguredError: If config is None

    Example:
        with CommandContext(require_auth=True, require_workspace=True) as ctx:
            workspace_config = require_workspace_config(ctx.workspace_config)
            workspace_id = workspace_config.workspace_id  # Now typed correctly
    """
    if config is None:
        raise WorkspaceNotConfiguredError(
            "Workspace configuration required. Run 'anyt init' first."
        )
    return config


def require_api_config(config: dict[str, str] | None) -> dict[str, str]:
    """Ensure API config exists, raise if not.

    Use this instead of `assert ctx.api_config is not None` to ensure
    validation runs regardless of Python optimization flags (-O).

    Args:
        config: API configuration that may be None

    Returns:
        The API configuration (type-narrowed to non-None)

    Raises:
        AuthenticationError: If config is None

    Example:
        with CommandContext(require_auth=True) as ctx:
            api_config = require_api_config(ctx.api_config)
            api_url = api_config["api_url"]  # Now typed correctly
    """
    if config is None:
        raise AuthenticationError(
            "Authentication required. Set ANYT_API_KEY environment variable."
        )
    return config


def require_not_none(value: Any | None, name: str = "value") -> Any:
    """Ensure a value is not None, raise if it is.

    Generic guard for any value that should not be None.

    Args:
        value: Value to check
        name: Name of the value for error message

    Returns:
        The value (type-narrowed to non-None)

    Raises:
        ValueError: If value is None
    """
    if value is None:
        raise ValueError(f"Required {name} is None")
    return value
