"""
Registry for coding agent implementations.
"""

from typing import Optional

from .base import CodingAgent
from .claude import ClaudeCodeAgent
from .codex import CodexAgent
from .gemini import GeminiCLIAgent


class CodingAgentRegistry:
    """Registry of available coding agent implementations.

    Provides a central point for looking up and instantiating coding agents
    by their identifier.
    """

    # Map of agent identifiers to their classes
    _agent_classes: dict[str, type[CodingAgent]] = {
        "claude": ClaudeCodeAgent,
        "codex": CodexAgent,
        "gemini": GeminiCLIAgent,
    }

    # Cache of instantiated agents
    _instances: dict[str, CodingAgent] = {}

    @classmethod
    def get_agent(cls, agent_name: str) -> Optional[CodingAgent]:
        """Get a coding agent by name.

        Args:
            agent_name: The agent identifier (e.g., 'claude', 'codex').

        Returns:
            The CodingAgent instance, or None if not found.
        """
        name = agent_name.lower()

        # Return cached instance if available
        if name in cls._instances:
            return cls._instances[name]

        # Create new instance if agent class exists
        if name in cls._agent_classes:
            agent = cls._agent_classes[name]()
            cls._instances[name] = agent
            return agent

        return None

    @classmethod
    def list_agents(cls) -> list[str]:
        """Get list of all registered agent names.

        Returns:
            List of agent identifiers.
        """
        return sorted(cls._agent_classes.keys())

    @classmethod
    def register_agent(cls, name: str, agent_class: type[CodingAgent]) -> None:
        """Register a custom agent implementation.

        Args:
            name: The agent identifier to register under.
            agent_class: The CodingAgent subclass to register.
        """
        cls._agent_classes[name.lower()] = agent_class
        # Clear cached instance if exists
        if name.lower() in cls._instances:
            del cls._instances[name.lower()]

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the instance cache.

        Useful for testing or when agent configurations change.
        """
        cls._instances.clear()
