"""Workflow execution metadata models."""

from datetime import UTC, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WorkflowExecutionMetadata(BaseModel):
    """Workflow execution metadata stored in task.

    This metadata tracks workflow execution details including
    execution ID, agent ID, timestamps, and status.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_execution_id": "exec-abc123",
                "workflow_name": "code-implementation",
                "agent_id": "agent-xyz789",
                "started_at": "2025-10-23T10:00:00Z",
                "completed_at": "2025-10-23T10:05:32Z",
                "status": "success",
                "duration_seconds": 332.5,
            }
        }
    )

    workflow_execution_id: str = Field(
        ..., description="Unique UUID for this workflow execution"
    )
    workflow_name: str = Field(..., description="Name of the workflow")
    agent_id: str = Field(..., description="ID of the agent that executed the workflow")
    started_at: str = Field(
        ..., description="ISO 8601 timestamp when execution started"
    )
    completed_at: Optional[str] = Field(
        None, description="ISO 8601 timestamp when execution completed"
    )
    status: str = Field(
        ..., description="Execution status: running, success, failure, cancelled"
    )
    duration_seconds: Optional[float] = Field(
        None, description="Execution duration in seconds"
    )

    @classmethod
    def create_started(
        cls, workflow_execution_id: str, workflow_name: str, agent_id: str
    ) -> "WorkflowExecutionMetadata":
        """Create metadata for a workflow that just started.

        Args:
            workflow_execution_id: Unique execution ID
            workflow_name: Name of the workflow
            agent_id: ID of the agent executing the workflow

        Returns:
            WorkflowExecutionMetadata with running status
        """
        return cls(
            workflow_execution_id=workflow_execution_id,
            workflow_name=workflow_name,
            agent_id=agent_id,
            started_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            status="running",
            completed_at=None,
            duration_seconds=None,
        )

    def complete_success(self, duration_seconds: Optional[float] = None) -> None:
        """Mark the workflow as successfully completed.

        Args:
            duration_seconds: Optional duration to override calculated duration
        """
        # Only set completed_at if not already set
        if self.completed_at is None:
            self.completed_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        self.status = "success"
        if duration_seconds is not None:
            self.duration_seconds = duration_seconds
        elif self.started_at and self.completed_at:
            # Calculate duration
            start = datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))
            end = datetime.fromisoformat(self.completed_at.replace("Z", "+00:00"))
            self.duration_seconds = (end - start).total_seconds()

    def complete_failure(
        self, duration_seconds: Optional[float] = None, error: Optional[str] = None
    ) -> None:
        """Mark the workflow as failed.

        Args:
            duration_seconds: Optional duration to override calculated duration
            error: Optional error message (not stored in metadata, handle separately)
        """
        # Only set completed_at if not already set
        if self.completed_at is None:
            self.completed_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        self.status = "failure"
        if duration_seconds is not None:
            self.duration_seconds = duration_seconds
        elif self.started_at and self.completed_at:
            # Calculate duration
            start = datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))
            end = datetime.fromisoformat(self.completed_at.replace("Z", "+00:00"))
            self.duration_seconds = (end - start).total_seconds()
