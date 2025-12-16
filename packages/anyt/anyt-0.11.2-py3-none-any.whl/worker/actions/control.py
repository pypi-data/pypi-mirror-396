"""
Control flow actions for workflow execution.
"""

from typing import Any, Dict

from rich.markup import escape

from cli.commands.console import console
from .base import Action
from ..context import ExecutionContext


class FailAction(Action):
    """Fail the workflow with a message.

    This action always raises an exception to stop workflow execution.
    Use with 'if:' condition to conditionally fail.
    """

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Fail the workflow with the given message.

        Args:
            params: Action parameters
                - message (required): Error message to display
            ctx: Execution context

        Raises:
            RuntimeError: Always raised to fail the workflow
        """
        message = params.get("message", "Workflow failed")

        # Display failure message
        console.print(f"  [red]✗ {escape(message)}[/red]")

        # Raise exception to stop workflow
        raise RuntimeError(message)


class CheckConditionAction(Action):
    """Check a condition and optionally fail if met.

    This action evaluates a condition and can fail the workflow
    if the condition is true. Useful for guard conditions.
    """

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Check condition and optionally fail.

        Args:
            params: Action parameters
                - condition (required): Boolean condition (already evaluated by workflow)
                - fail_message (optional): Message if condition fails
                - fail_on_true (optional, default: true): Fail when condition is true
            ctx: Execution context

        Returns:
            Dict with keys:
                - condition_met: bool (result of condition evaluation)

        Raises:
            RuntimeError: If condition is met and fail_on_true is true
        """
        # The condition is already evaluated by the workflow expression evaluator
        # when passed as a parameter, so we receive the actual boolean value
        condition = params.get("condition", False)
        fail_message = params.get("fail_message", "Condition check failed")
        fail_on_true = params.get("fail_on_true", True)

        # Handle string 'true'/'false' from template interpolation
        if isinstance(condition, str):
            condition = condition.lower() == "true"

        if condition and fail_on_true:
            console.print(f"  [red]✗ {escape(fail_message)}[/red]")
            raise RuntimeError(fail_message)

        return {
            "condition_met": condition,
        }
