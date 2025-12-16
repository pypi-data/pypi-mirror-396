"""
Coding agent abstraction layer.

This package provides a unified interface for different coding CLI tools
(Claude, Codex, Gemini CLI) with consistent command building and
output parsing.
"""

from .base import CodeExecutionResult, CodingAgent
from .claude import ClaudeCodeAgent
from .codex import CodexAgent
from .config import (
    AgentCLIConfig,
    get_agent_config,
    get_backend_type,
    list_backend_types,
)
from .detector import (
    AgentDetector,
    DetectedAgent,
    get_install_instructions,
    interactive_agent_setup,
    print_detection_table,
)
from .gemini import GeminiCLIAgent
from .registry import CodingAgentRegistry

__all__ = [
    "CodingAgent",
    "CodeExecutionResult",
    "AgentCLIConfig",
    "get_agent_config",
    "get_backend_type",
    "list_backend_types",
    "ClaudeCodeAgent",
    "CodexAgent",
    "GeminiCLIAgent",
    "CodingAgentRegistry",
    "AgentDetector",
    "DetectedAgent",
    "get_install_instructions",
    "interactive_agent_setup",
    "print_detection_table",
]
