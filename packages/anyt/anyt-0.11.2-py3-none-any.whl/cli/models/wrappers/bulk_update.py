"""Domain wrappers for bulk update models."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sdk.generated.models.BulkTaskResult import (
        BulkTaskResult as GeneratedBulkTaskResult,
    )
    from sdk.generated.models.BulkUpdateTasksResponse import (
        BulkUpdateTasksResponse as GeneratedBulkUpdateTasksResponse,
    )


class BulkTaskResult:
    """Domain wrapper for BulkTaskResult.

    Wraps the generated BulkTaskResult model to provide
    a CLI-friendly interface.
    """

    def __init__(self, generated: "GeneratedBulkTaskResult"):
        """Initialize wrapper with generated model.

        Args:
            generated: Generated BulkTaskResult instance
        """
        self._result = generated

    def __getattr__(self, name: str) -> object:
        """Delegate all attributes to generated model."""
        return getattr(self._result, name)

    @property
    def identifier(self) -> str:
        """Get task identifier."""
        return self._result.identifier

    @property
    def task_id(self) -> str | None:
        """Get task ID (numeric or None)."""
        return self._result.task_id

    @property
    def success(self) -> bool:
        """Check if operation succeeded."""
        return self._result.success

    @property
    def message(self) -> str | None:
        """Get success/info message."""
        return self._result.message

    @property
    def error(self) -> str | None:
        """Get error message if operation failed."""
        return self._result.error

    def to_generated(self) -> "GeneratedBulkTaskResult":
        """Get underlying generated model.

        Returns:
            Generated BulkTaskResult instance
        """
        return self._result


class BulkUpdateTasksResponse:
    """Domain wrapper for BulkUpdateTasksResponse.

    Wraps the generated BulkUpdateTasksResponse model to provide
    a CLI-friendly interface.
    """

    def __init__(self, generated: "GeneratedBulkUpdateTasksResponse"):
        """Initialize wrapper with generated model.

        Args:
            generated: Generated BulkUpdateTasksResponse instance
        """
        self._response = generated
        # Wrap each result with our domain wrapper
        self.results = [BulkTaskResult(r) for r in generated.results]

    def __getattr__(self, name: str) -> object:
        """Delegate all attributes to generated model."""
        return getattr(self._response, name)

    @property
    def updated(self) -> int:
        """Get total number of updated tasks."""
        return self._response.updated

    @property
    def total(self) -> int | None:
        """Get total number of tasks processed."""
        return self._response.total

    @property
    def succeeded(self) -> int | None:
        """Get number of successful updates."""
        return self._response.succeeded

    @property
    def failed(self) -> int | None:
        """Get number of failed updates."""
        return self._response.failed

    def to_generated(self) -> "GeneratedBulkUpdateTasksResponse":
        """Get underlying generated model.

        Returns:
            Generated BulkUpdateTasksResponse instance
        """
        return self._response
