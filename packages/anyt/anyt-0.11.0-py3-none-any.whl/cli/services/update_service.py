"""Service for checking and performing CLI updates."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
import httpx
from packaging.version import Version

from cli import __version__

PYPI_PACKAGE_NAME = "anyt"
PYPI_URL = f"https://pypi.org/pypi/{PYPI_PACKAGE_NAME}/json"


class InstallMethod(str, Enum):
    """Installation method for the CLI."""

    UV = "uv"
    PIPX = "pipx"
    PIP = "pip"
    UNKNOWN = "unknown"


@dataclass
class VersionInfo:
    """Version information for the CLI."""

    current: str
    latest: str | None
    update_available: bool
    error: str | None = None


@dataclass
class InstallInfo:
    """Installation information for the CLI."""

    method: InstallMethod
    executable_path: str | None
    python_version: str


class UpdateService:
    """Service for managing CLI updates."""

    def get_current_version(self) -> str:
        """Get the currently installed version."""
        return __version__

    async def get_latest_version(self) -> str | None:
        """Fetch the latest version from PyPI.

        Returns:
            Latest version string, or None if unable to fetch.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(PYPI_URL)
                response.raise_for_status()
                data = response.json()
                version: str = data["info"]["version"]
                return version
        except (httpx.HTTPError, KeyError, json.JSONDecodeError):
            return None

    def is_update_available(self, current: str, latest: str) -> bool:
        """Check if an update is available.

        Args:
            current: Current version string
            latest: Latest version string

        Returns:
            True if latest > current
        """
        try:
            return Version(latest) > Version(current)
        except Exception:  # noqa: BLE001 - Gracefully handle version parsing errors
            return False

    async def check_version(self) -> VersionInfo:
        """Check current version against latest available.

        Returns:
            VersionInfo with current, latest, and update_available status.
        """
        current = self.get_current_version()
        latest = await self.get_latest_version()

        if latest is None:
            return VersionInfo(
                current=current,
                latest=None,
                update_available=False,
                error="Unable to fetch latest version from PyPI",
            )

        return VersionInfo(
            current=current,
            latest=latest,
            update_available=self.is_update_available(current, latest),
        )

    def detect_install_method(self) -> InstallMethod:
        """Detect how the CLI was installed.

        Checks in order:
        1. uv tool list - for uv tool installations
        2. pipx list - for pipx installations
        3. Fallback to pip

        Returns:
            InstallMethod enum value
        """
        # Check uv tool first
        if self._is_uv_tool_install():
            return InstallMethod.UV

        # Check pipx
        if self._is_pipx_install():
            return InstallMethod.PIPX

        # Check if pip is available (fallback)
        if shutil.which("pip") or shutil.which("pip3"):
            return InstallMethod.PIP

        return InstallMethod.UNKNOWN

    def _is_uv_tool_install(self) -> bool:
        """Check if installed via uv tool."""
        uv_path = shutil.which("uv")
        if not uv_path:
            return False

        try:
            result = subprocess.run(
                ["uv", "tool", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Check if anyt is in the tool list
            return PYPI_PACKAGE_NAME in result.stdout
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ):
            return False

    def _is_pipx_install(self) -> bool:
        """Check if installed via pipx."""
        pipx_path = shutil.which("pipx")
        if not pipx_path:
            return False

        try:
            result = subprocess.run(
                ["pipx", "list", "--json"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return False

            data = json.loads(result.stdout)
            # pipx list --json returns {"venvs": {"package_name": {...}}}
            venvs = data.get("venvs", {})
            return PYPI_PACKAGE_NAME in venvs
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
            json.JSONDecodeError,
        ):
            return False

    def get_executable_path(self) -> str | None:
        """Get the path to the anyt executable."""
        return shutil.which(PYPI_PACKAGE_NAME)

    def get_install_info(self) -> InstallInfo:
        """Get installation information.

        Returns:
            InstallInfo with method, path, and Python version.
        """
        return InstallInfo(
            method=self.detect_install_method(),
            executable_path=self.get_executable_path(),
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        )

    def get_upgrade_command(
        self, method: InstallMethod, force: bool = False
    ) -> list[str] | None:
        """Get the command to upgrade the CLI.

        Args:
            method: Installation method
            force: Whether to force reinstall

        Returns:
            Command as list of strings, or None if unknown method.
        """
        if method == InstallMethod.UV:
            if force:
                return ["uv", "tool", "install", "--force", PYPI_PACKAGE_NAME]
            return ["uv", "tool", "upgrade", PYPI_PACKAGE_NAME]

        if method == InstallMethod.PIPX:
            if force:
                return ["pipx", "install", "--force", PYPI_PACKAGE_NAME]
            return ["pipx", "upgrade", PYPI_PACKAGE_NAME]

        if method == InstallMethod.PIP:
            pip_cmd = "pip3" if shutil.which("pip3") else "pip"
            if force:
                return [pip_cmd, "install", "--force-reinstall", PYPI_PACKAGE_NAME]
            return [pip_cmd, "install", "--upgrade", PYPI_PACKAGE_NAME]

        return None

    def run_upgrade(
        self,
        method: InstallMethod,
        force: bool = False,
    ) -> tuple[bool, str]:
        """Run the upgrade command.

        Args:
            method: Installation method
            force: Whether to force reinstall

        Returns:
            Tuple of (success, output/error message)
        """
        command = self.get_upgrade_command(method, force)
        if command is None:
            return (
                False,
                "Unknown installation method. Cannot determine upgrade command.",
            )

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout for upgrade
            )

            if result.returncode == 0:
                return True, result.stdout or "Upgrade completed successfully."
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return False, f"Upgrade failed: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Upgrade timed out after 2 minutes."
        except subprocess.SubprocessError as e:
            return False, f"Failed to run upgrade command: {e}"
        except FileNotFoundError as e:
            return False, f"Command not found: {e}"
