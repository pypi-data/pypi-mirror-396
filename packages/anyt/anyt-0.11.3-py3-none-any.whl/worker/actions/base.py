"""
Base action class for workflow actions.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from ..context import ExecutionContext


class Action(ABC):
    """Base class for workflow actions."""

    @abstractmethod
    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute the action and return outputs."""
        pass
