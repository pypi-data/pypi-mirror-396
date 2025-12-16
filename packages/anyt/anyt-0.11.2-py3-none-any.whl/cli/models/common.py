"""Common types and enums used across the CLI."""

from enum import Enum


class Status(str, Enum):
    """Task status values.

    Valid status values for AnyTask tasks. Note that some values use
    specific spellings that must match the backend API exactly.

    Status Workflow:
    - BACKLOG: Default status for new tasks, not yet scheduled
    - TODO: Task is ready to be worked on
    - ACTIVE: Task is actively being worked on
    - BLOCKED: Task is blocked by dependencies or external issues
    - DONE: Task is completed
    - CANCELED: Task was cancelled (NOTE: single 'l' spelling, backend convention)
    - ARCHIVED: Task is archived and no longer active

    Examples:
        >>> task = TaskCreate(title="Fix bug", status=Status.TODO)
        >>> task = TaskCreate(title="Fix bug", status="todo")  # String also works
    """

    BACKLOG = "backlog"  # Default status for new tasks
    TODO = "todo"  # Ready to work on
    ACTIVE = "active"  # Currently being worked on
    BLOCKED = "blocked"  # Blocked by dependencies or issues
    CANCELED = "canceled"  # Cancelled (single 'l', backend spelling)
    DONE = "done"  # Completed
    ARCHIVED = "archived"  # Archived and no longer active


class Priority(int, Enum):
    """Task priority values.

    Priority scale from -2 (lowest) to 2 (highest). Default is NORMAL (0).

    Priority Levels:
    - HIGHEST (2): Critical, urgent work
    - HIGH (1): Important work
    - NORMAL (0): Default priority
    - LOW (-1): Low priority work
    - LOWEST (-2): Nice-to-have work

    Examples:
        >>> task = TaskCreate(title="Fix bug", priority=Priority.HIGH)
        >>> task = TaskCreate(title="Fix bug", priority=1)  # Int also works
    """

    LOWEST = -2  # Nice-to-have
    LOW = -1  # Low priority
    NORMAL = 0  # Default priority
    HIGH = 1  # Important work
    HIGHEST = 2  # Critical, urgent work


class AssigneeType(str, Enum):
    """Assignee type for tasks.

    Note: Values must match backend API exactly.
    """

    HUMAN = "human"
    AGENT = "agent"


class ProjectStatus(str, Enum):
    """Project status values.

    Note: Values must match backend API exactly.
    """

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELED = "canceled"


class CodingAgentType(str, Enum):
    """Coding agent type for task assignment.

    Represents the type of coding agent that can be assigned to work on a task.
    Values must match backend API exactly.
    """

    CLAUDE_CODE = "claude_code"
    CODEX = "codex"
    GEMINI_CLI = "gemini_cli"


class AIIntegration(str, Enum):
    """AI tool integration options for workspace initialization.

    Currently supported AI tools that can be configured during init.
    More integrations may be added in the future.
    """

    CLAUDE_CODE = "claude_code"  # Claude Code (Anthropic's CLI tool)
