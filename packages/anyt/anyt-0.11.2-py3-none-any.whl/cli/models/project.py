"""Project domain models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from cli.models.common import ProjectStatus


class Project(BaseModel):
    """Full project model."""

    id: int = Field(description="Project ID")
    name: str = Field(description="Project name")
    description: Optional[str] = Field(default=None, description="Project description")
    status: Optional[ProjectStatus] = Field(default=None, description="Project status")
    lead_id: Optional[str] = Field(default=None, description="Project lead user ID")
    start_date: Optional[datetime] = Field(
        default=None, description="Project start date"
    )
    target_date: Optional[datetime] = Field(
        default=None, description="Project target completion date"
    )
    color: Optional[str] = Field(default=None, description="Project color (hex)")
    icon: Optional[str] = Field(default=None, description="Project icon identifier")
    workspace_id: int = Field(description="Workspace ID")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(
        default=None, description="Soft delete timestamp"
    )

    model_config = ConfigDict(
        use_enum_values=False  # Keep enum instances for status comparison
    )


class ProjectCreate(BaseModel):
    """Project creation payload."""

    name: str = Field(description="Project name")
    description: Optional[str] = Field(default=None, description="Project description")
    status: Optional[ProjectStatus] = Field(
        default=ProjectStatus.ACTIVE, description="Project status"
    )
    lead_id: Optional[str] = Field(default=None, description="Project lead user ID")
    start_date: Optional[str] = Field(
        default=None, description="Project start date (ISO format)"
    )
    target_date: Optional[str] = Field(
        default=None, description="Project target completion date (ISO format)"
    )
    color: Optional[str] = Field(default=None, description="Project color (hex)")
    icon: Optional[str] = Field(default=None, description="Project icon identifier")

    model_config = ConfigDict(
        use_enum_values=True  # Convert enums to values for API
    )
