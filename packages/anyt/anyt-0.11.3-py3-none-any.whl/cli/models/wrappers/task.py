"""Task domain wrapper - delegates to generated model with CLI-friendly API."""

from datetime import datetime
from functools import cached_property
from typing import Any, Optional

from sdk.generated.models.AssigneeType import AssigneeType as GeneratedAssigneeType
from sdk.generated.models.CodingAgentType import (
    CodingAgentType as GeneratedCodingAgentType,
)
from sdk.generated.models.DependencyTaskInfo import (
    DependencyTaskInfo as GeneratedDependencyTaskInfo,
)
from sdk.generated.models.Task import Task as GeneratedTask
from sdk.generated.models.TaskStatus import TaskStatus as GeneratedTaskStatus
from cli.models.common import AssigneeType, CodingAgentType, Priority, Status


class Task:
    """Domain task model - wraps generated model with CLI-friendly API.

    This wrapper eliminates the need for manual conversion code by:
    - Delegating all attribute access to the underlying generated model
    - Providing CLI-friendly datetime properties (parsed from ISO strings)
    - Providing helper methods for common task operations
    - Converting generated enums to domain enums for consistency
    """

    def __init__(self, generated: GeneratedTask):
        """Initialize wrapper with generated model.

        Args:
            generated: Auto-generated Task model from OpenAPI spec
        """
        self._task = generated

    # Delegate all attributes to generated model
    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to underlying generated model."""
        return getattr(self._task, name)

    # Override specific properties to provide domain enum conversions
    @property
    def status(self) -> Status:
        """Get task status as domain Status enum."""
        return self._convert_status_to_domain(self._task.status)

    @property
    def priority(self) -> Priority:
        """Get task priority as domain Priority enum."""
        return self._convert_priority_to_domain(self._task.priority)

    @property
    def assignee_type(self) -> Optional[AssigneeType]:
        """Get assignee type as domain AssigneeType enum."""
        return self._convert_assignee_type_to_domain(self._task.assignee_type)

    @property
    def assigned_coding_agent(self) -> Optional[CodingAgentType]:
        """Get assigned coding agent as domain CodingAgentType enum."""
        return self._convert_coding_agent_type_to_domain(
            self._task.assigned_coding_agent
        )

    # CLI-friendly datetime properties
    @cached_property
    def created_at(self) -> datetime:
        """Parse created_at string to datetime."""
        return self._parse_datetime(self._task.created_at)

    @cached_property
    def updated_at(self) -> datetime:
        """Parse updated_at string to datetime."""
        return self._parse_datetime(self._task.updated_at)

    @cached_property
    def started_at(self) -> Optional[datetime]:
        """Parse started_at string to datetime."""
        return (
            self._parse_datetime(self._task.started_at)
            if self._task.started_at
            else None
        )

    @cached_property
    def completed_at(self) -> Optional[datetime]:
        """Parse completed_at string to datetime."""
        return (
            self._parse_datetime(self._task.completed_at)
            if self._task.completed_at
            else None
        )

    @cached_property
    def canceled_at(self) -> Optional[datetime]:
        """Parse canceled_at string to datetime."""
        return (
            self._parse_datetime(self._task.canceled_at)
            if self._task.canceled_at
            else None
        )

    @cached_property
    def archived_at(self) -> Optional[datetime]:
        """Parse archived_at string to datetime."""
        return (
            self._parse_datetime(self._task.archived_at)
            if self._task.archived_at
            else None
        )

    @cached_property
    def deleted_at(self) -> Optional[datetime]:
        """Parse deleted_at string to datetime."""
        return (
            self._parse_datetime(self._task.deleted_at)
            if self._task.deleted_at
            else None
        )

    # Helper methods
    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self._task.status == GeneratedTaskStatus.DONE

    @property
    def is_blocked(self) -> bool:
        """Check if task is blocked."""
        return self._task.status == GeneratedTaskStatus.BLOCKED

    @property
    def is_canceled(self) -> bool:
        """Check if task is canceled."""
        return self._task.status == GeneratedTaskStatus.CANCELED

    @property
    def is_archived(self) -> bool:
        """Check if task is archived."""
        return self._task.status == GeneratedTaskStatus.ARCHIVED

    # Expose underlying model for API calls
    def to_generated(self) -> GeneratedTask:
        """Get underlying generated model for API calls."""
        return self._task

    # Conversion helpers (private methods)
    @staticmethod
    def _parse_datetime(dt_str: str) -> datetime:
        """Parse ISO 8601 datetime string."""
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
        return datetime.fromisoformat(dt_str)

    @staticmethod
    def _convert_status_to_domain(
        status: Optional[GeneratedTaskStatus] | str,
    ) -> Status:
        """Convert generated status to domain Status enum."""
        if not status:
            return Status.BACKLOG

        # Handle string statuses (from DependencyTaskInfo)
        if isinstance(status, str):
            status_str_map = {
                "backlog": Status.BACKLOG,
                "todo": Status.TODO,
                "active": Status.ACTIVE,
                "blocked": Status.BLOCKED,
                "done": Status.DONE,
                "canceled": Status.CANCELED,
                "archived": Status.ARCHIVED,
            }
            return status_str_map.get(status.lower(), Status.BACKLOG)

        # Handle GeneratedTaskStatus enum
        # Map generated enum to domain enum
        status_enum_map = {  # type: ignore[unreachable]
            GeneratedTaskStatus.BACKLOG: Status.BACKLOG,
            GeneratedTaskStatus.TODO: Status.TODO,
            GeneratedTaskStatus.ACTIVE: Status.ACTIVE,
            GeneratedTaskStatus.BLOCKED: Status.BLOCKED,
            GeneratedTaskStatus.DONE: Status.DONE,
            GeneratedTaskStatus.CANCELED: Status.CANCELED,
            GeneratedTaskStatus.ARCHIVED: Status.ARCHIVED,
        }
        return status_enum_map.get(status, Status.BACKLOG)

    @staticmethod
    def _convert_priority_to_domain(priority: Optional[int]) -> Priority:
        """Convert generated priority int to domain Priority enum."""
        if priority is None:
            return Priority.NORMAL
        # Priority enum values: -2=LOWEST, -1=LOW, 0=NORMAL, 1=HIGH, 2=HIGHEST
        priority_map = {
            -2: Priority.LOWEST,
            -1: Priority.LOW,
            0: Priority.NORMAL,
            1: Priority.HIGH,
            2: Priority.HIGHEST,
        }
        return priority_map.get(priority, Priority.NORMAL)

    @staticmethod
    def _convert_assignee_type_to_domain(
        assignee_type: Optional[GeneratedAssigneeType],
    ) -> Optional[AssigneeType]:
        """Convert generated assignee_type to domain AssigneeType enum."""
        if not assignee_type:
            return None
        # Map generated enum to domain enum
        assignee_type_map = {
            GeneratedAssigneeType.HUMAN: AssigneeType.HUMAN,
        }
        return assignee_type_map.get(assignee_type, AssigneeType.HUMAN)

    @staticmethod
    def _convert_coding_agent_type_to_domain(
        coding_agent_type: Optional[GeneratedCodingAgentType],
    ) -> Optional[CodingAgentType]:
        """Convert generated coding_agent_type to domain CodingAgentType enum."""
        if not coding_agent_type:
            return None
        # Map generated enum to domain enum
        coding_agent_type_map = {
            GeneratedCodingAgentType.CLAUDE_CODE: CodingAgentType.CLAUDE_CODE,
            GeneratedCodingAgentType.CODEX: CodingAgentType.CODEX,
            GeneratedCodingAgentType.GEMINI_CLI: CodingAgentType.GEMINI_CLI,
        }
        return coding_agent_type_map.get(coding_agent_type)


class TaskDependencyInfo:
    """Minimal task info wrapper for dependency responses."""

    def __init__(self, generated: GeneratedDependencyTaskInfo):
        """Initialize wrapper with generated dependency info.

        Args:
            generated: Auto-generated DependencyTaskInfo model from OpenAPI spec
        """
        self._info = generated

    # Delegate all attributes to generated model
    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to underlying generated model."""
        return getattr(self._info, name)

    # Override specific properties to provide domain enum conversions
    @property
    def status(self) -> Status:
        """Get task status as domain Status enum."""
        return Task._convert_status_to_domain(self._info.status)

    @property
    def priority(self) -> Priority:
        """Get task priority as domain Priority enum."""
        return Task._convert_priority_to_domain(self._info.priority)

    # Expose underlying model
    def to_generated(self) -> GeneratedDependencyTaskInfo:
        """Get underlying generated model."""
        return self._info
