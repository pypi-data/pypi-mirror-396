"""
Agent detection and interactive setup.

This module provides functionality to detect installed coding agents,
display their status, and interactively confirm agent selection.
"""

import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Optional

from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from .config import AGENT_CONFIGS, AgentCLIConfig


@dataclass
class DetectedAgent:
    """Information about a detected coding agent.

    Attributes:
        config: The agent's CLI configuration.
        installed: Whether the agent CLI is installed.
        version: The detected version string (if available).
        path: The path to the CLI executable (if installed).
    """

    config: AgentCLIConfig
    installed: bool
    version: Optional[str] = None
    path: Optional[str] = None


class AgentDetector:
    """Detects installed coding agents by checking CLI availability."""

    # Version extraction patterns for each agent
    VERSION_PATTERNS: dict[str, str] = {
        "claude": r"(\d+\.\d+\.\d+)",
        "codex": r"(\d+\.\d+\.\d+)",
        "gemini": r"(\d+\.\d+\.\d+)",
    }

    # Install instructions for each agent
    INSTALL_INSTRUCTIONS: dict[str, str] = {
        "claude": "npm install -g @anthropic-ai/claude-code",
        "codex": "npm install -g @openai/codex",
        "gemini": "npm install -g @anthropic-ai/gemini-cli",
    }

    def detect_all(self) -> list[DetectedAgent]:
        """Detect all configured coding agents.

        Returns:
            List of DetectedAgent objects for each configured agent.
        """
        results: list[DetectedAgent] = []

        for agent_name, config in AGENT_CONFIGS.items():
            path = shutil.which(config.cli_command)
            installed = path is not None

            version = None
            if installed and path:
                version = self._get_version(config.cli_command, agent_name)

            results.append(
                DetectedAgent(
                    config=config,
                    installed=installed,
                    version=version,
                    path=path,
                )
            )

        return results

    def _get_version(self, cli_command: str, agent_name: str) -> Optional[str]:
        """Get the version of an installed agent CLI.

        Args:
            cli_command: The CLI command to check.
            agent_name: The agent identifier for pattern lookup.

        Returns:
            The version string if parseable, None otherwise.
        """
        try:
            # Try --version first
            result = subprocess.run(
                [cli_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            output = result.stdout or result.stderr

            # If --version didn't work, try --help
            if not output or result.returncode != 0:
                result = subprocess.run(
                    [cli_command, "--help"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                output = result.stdout or result.stderr

            # Parse version using agent-specific pattern
            pattern = self.VERSION_PATTERNS.get(agent_name, r"(\d+\.\d+\.\d+)")
            match = re.search(pattern, output)
            if match:
                return match.group(1)

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
            pass

        return None


def print_detection_table(
    agents: list[DetectedAgent], console: Optional[Console] = None
) -> None:
    """Print a table showing detected agent status.

    Args:
        agents: List of detected agents to display.
        console: Rich console to use for output (creates new one if None).
    """
    if console is None:
        console = Console()

    table = Table(title="Coding Agent Detection")
    table.add_column("Agent", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Version")
    table.add_column("Path")

    for agent in agents:
        status = (
            "[green]✓ Installed[/green]"
            if agent.installed
            else "[red]✗ Not Found[/red]"
        )
        version = agent.version or "-"
        path = agent.path or "-"

        table.add_row(agent.config.name, status, version, path)

    console.print(table)


def get_install_instructions(agent_name: str) -> str:
    """Get installation instructions for an agent.

    Args:
        agent_name: The agent identifier.

    Returns:
        Installation instruction string.
    """
    return AgentDetector.INSTALL_INSTRUCTIONS.get(
        agent_name.lower(), f"Visit the {agent_name} documentation for installation"
    )


def interactive_agent_setup(console: Optional[Console] = None) -> list[str]:
    """Run interactive agent setup flow.

    Detects all agents, displays their status, and prompts for confirmation.

    Args:
        console: Rich console to use for output (creates new one if None).

    Returns:
        List of backend CodingAgentType values (e.g., ['claude_code', 'codex']).
        These values can be passed directly to the backend API.

    Raises:
        SystemExit: If no agents are installed or user cancels.
    """
    if console is None:
        console = Console()

    detector = AgentDetector()
    agents = detector.detect_all()

    # Print detection results
    console.print()
    print_detection_table(agents, console)
    console.print()

    # Check if any agents are installed
    installed_agents = [a for a in agents if a.installed]

    if not installed_agents:
        console.print("[bold red]Error:[/bold red] No coding agents installed!")
        console.print()
        console.print("Please install at least one of the following:")
        console.print()

        for agent_name in AgentDetector.INSTALL_INSTRUCTIONS:
            instruction = get_install_instructions(agent_name)
            config = AGENT_CONFIGS.get(agent_name)
            name = config.name if config else agent_name
            console.print(f"  [cyan]{name}[/cyan]: {instruction}")

        console.print()
        raise SystemExit(1)

    # Show summary of installed agents
    agent_names = [a.config.name for a in installed_agents]
    console.print(
        f"[green]Found {len(installed_agents)} installed agent(s):[/green] "
        f"{', '.join(agent_names)}"
    )
    console.print()

    # Prompt for confirmation
    if not Confirm.ask("Start worker with detected agents?", default=True):
        console.print("[yellow]Cancelled.[/yellow]")
        raise SystemExit(0)

    # Return list of backend CodingAgentType values for API compatibility
    # Maps from installed agent configs to their backend_type values
    return [
        config.backend_type
        for agent_name, config in AGENT_CONFIGS.items()
        if any(a.config.cli_command == config.cli_command for a in installed_agents)
    ]
