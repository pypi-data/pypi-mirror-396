"""Workflow manifest loader for loading workflow requirements from YAML files."""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError

from worker.models.workflow_requirements import (
    GitContextType,
    WorkflowRequirements,
)


class WorkflowManifest(BaseModel):
    """Complete workflow manifest including metadata."""

    name: str = Field(..., description="Display name of the workflow")
    description: str = Field(..., description="Description of the workflow purpose")
    version: str = Field(..., description="Version of the manifest schema")
    requirements: WorkflowRequirements = Field(..., description="Workflow requirements")

    model_config = {"frozen": False}


class ManifestLoadError(Exception):
    """Error loading or parsing workflow manifest."""

    pass


class WorkflowManifestLoader:
    """Loader for workflow manifests from YAML files."""

    def __init__(self, workflows_dir: Path | None = None):
        """Initialize manifest loader.

        Args:
            workflows_dir: Directory containing workflow YAML files.
                          Defaults to .anyt/workflows/ in current directory.
        """
        self.workflows_dir = workflows_dir or Path.cwd() / ".anyt" / "workflows"

    def load(self, workflow_name: str) -> WorkflowManifest:
        """Load workflow manifest from YAML file.

        Args:
            workflow_name: Name of the workflow (without .yaml extension)

        Returns:
            WorkflowManifest with parsed requirements

        Raises:
            ManifestLoadError: If manifest cannot be loaded or parsed
        """
        manifest_path = self.workflows_dir / f"{workflow_name}.yaml"

        if not manifest_path.exists():
            raise ManifestLoadError(
                f"Workflow manifest not found: {manifest_path}\n"
                f"Available workflows: {', '.join(self.list_workflows())}"
            )

        try:
            with open(manifest_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ManifestLoadError(f"Invalid YAML in {manifest_path}: {e}") from e
        except Exception as e:  # noqa: BLE001 - Intentionally broad: wrap any I/O error
            # Wrap any file I/O error in ManifestLoadError with context
            raise ManifestLoadError(
                f"Error reading manifest {manifest_path}: {e}"
            ) from e

        if not isinstance(data, dict):
            raise ManifestLoadError(
                f"Invalid manifest format in {manifest_path}: expected dictionary"
            )

        # Transform YAML structure to match our Pydantic models
        transformed_data = self._transform_manifest_data(data)

        try:
            return WorkflowManifest.model_validate(transformed_data)
        except ValidationError as e:
            raise ManifestLoadError(
                f"Invalid manifest schema in {manifest_path}: {e}"
            ) from e

    def _transform_manifest_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform YAML manifest data to match Pydantic model structure.

        The YAML uses simplified field names that need to be mapped to
        the model's field names.
        """
        transformed: dict[str, Any] = {
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "version": data.get("version", "1.0"),
            "requirements": {},
        }

        requirements = data.get("requirements", {})

        # Transform commands
        if "commands" in requirements:
            transformed["requirements"]["commands"] = [
                self._transform_command(cmd) for cmd in requirements["commands"]
            ]

        # Transform env_vars
        if "env_vars" in requirements:
            transformed["requirements"]["env_vars"] = [
                self._transform_env_var(env) for env in requirements["env_vars"]
            ]

        # Transform git_context
        if "git_context" in requirements:
            transformed["requirements"]["git_context"] = [
                self._transform_git_context(ctx) for ctx in requirements["git_context"]
            ]

        return transformed

    def _transform_command(self, cmd: dict[str, Any]) -> dict[str, Any]:
        """Transform command requirement from YAML to model format."""
        transformed: dict[str, Any] = {
            "name": cmd.get("name", ""),
            "required": cmd.get("required", True),
        }

        # Map 'check' to 'check_command'
        if "check" in cmd:
            transformed["check_command"] = cmd["check"]

        # Map 'install' to 'install_instructions' with OS name normalization
        if "install" in cmd:
            install_map = cmd["install"]
            # Normalize OS names
            normalized: dict[str, str] = {}
            for os_name, instruction in install_map.items():
                # Map common OS name variations to our standard names
                normalized_name = self._normalize_os_name(os_name)
                normalized[normalized_name] = instruction
            transformed["install_instructions"] = normalized

        return transformed

    def _transform_env_var(self, env: dict[str, Any]) -> dict[str, Any]:
        """Transform env var requirement from YAML to model format."""
        transformed: dict[str, Any] = {
            "name": env.get("name", ""),
            "required": env.get("required", True),
        }

        # Map 'check' to 'check_command'
        if "check" in env:
            transformed["check_command"] = env["check"]

        # Map 'setup' to 'setup_instructions' or use error message
        if "setup" in env:
            transformed["setup_instructions"] = env["setup"]
        elif "error" in env:
            transformed["setup_instructions"] = env["error"]
        else:
            # Default setup instruction
            transformed["setup_instructions"] = (
                f"Set {env.get('name', 'environment variable')}"
            )

        return transformed

    def _transform_git_context(self, ctx: dict[str, Any]) -> dict[str, Any]:
        """Transform git context requirement from YAML to model format."""
        context_type_str = ctx.get("type", "repository")

        # Map string to enum
        try:
            context_type = GitContextType(context_type_str)
        except ValueError:
            context_type = GitContextType.REPOSITORY

        transformed: dict[str, Any] = {
            "context_type": context_type,
            "required": ctx.get("required", True),
        }

        # Map 'check' to 'check_command'
        if "check" in ctx:
            transformed["check_command"] = ctx["check"]

        # Add value if present
        if "value" in ctx:
            transformed["value"] = ctx["value"]

        return transformed

    def _normalize_os_name(self, os_name: str) -> str:
        """Normalize OS name to standard format.

        Maps: macos -> darwin, ubuntu/debian -> linux
        """
        os_map = {
            "macos": "darwin",
            "mac": "darwin",
            "osx": "darwin",
            "ubuntu": "linux",
            "debian": "linux",
            "win": "windows",
            "win32": "windows",
        }
        normalized = os_map.get(os_name.lower(), os_name.lower())
        # Only return valid OS names
        if normalized in {"darwin", "linux", "windows"}:
            return normalized
        return "linux"  # Default fallback

    def list_workflows(self) -> list[str]:
        """List available workflow names (without .yaml extension).

        Returns:
            List of workflow names found in workflows directory
        """
        if not self.workflows_dir.exists():
            return []

        workflows = []
        for path in self.workflows_dir.glob("*.yaml"):
            workflows.append(path.stem)  # stem = filename without extension

        return sorted(workflows)

    def get_workflow_info(self, workflow_name: str) -> dict[str, str]:
        """Get basic workflow information without loading full requirements.

        Args:
            workflow_name: Name of the workflow

        Returns:
            Dictionary with name, description, and version

        Raises:
            ManifestLoadError: If workflow cannot be loaded
        """
        manifest = self.load(workflow_name)
        return {
            "name": manifest.name,
            "description": manifest.description,
            "version": manifest.version,
        }

    def get_current_os(self) -> str:
        """Get current OS in normalized format.

        Returns:
            'darwin', 'linux', or 'windows'
        """
        system = platform.system().lower()
        if system == "darwin":
            return "darwin"
        elif system == "linux":
            return "linux"
        elif system == "windows":
            return "windows"
        return "linux"  # Default fallback
