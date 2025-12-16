"""Helper utilities for CLI commands.

This module provides re-exports from submodules for backward compatibility.
"""

from cli.commands.console import console
from cli.commands.helpers.formatting import (
    format_priority,
    format_relative_time,
    truncate_text,
)
from cli.commands.helpers.identifiers import (
    find_similar_tasks,
    get_active_task_id,
    normalize_identifier,
    resolve_task_identifier,
)
from cli.commands.helpers.planning import resolve_plan_content
from cli.commands.helpers.workspace import (
    clear_workspace_cache,
    get_workspace_or_exit,
    resolve_workspace_context,
)

__all__ = [
    # Re-exported from console
    "console",
    # Workspace utilities
    "clear_workspace_cache",
    "get_workspace_or_exit",
    "resolve_workspace_context",
    # Formatting utilities
    "format_priority",
    "format_relative_time",
    "truncate_text",
    # Identifier utilities
    "get_active_task_id",
    "resolve_task_identifier",
    "normalize_identifier",
    "find_similar_tasks",
    # Planning utilities
    "resolve_plan_content",
]
