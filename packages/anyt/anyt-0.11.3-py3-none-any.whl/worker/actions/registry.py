"""
Action registry for workflow actions.
"""

from typing import Dict, Optional

from .base import Action
from .cache import CacheAction
from .claude import ClaudeCodeAction, ClaudePromptAction
from .coding_agent import CodingAgentAction
from .control import CheckConditionAction, FailAction
from .git import CheckoutAction, GitCloneAction, GitCommitAction
from .github import CreatePullRequestAction, GitPushAction, MergePullRequestAction
from .local_task import (
    LocalTaskPullAction,
    LocalTaskPushAction,
    LocalTaskReadAction,
    LocalTaskWriteAction,
    TaskValidateSectionsAction,
)
from .plan import PlanSubmitAction
from .pr import (
    PullRequestRegisterAction,
    PullRequestSyncAction,
    PullRequestUpdateAction,
)
from .task import TaskAnalyzeAction, TaskDetailAction, TaskUpdateAction
from .testing import BuildAction, TestAction


class ActionRegistry:
    """Registry of available workflow actions."""

    def __init__(self) -> None:
        """Initialize registry with all available actions."""
        self.actions: Dict[str, Action] = {
            # Git actions
            "anyt/checkout@v1": CheckoutAction(),
            "anyt/git-clone@v1": GitCloneAction(),
            "anyt/git-commit@v1": GitCommitAction(),
            "anyt/git-push@v1": GitPushAction(),
            # GitHub actions
            "anyt/github-pr-create@v1": CreatePullRequestAction(),
            "anyt/github-pr-merge@v1": MergePullRequestAction(),
            # PR tracking actions
            "anyt/pr-register@v1": PullRequestRegisterAction(),
            "anyt/pr-update@v1": PullRequestUpdateAction(),
            "anyt/pr-sync@v1": PullRequestSyncAction(),
            # Cache actions
            "anyt/cache@v1": CacheAction(),
            # Claude/AI actions
            "anyt/claude-prompt@v1": ClaudePromptAction(),
            "anyt/claude-code@v1": ClaudeCodeAction(),
            # Generic coding agent action (dispatches to assigned agent)
            "anyt/coding-agent@v1": CodingAgentAction(),
            # Task actions
            "anyt/task-update@v1": TaskUpdateAction(),
            "anyt/task-analyze@v1": TaskAnalyzeAction(),
            "anyt/task-detail@v1": TaskDetailAction(),
            # Plan actions
            "anyt/plan-submit@v1": PlanSubmitAction(),
            # Testing/Build actions
            "anyt/test@v1": TestAction(),
            "anyt/build@v1": BuildAction(),
            # Local task actions (filesystem-first)
            "anyt/local-task-pull@v1": LocalTaskPullAction(),
            "anyt/local-task-push@v1": LocalTaskPushAction(),
            "anyt/local-task-read@v1": LocalTaskReadAction(),
            "anyt/local-task-write@v1": LocalTaskWriteAction(),
            # Task validation actions
            "anyt/task-validate-sections@v1": TaskValidateSectionsAction(),
            # Control flow actions
            "anyt/fail@v1": FailAction(),
            "anyt/check-condition@v1": CheckConditionAction(),
        }

    def get_action(self, action_name: str) -> Optional[Action]:
        """Get an action by name.

        Args:
            action_name: The name of the action (e.g., "anyt/checkout@v1")

        Returns:
            The action instance or None if not found
        """
        return self.actions.get(action_name)

    def register_action(self, name: str, action: Action) -> None:
        """Register a custom action.

        Args:
            name: The action name (e.g., "custom/my-action@v1")
            action: The action instance to register
        """
        self.actions[name] = action

    def list_actions(self) -> list[str]:
        """Get list of all registered action names.

        Returns:
            List of action names
        """
        return sorted(self.actions.keys())
