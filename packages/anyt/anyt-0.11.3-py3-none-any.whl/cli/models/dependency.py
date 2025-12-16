"""Task dependency models."""

from datetime import datetime

from pydantic import BaseModel, Field


class TaskDependency(BaseModel):
    """Task dependency relationship."""

    task_id: int = Field(description="Dependent task ID")
    depends_on_id: int = Field(description="Task that this depends on")
    created_at: datetime = Field(description="Creation timestamp")
