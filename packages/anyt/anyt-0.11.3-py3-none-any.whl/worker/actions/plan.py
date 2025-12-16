"""
Plan submission workflow actions.
"""

import logging
import os
from typing import Any, Dict

from sdk.generated.api_config import APIConfig
from sdk.generated.models.TaskUpdate import TaskUpdate
from sdk.generated.services.async_Tasks_service import updateTask

from .base import Action
from ..context import ExecutionContext

logger = logging.getLogger(__name__)


class PlanSubmitAction(Action):
    """Submit an implementation plan for a task.

    This action saves an implementation plan to the task via the update API.
    The plan is stored as a simple text field on the task (no separate review workflow).
    """

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Submit plan to AnyTask.

        Args:
            params: Action parameters
                - plan (required): Implementation plan content (markdown)
            ctx: Execution context with task data

        Returns:
            Dict with keys:
                - submitted: bool (True if plan was submitted)
                - task_id: int (task ID from response)

        Raises:
            ValueError: If required parameters are missing
        """
        # Get required plan parameter
        plan = params.get("plan")
        if not plan:
            raise ValueError("plan parameter is required")

        # Get task identifier from context
        task_identifier = ctx.task.get("identifier")
        if not task_identifier:
            raise ValueError("Task identifier not found in context")

        # Get workspace_id from context
        workspace_id = ctx.workspace_id
        if not workspace_id:
            raise ValueError("Workspace ID not found in context")

        # Get API configuration from context or environment
        ctx_env = ctx.env or {}
        api_config = self._get_api_config(ctx_env)

        # Create update request with implementation_plan
        request = TaskUpdate(
            implementation_plan=plan,
        )

        # Call the API to update the task
        try:
            response = await updateTask(
                api_config_override=api_config,
                workspace_id=workspace_id,
                task_identifier=task_identifier,
                data=request,
                X_API_Key=self._get_api_key(ctx_env),
            )

            return {
                "submitted": True,
                "task_id": response.id,
            }
        except Exception as e:
            logger.error(f"Failed to submit plan for task {task_identifier}: {e}")
            raise

    def _get_api_config(self, ctx_env: Dict[str, str]) -> APIConfig:
        """Get API configuration from context or environment."""
        api_url = (
            ctx_env.get("ANYT_API_URL")
            or os.getenv("ANYT_API_URL")
            or "https://api.anyt.dev"
        )
        return APIConfig(base_path=api_url)

    def _get_api_key(self, ctx_env: Dict[str, str]) -> str | None:
        """Get API key from context or environment."""
        return ctx_env.get("ANYT_API_KEY") or os.getenv("ANYT_API_KEY")
