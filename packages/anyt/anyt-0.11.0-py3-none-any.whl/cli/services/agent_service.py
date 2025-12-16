"""Agent service for managing coding agent integrations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Self
import shutil


class AgentType(str, Enum):
    """Supported coding agent types."""

    CLAUDE = "claude"
    CODEX = "codex"
    GEMINI = "gemini"


@dataclass
class AgentInfo:
    """Information about a coding agent."""

    type: AgentType
    name: str
    description: str
    target_dir: str  # Relative to user's home or cwd
    commands_subdir: str  # Subdirectory for commands (empty string for flat structure)
    use_home_dir: bool = False  # If True, install to home directory instead of cwd
    file_prefix: str = ""  # Prefix for command files (used for shared directories)
    file_extension: str = "md"  # File extension for commands (md, toml, etc.)

    @property
    def display_name(self) -> str:
        """Get display name for the agent."""
        return self.name


# Registry of supported agents
AGENT_REGISTRY: dict[AgentType, AgentInfo] = {
    AgentType.CLAUDE: AgentInfo(
        type=AgentType.CLAUDE,
        name="Claude Code",
        description="Anthropic's Claude Code CLI assistant",
        target_dir=".claude",
        commands_subdir="commands/anyt",
    ),
    AgentType.CODEX: AgentInfo(
        type=AgentType.CODEX,
        name="Codex CLI",
        description="OpenAI Codex CLI assistant",
        target_dir=".codex",
        commands_subdir="prompts",  # Codex uses prompts/ directly, no subdirs
        use_home_dir=True,  # Codex installs to ~/.codex/prompts/
        file_prefix="anyt-",  # Prefix files to namespace them
    ),
    AgentType.GEMINI: AgentInfo(
        type=AgentType.GEMINI,
        name="Gemini CLI",
        description="Google Gemini CLI assistant",
        target_dir=".gemini",
        commands_subdir="commands/anyt",  # Subdirectory creates /anyt:cmd namespace
        file_extension="toml",  # Gemini uses TOML format
    ),
}


@dataclass
class InstallResult:
    """Result of an install operation."""

    success: bool
    installed_commands: list[str]
    target_path: Path
    message: str
    was_override: bool = False


@dataclass
class UninstallResult:
    """Result of an uninstall operation."""

    success: bool
    removed_commands: list[str]
    message: str


@dataclass
class AgentStatus:
    """Status of an agent installation."""

    agent: AgentInfo
    installed: bool
    installed_commands: list[str]
    target_path: Path | None


class AgentIntegration(ABC):
    """Base class for agent integrations."""

    def __init__(self, agent_info: AgentInfo, base_path: Path | None = None):
        """Initialize agent integration.

        Args:
            agent_info: Information about this agent
            base_path: Base path for installation (default: current working directory)
        """
        self.agent_info = agent_info
        self.base_path = base_path or Path.cwd()

    @property
    def target_path(self) -> Path:
        """Get the full target path for commands."""
        if self.agent_info.use_home_dir:
            base = Path.home()
        else:
            base = self.base_path

        path = base / self.agent_info.target_dir
        if self.agent_info.commands_subdir:
            path = path / self.agent_info.commands_subdir
        return path

    @property
    @abstractmethod
    def source_commands_path(self) -> Path:
        """Get the path to bundled command templates."""
        ...

    def get_available_commands(self) -> list[str]:
        """Get list of available command templates."""
        source = self.source_commands_path
        if not source.exists():
            return []
        ext = self.agent_info.file_extension
        return [f.name for f in source.glob(f"*.{ext}") if f.is_file()]

    def get_installed_commands(self) -> list[str]:
        """Get list of installed commands."""
        if not self.target_path.exists():
            return []
        ext = self.agent_info.file_extension
        return [f.name for f in self.target_path.glob(f"*.{ext}") if f.is_file()]

    def is_installed(self) -> bool:
        """Check if agent commands are installed."""
        return self.target_path.exists() and len(self.get_installed_commands()) > 0

    def get_status(self) -> AgentStatus:
        """Get the installation status of this agent."""
        return AgentStatus(
            agent=self.agent_info,
            installed=self.is_installed(),
            installed_commands=self.get_installed_commands(),
            target_path=self.target_path if self.is_installed() else None,
        )

    def install(self, force: bool = False) -> InstallResult:
        """Install agent commands.

        Args:
            force: If True, override existing commands without prompting

        Returns:
            InstallResult with details of the operation
        """
        source = self.source_commands_path
        if not source.exists():
            return InstallResult(
                success=False,
                installed_commands=[],
                target_path=self.target_path,
                message=f"No command templates found for {self.agent_info.name}",
            )

        available = self.get_available_commands()
        if not available:
            return InstallResult(
                success=False,
                installed_commands=[],
                target_path=self.target_path,
                message=f"No command templates available for {self.agent_info.name}",
            )

        was_override = self.target_path.exists()
        if was_override and not force:
            # Caller should check and prompt user
            return InstallResult(
                success=False,
                installed_commands=[],
                target_path=self.target_path,
                message=f"Commands already exist at {self.target_path}. Use --force to override.",
                was_override=False,
            )

        # Create target directory
        self.target_path.mkdir(parents=True, exist_ok=True)

        # Copy command files
        installed = []
        ext = self.agent_info.file_extension
        for cmd_file in source.glob(f"*.{ext}"):
            target_file = self.target_path / cmd_file.name
            shutil.copy2(cmd_file, target_file)
            installed.append(cmd_file.name)

        return InstallResult(
            success=True,
            installed_commands=installed,
            target_path=self.target_path,
            message=f"Installed {len(installed)} commands to {self.target_path}",
            was_override=was_override,
        )

    def uninstall(self) -> UninstallResult:
        """Uninstall agent commands.

        Returns:
            UninstallResult with details of the operation
        """
        if not self.target_path.exists():
            return UninstallResult(
                success=False,
                removed_commands=[],
                message=f"No commands installed at {self.target_path}",
            )

        removed = self.get_installed_commands()

        # Remove the anyt commands directory
        shutil.rmtree(self.target_path)

        return UninstallResult(
            success=True,
            removed_commands=removed,
            message=f"Removed {len(removed)} commands from {self.target_path}",
        )


class ClaudeIntegration(AgentIntegration):
    """Claude Code agent integration."""

    def __init__(self, base_path: Path | None = None):
        super().__init__(AGENT_REGISTRY[AgentType.CLAUDE], base_path)

    @property
    def source_commands_path(self) -> Path:
        """Get the path to bundled Claude command templates."""
        # Commands are bundled in the package data directory
        return Path(__file__).parent.parent / "data" / "agent_commands" / "claude"


class CodexIntegration(AgentIntegration):
    """Codex CLI agent integration.

    Codex uses a global prompts directory (~/.codex/prompts/) that may be shared
    with other tools. Commands are prefixed with 'anyt-' to namespace them.
    """

    def __init__(self, base_path: Path | None = None):
        super().__init__(AGENT_REGISTRY[AgentType.CODEX], base_path)

    @property
    def source_commands_path(self) -> Path:
        """Get the path to bundled Codex command templates."""
        return Path(__file__).parent.parent / "data" / "agent_commands" / "codex"

    def get_installed_commands(self) -> list[str]:
        """Get list of installed anyt commands (prefixed files only)."""
        if not self.target_path.exists():
            return []
        prefix = self.agent_info.file_prefix
        ext = self.agent_info.file_extension
        return [
            f.name for f in self.target_path.glob(f"{prefix}*.{ext}") if f.is_file()
        ]

    def is_installed(self) -> bool:
        """Check if anyt commands are installed."""
        return len(self.get_installed_commands()) > 0

    def install(self, force: bool = False) -> InstallResult:
        """Install agent commands to shared prompts directory.

        Only overwrites anyt-prefixed files, leaving other prompts intact.
        """
        source = self.source_commands_path
        if not source.exists():
            return InstallResult(
                success=False,
                installed_commands=[],
                target_path=self.target_path,
                message=f"No command templates found for {self.agent_info.name}",
            )

        available = self.get_available_commands()
        if not available:
            return InstallResult(
                success=False,
                installed_commands=[],
                target_path=self.target_path,
                message=f"No command templates available for {self.agent_info.name}",
            )

        # Check if our commands already exist
        existing = self.get_installed_commands()
        was_override = len(existing) > 0
        if was_override and not force:
            return InstallResult(
                success=False,
                installed_commands=[],
                target_path=self.target_path,
                message=f"Commands already exist at {self.target_path}. Use --force to override.",
                was_override=False,
            )

        # Create target directory
        self.target_path.mkdir(parents=True, exist_ok=True)

        # Copy command files
        installed = []
        ext = self.agent_info.file_extension
        for cmd_file in source.glob(f"*.{ext}"):
            target_file = self.target_path / cmd_file.name
            shutil.copy2(cmd_file, target_file)
            installed.append(cmd_file.name)

        return InstallResult(
            success=True,
            installed_commands=installed,
            target_path=self.target_path,
            message=f"Installed {len(installed)} commands to {self.target_path}",
            was_override=was_override,
        )

    def uninstall(self) -> UninstallResult:
        """Uninstall only anyt-prefixed commands, preserving other prompts."""
        installed = self.get_installed_commands()
        if not installed:
            return UninstallResult(
                success=False,
                removed_commands=[],
                message=f"No anyt commands installed at {self.target_path}",
            )

        # Remove only anyt-prefixed files
        for cmd_name in installed:
            cmd_path = self.target_path / cmd_name
            if cmd_path.exists():
                cmd_path.unlink()

        return UninstallResult(
            success=True,
            removed_commands=installed,
            message=f"Removed {len(installed)} commands from {self.target_path}",
        )


class GeminiIntegration(AgentIntegration):
    """Gemini CLI agent integration."""

    def __init__(self, base_path: Path | None = None):
        super().__init__(AGENT_REGISTRY[AgentType.GEMINI], base_path)

    @property
    def source_commands_path(self) -> Path:
        """Get the path to bundled Gemini command templates."""
        return Path(__file__).parent.parent / "data" / "agent_commands" / "gemini"


class AgentService:
    """Service for managing coding agent integrations."""

    def __init__(self, base_path: Path | None = None):
        """Initialize agent service.

        Args:
            base_path: Base path for agent installations (default: current working directory)
        """
        self.base_path = base_path or Path.cwd()
        self._integrations: dict[AgentType, AgentIntegration] = {
            AgentType.CLAUDE: ClaudeIntegration(self.base_path),
            AgentType.CODEX: CodexIntegration(self.base_path),
            AgentType.GEMINI: GeminiIntegration(self.base_path),
        }

    @classmethod
    def from_config(cls) -> Self:
        """Create service from current directory."""
        return cls()

    def get_supported_agents(self) -> list[AgentInfo]:
        """Get list of all supported agents."""
        return list(AGENT_REGISTRY.values())

    def get_agent_info(self, agent_type: str) -> AgentInfo | None:
        """Get info for a specific agent type."""
        try:
            return AGENT_REGISTRY[AgentType(agent_type)]
        except (ValueError, KeyError):
            return None

    def get_integration(self, agent_type: str) -> AgentIntegration | None:
        """Get the integration for a specific agent type."""
        try:
            return self._integrations[AgentType(agent_type)]
        except (ValueError, KeyError):
            return None

    def list_agents(self) -> list[AgentStatus]:
        """List all agents with their installation status."""
        return [integration.get_status() for integration in self._integrations.values()]

    def install(self, agent_type: str, force: bool = False) -> InstallResult:
        """Install commands for a specific agent.

        Args:
            agent_type: Type of agent (e.g., "claude")
            force: If True, override existing commands

        Returns:
            InstallResult with details of the operation
        """
        integration = self.get_integration(agent_type)
        if not integration:
            return InstallResult(
                success=False,
                installed_commands=[],
                target_path=Path(),
                message=f"Unknown agent type: {agent_type}. Supported: {', '.join(t.value for t in AgentType)}",
            )

        return integration.install(force=force)

    def uninstall(self, agent_type: str) -> UninstallResult:
        """Uninstall commands for a specific agent.

        Args:
            agent_type: Type of agent (e.g., "claude")

        Returns:
            UninstallResult with details of the operation
        """
        integration = self.get_integration(agent_type)
        if not integration:
            return UninstallResult(
                success=False,
                removed_commands=[],
                message=f"Unknown agent type: {agent_type}. Supported: {', '.join(t.value for t in AgentType)}",
            )

        return integration.uninstall()

    def check_existing(self, agent_type: str) -> bool:
        """Check if commands already exist for an agent.

        Args:
            agent_type: Type of agent (e.g., "claude")

        Returns:
            True if commands exist, False otherwise
        """
        integration = self.get_integration(agent_type)
        if not integration:
            return False
        return integration.is_installed()
