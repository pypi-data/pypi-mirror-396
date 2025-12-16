"""Domain wrappers for task suggestion models."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sdk.generated.models.TaskSuggestion_Output import TaskSuggestion_Output
    from sdk.generated.models.TaskSuggestionsResponse import (
        TaskSuggestionsResponse as GeneratedTaskSuggestionsResponse,
    )

from cli.models.wrappers.task import Task


class TaskSuggestion:
    """Domain wrapper for TaskSuggestion_Output.

    Wraps the generated TaskSuggestion_Output model to provide
    a CLI-friendly interface.
    """

    def __init__(self, generated: "TaskSuggestion_Output"):
        """Initialize wrapper with generated model.

        Args:
            generated: Generated TaskSuggestion_Output instance
        """
        self._suggestion = generated
        # Wrap the task with our domain wrapper
        self.task = Task(generated.task)

    def __getattr__(self, name: str) -> object:
        """Delegate all other attributes to generated model."""
        return getattr(self._suggestion, name)

    @property
    def is_ready(self) -> bool:
        """Check if task is ready to work on (all dependencies complete)."""
        return self._suggestion.is_ready

    @property
    def blocked_by(self) -> list[str] | None:
        """Get list of task identifiers that block this task."""
        return self._suggestion.blocked_by

    @property
    def blocks(self) -> list[str] | None:
        """Get list of task identifiers this task blocks."""
        return self._suggestion.blocks

    def to_generated(self) -> "TaskSuggestion_Output":
        """Get underlying generated model.

        Returns:
            Generated TaskSuggestion_Output instance
        """
        return self._suggestion


class TaskSuggestionsResponse:
    """Domain wrapper for TaskSuggestionsResponse.

    Wraps the generated TaskSuggestionsResponse model to provide
    a CLI-friendly interface.
    """

    def __init__(self, generated: "GeneratedTaskSuggestionsResponse"):
        """Initialize wrapper with generated model.

        Args:
            generated: Generated TaskSuggestionsResponse instance
        """
        self._response = generated
        # Wrap each suggestion with our domain wrapper
        self.suggestions = [TaskSuggestion(s) for s in generated.suggestions]

    def __getattr__(self, name: str) -> object:
        """Delegate all other attributes to generated model."""
        return getattr(self._response, name)

    @property
    def total_ready(self) -> int:
        """Get total count of ready tasks."""
        return self._response.total_ready

    @property
    def total_blocked(self) -> int:
        """Get total count of blocked tasks."""
        return self._response.total_blocked

    def to_generated(self) -> "GeneratedTaskSuggestionsResponse":
        """Get underlying generated model.

        Returns:
            Generated TaskSuggestionsResponse instance
        """
        return self._response
