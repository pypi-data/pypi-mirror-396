"""Workflow requirements models for defining and validating workflow prerequisites."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class RequirementType(str, Enum):
    """Types of requirements that can be checked."""

    COMMAND = "command"
    ENV_VAR = "env_var"
    GIT_CONTEXT = "git_context"
    FILE_SYSTEM = "file_system"


class GitContextType(str, Enum):
    """Types of git context checks."""

    REPOSITORY = "repository"  # Check if in a git repository
    REMOTE = "remote"  # Check for specific remote
    BRANCH = "branch"  # Check for specific branch


class FileSystemType(str, Enum):
    """Types of file system checks."""

    DIRECTORY = "directory"
    FILE = "file"


class CheckType(str, Enum):
    """Special check types for requirements that aren't simple command checks."""

    CODING_AGENT = "coding_agent"  # Check if any coding agent is installed
    GH_AUTH = "gh_auth"  # Check if GitHub CLI is authenticated
    CLAUDE_AUTH = "claude_auth"  # Check if Claude CLI has API token configured


class CommandRequirement(BaseModel):
    """Requirement for a command-line tool to be installed."""

    name: str = Field(..., description="Name of the command (e.g., 'git', 'gh')")
    check_command: str | None = Field(
        None,
        description="Optional command to check version or validate installation (e.g., 'git --version')",
    )
    check_type: CheckType | None = Field(
        None,
        description="Special check type for non-standard requirements (e.g., 'coding_agent')",
    )
    install_instructions: dict[str, str] = Field(
        default_factory=dict,
        description="Installation instructions per OS (e.g., {'darwin': 'brew install git', 'linux': 'apt install git'})",
    )
    required: bool = Field(
        True, description="Whether this requirement is mandatory or optional"
    )

    @field_validator("install_instructions")
    @classmethod
    def validate_install_instructions(cls, v: dict[str, str]) -> dict[str, str]:
        """Validate that install instructions use standard OS names."""
        valid_os = {"darwin", "linux", "windows"}
        for os_name in v.keys():
            if os_name not in valid_os:
                raise ValueError(
                    f"Invalid OS name '{os_name}'. Must be one of: {valid_os}"
                )
        return v

    model_config = {"frozen": False}


class EnvVarRequirement(BaseModel):
    """Requirement for an environment variable to be set."""

    name: str = Field(..., description="Name of the environment variable")
    check_command: str | None = Field(
        None,
        description="Optional command to validate the env var (e.g., 'gh auth status' for GITHUB_TOKEN)",
    )
    setup_instructions: str = Field(
        ..., description="Instructions for setting up the environment variable"
    )
    required: bool = Field(
        True, description="Whether this requirement is mandatory or optional"
    )

    model_config = {"frozen": False}


class GitContextRequirement(BaseModel):
    """Requirement for specific git repository context."""

    context_type: GitContextType = Field(..., description="Type of git context check")
    value: str | None = Field(
        None,
        description="Expected value (e.g., remote name, branch name). Not needed for 'repository' type.",
    )
    check_command: str | None = Field(
        None,
        description="Optional custom command to check git context",
    )
    required: bool = Field(
        True, description="Whether this requirement is mandatory or optional"
    )

    @model_validator(mode="after")
    def validate_value_required(self) -> "GitContextRequirement":
        """Validate that value is provided when required by context type."""
        if self.context_type in (GitContextType.REMOTE, GitContextType.BRANCH):
            if not self.value:
                raise ValueError(
                    f"value is required for context_type '{self.context_type}'"
                )
        return self

    model_config = {"frozen": False}


class FileSystemRequirement(BaseModel):
    """Requirement for files or directories to exist."""

    fs_type: FileSystemType = Field(..., description="Type of file system check")
    path: str = Field(..., description="Path to the file or directory")
    permissions: str | None = Field(
        None,
        description="Optional required permissions (e.g., 'r', 'rw', 'rwx')",
    )
    required: bool = Field(
        True, description="Whether this requirement is mandatory or optional"
    )

    model_config = {"frozen": False}


class RequirementCheckResult(BaseModel):
    """Result of a requirement check."""

    success: bool = Field(..., description="Whether the requirement check passed")
    message: str = Field(..., description="Human-readable message about the check")
    fix_instructions: str | None = Field(
        None, description="Instructions for fixing a failed check"
    )
    warning: bool = Field(False, description="Whether this is a warning (soft failure)")
    from_cache: bool = Field(False, description="Whether this result came from cache")

    model_config = {"frozen": False}


class WorkflowRequirements(BaseModel):
    """Aggregate model containing all requirement types for a workflow."""

    commands: list[CommandRequirement] = Field(
        default_factory=list, description="Required command-line tools"
    )
    env_vars: list[EnvVarRequirement] = Field(
        default_factory=list, description="Required environment variables"
    )
    git_context: list[GitContextRequirement] = Field(
        default_factory=list, description="Required git context"
    )
    file_system: list[FileSystemRequirement] = Field(
        default_factory=list, description="Required files or directories"
    )

    def has_requirements(self) -> bool:
        """Check if any requirements are defined."""
        return bool(
            self.commands or self.env_vars or self.git_context or self.file_system
        )

    def count_requirements(self) -> int:
        """Count total number of requirements."""
        return (
            len(self.commands)
            + len(self.env_vars)
            + len(self.git_context)
            + len(self.file_system)
        )

    model_config = {"frozen": False}
