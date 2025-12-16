"""Task view domain models."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class TaskView(BaseModel):
    """Full task view model."""

    id: int = Field(description="View ID")
    name: str = Field(description="View name")
    workspace_id: int = Field(description="Workspace ID")
    user_id: str = Field(description="Owner user ID")
    filters: dict[str, Any] = Field(description="Filter configuration")
    is_default: bool = Field(default=False, description="Is default view")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class TaskViewCreate(BaseModel):
    """Task view creation payload."""

    name: str = Field(description="View name")
    filters: dict[str, Any] = Field(description="Filter configuration")
    is_default: bool = Field(default=False, description="Set as default view")


class TaskViewUpdate(BaseModel):
    """Task view update payload."""

    name: Optional[str] = Field(default=None, description="View name")
    filters: Optional[dict[str, Any]] = Field(
        default=None, description="Filter configuration"
    )
    is_default: Optional[bool] = Field(default=None, description="Set as default view")
