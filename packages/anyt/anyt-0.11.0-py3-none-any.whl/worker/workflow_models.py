"""
Workflow models for the AnyTask Worker system.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from worker.models.workflow_requirements import WorkflowRequirements


class StepStatus(str, Enum):
    """Status of a workflow step."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"


class ProjectScope(str, Enum):
    """Scope level for workflow project operations."""

    WORKSPACE = "workspace"
    PROJECT = "project"


class WorkflowTrigger(BaseModel):
    """Trigger conditions for a workflow."""

    task_created: Optional[Dict[str, List[str]]] = None
    task_updated: Optional[Dict[str, List[str]]] = None


class WorkflowOn(BaseModel):
    """Event triggers for workflow execution."""

    task_created: Optional[Dict[str, Any]] = None
    task_updated: Optional[Dict[str, Any]] = None


class StepAction(BaseModel):
    """Action configuration for a step."""

    model_config = {"populate_by_name": True}

    uses: str  # Action identifier (e.g., 'anyt/claude-code@v1')
    with_: Dict[str, Any] = Field(default_factory=dict, alias="with")
    id: Optional[str] = None


class WorkflowStep(BaseModel):
    """A single step in a workflow."""

    model_config = {"populate_by_name": True}

    name: str
    uses: Optional[str] = None  # For action-based steps
    run: Optional[str] = None  # For command-based steps
    with_: Optional[Dict[str, Any]] = Field(None, alias="with")
    id: Optional[str] = None
    if_: Optional[str] = Field(None, alias="if")  # Conditional execution
    continue_on_error: bool = Field(default=False, alias="continue-on-error")
    timeout_minutes: int = Field(default=30, alias="timeout-minutes")
    env: Optional[Dict[str, str]] = None
    parallel: Optional[List["WorkflowStep"]] = None  # For parallel execution


class WorkflowJob(BaseModel):
    """A job containing multiple steps."""

    model_config = {"populate_by_name": True}

    name: str
    runs_on: str = Field(default="local", alias="runs-on")
    timeout_minutes: int = Field(default=60, alias="timeout-minutes")
    steps: List[WorkflowStep]


# Update forward references for self-referential WorkflowStep
WorkflowStep.model_rebuild()


class WorkflowOnFailure(BaseModel):
    """Actions to take on workflow failure."""

    steps: List[WorkflowStep] = Field(default_factory=lambda: [])


class WorkflowSettings(BaseModel):
    """Workflow execution settings."""

    model_config = {"populate_by_name": True}

    clone_repo: bool = Field(
        default=False,
        description="Clone project repository before workflow execution",
    )
    cleanup_workspace: bool = Field(
        default=True,
        description="Cleanup task workspace after execution",
    )
    project_scope: ProjectScope = Field(
        default=ProjectScope.WORKSPACE,
        description="Scope level for project selection/creation operations",
    )


class Workflow(BaseModel):
    """Complete workflow definition."""

    model_config = {"populate_by_name": True}

    name: str
    description: Optional[str] = None
    on: WorkflowOn
    jobs: Dict[str, WorkflowJob]
    on_failure: Optional[WorkflowOnFailure] = Field(None, alias="on-failure")
    requirements: Optional[WorkflowRequirements] = None
    settings: Optional[WorkflowSettings] = None


class StepResult(BaseModel):
    """Result of a step execution."""

    step_id: str
    step_name: str
    status: StepStatus
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class WorkflowExecution(BaseModel):
    """Execution state of a workflow."""

    workflow_name: str
    task_id: str
    task_identifier: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str  # "running", "success", "failure"
    step_results: List[StepResult] = Field(default_factory=lambda: [])
    context: Dict[str, Any] = Field(default_factory=lambda: {})
    total_tokens: int = 0  # Total LLM tokens used across all steps
