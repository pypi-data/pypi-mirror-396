"""Helper functions for task commands.

This module re-exports from cli.commands.helpers submodules for backward compatibility.
New code should import directly from the submodules:
- cli.commands.helpers.workspace
- cli.commands.helpers.formatting
- cli.commands.helpers.identifiers
- cli.commands.helpers.planning
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
    "console",
    "clear_workspace_cache",
    "get_workspace_or_exit",
    "resolve_workspace_context",
    "format_priority",
    "format_relative_time",
    "truncate_text",
    "get_active_task_id",
    "resolve_task_identifier",
    "normalize_identifier",
    "find_similar_tasks",
    "resolve_plan_content",
]
