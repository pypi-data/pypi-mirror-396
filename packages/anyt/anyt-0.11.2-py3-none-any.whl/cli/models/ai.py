"""AI-related domain models."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class OrganizationResult(BaseModel):
    """Result of workspace organization."""

    changes: list[dict[str, Any]] = Field(
        description="List of changes made or suggested"
    )
    summary: str = Field(description="Summary of organization actions")
    normalized_tasks: list[dict[str, Any]] = Field(
        default_factory=lambda: [], description="Normalized task titles"
    )
    label_suggestions: list[dict[str, Any]] = Field(
        default_factory=lambda: [], description="Label suggestions"
    )
    duplicates: list[dict[str, Any]] = Field(
        default_factory=lambda: [], description="Potential duplicate tasks"
    )
    cost_tokens: Optional[int] = Field(default=None, description="Cost in tokens")


class TaskAutoFill(BaseModel):
    """Auto-filled task details."""

    identifier: str = Field(description="Task identifier")
    filled_fields: dict[str, Any] = Field(description="Fields that were auto-filled")
    reasoning: str | None = Field(default=None, description="AI reasoning")
    generated: Optional[dict[str, Any]] = Field(
        default=None, description="Generated content fields"
    )
    cost_tokens: Optional[int] = Field(default=None, description="Cost in tokens")


class AISuggestions(BaseModel):
    """AI-powered task suggestions."""

    recommended_tasks: list[dict[str, Any]] = Field(
        description="Recommended tasks to work on"
    )
    recommendations: Optional[list[dict[str, Any]]] = Field(
        default=None, description="Alias for recommended_tasks"
    )
    reasoning: str = Field(description="Reasoning for recommendations")


class TaskReview(BaseModel):
    """AI task review result."""

    identifier: str = Field(description="Task identifier")
    checks: list[dict[str, Any]] = Field(description="Review checks performed")
    warnings: list[str] = Field(default_factory=list, description="Review warnings")
    is_ready: bool = Field(description="Whether task is ready to be marked done")
    summary: str = Field(description="Review summary")


class WorkspaceSummary(BaseModel):
    """Workspace progress summary."""

    period: str = Field(description="Summary period (today, weekly, monthly)")
    activity_breakdown: dict[str, Any] = Field(description="Breakdown of activities")
    insights: list[str] = Field(description="Key insights from the period")
    summary_text: str = Field(description="Human-readable summary")
    summary: Optional[str] = Field(default=None, description="Alias for summary_text")
    cost_tokens: Optional[int] = Field(default=None, description="Cost in tokens")


class AIUsage(BaseModel):
    """AI usage statistics."""

    total_requests: int = Field(description="Total number of AI requests")
    total_tokens: int = Field(description="Total tokens consumed")
    total_cost: float = Field(description="Total cost in USD")
    breakdown: dict[str, Any] = Field(
        default_factory=lambda: {}, description="Usage breakdown by operation"
    )
    period: Optional[str] = Field(default=None, description="Usage period")
    operations: list[dict[str, Any]] = Field(
        default_factory=lambda: [], description="Operations breakdown"
    )
    total_calls: Optional[int] = Field(default=None, description="Total calls")
    cache_hits: Optional[int] = Field(default=None, description="Cache hits")
    cache_savings: Optional[float] = Field(default=None, description="Cache savings")
