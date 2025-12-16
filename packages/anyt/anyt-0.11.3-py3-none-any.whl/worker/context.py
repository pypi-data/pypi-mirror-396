"""
Execution context for workflow steps.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from sdk.generated.models.CodingAgentSettings import CodingAgentSettings


class ExecutionContext:
    """Context passed to workflow steps during execution."""

    def __init__(
        self,
        task: Dict[str, Any],
        workspace_dir: Path,
        outputs: Dict[str, Any],
        env: Dict[str, str],
        workspace_id: int,
        coding_agent_settings: Optional["CodingAgentSettings"] = None,
    ):
        """
        Initialize execution context.

        Args:
            task: Task data (id, identifier, title, description, etc.)
            workspace_dir: Path to workspace directory
            outputs: Outputs from previous steps (keyed by step ID)
            env: Environment variables
            workspace_id: Workspace ID for API calls (required)
            coding_agent_settings: Optional coding agent settings from backend
        """
        self.task = task
        self.workspace_dir = workspace_dir
        self.outputs = outputs
        self.env = env
        self.workspace_id = workspace_id
        self.coding_agent_settings = coding_agent_settings

    def get_task_field(self, field: str, default: Any = None) -> Any:
        """Get a field from the task data."""
        return self.task.get(field, default)

    def get_coding_agent_model(self) -> Optional[str]:
        """Get the model from coding agent settings if available."""
        if self.coding_agent_settings and self.coding_agent_settings.model:
            return self.coding_agent_settings.model
        return None

    def get_step_output(self, step_id: str, key: str, default: Any = None) -> Any:
        """Get an output value from a previous step."""
        step_outputs = self.outputs.get(step_id, {})
        return step_outputs.get(key, default)

    def set_output(self, step_id: str, key: str, value: Any) -> None:
        """Set an output value for the current step."""
        if step_id not in self.outputs:
            self.outputs[step_id] = {}
        self.outputs[step_id][key] = value
