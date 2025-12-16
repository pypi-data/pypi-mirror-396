"""Command requirement checker."""

from __future__ import annotations

import asyncio
import platform
import shutil
from datetime import datetime, timedelta
from typing import ClassVar

from worker.models.workflow_requirements import (
    CheckType,
    CommandRequirement,
    RequirementCheckResult,
)


class CommandChecker:
    """Checker for command-line tool requirements."""

    # Cache for check results (class-level to share across instances)
    _cache: ClassVar[dict[str, tuple[RequirementCheckResult, datetime]]] = {}
    _default_ttl: ClassVar[timedelta] = timedelta(minutes=5)

    async def check(
        self, requirement: CommandRequirement, use_cache: bool = True
    ) -> RequirementCheckResult:
        """
        Check if a command-line tool is installed and optionally validate it.

        Args:
            requirement: The command requirement to check
            use_cache: Whether to use cached results (default: True)

        Returns:
            RequirementCheckResult with success status and instructions
        """
        cache_key = f"command:{requirement.name}"

        # Check cache if enabled
        if use_cache and cache_key in self._cache:
            cached_result, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < self._default_ttl:
                # Return cached result with from_cache=True
                cached_result.from_cache = True
                return cached_result

        # Handle special check types
        if requirement.check_type == CheckType.CODING_AGENT:
            result = await self._check_coding_agent(requirement)
            self._cache[cache_key] = (result, datetime.now())
            return result

        if requirement.check_type == CheckType.GH_AUTH:
            result = await self._check_gh_auth(requirement)
            self._cache[cache_key] = (result, datetime.now())
            return result

        if requirement.check_type == CheckType.CLAUDE_AUTH:
            result = await self._check_claude_auth(requirement)
            self._cache[cache_key] = (result, datetime.now())
            return result

        # Check if command exists
        if not shutil.which(requirement.name):
            result = RequirementCheckResult(
                success=False,
                message=f"{requirement.name} not found",
                fix_instructions=self._get_install_instructions(requirement),
                warning=not requirement.required,
                from_cache=False,
            )
            self._cache[cache_key] = (result, datetime.now())
            return result

        # If check_command is provided, run it to validate
        if requirement.check_command:
            try:
                version = await self._run_check_command(requirement.check_command)
                result = RequirementCheckResult(
                    success=True,
                    message=f"{requirement.name} installed ({version})",
                    fix_instructions=None,
                    warning=False,
                    from_cache=False,
                )
            except (OSError, RuntimeError) as e:
                # OSError: Command execution failed
                # RuntimeError: Command-specific validation errors
                result = RequirementCheckResult(
                    success=False,
                    message=f"{requirement.name} found but validation failed: {e}",
                    fix_instructions=self._get_install_instructions(requirement),
                    warning=not requirement.required,
                    from_cache=False,
                )
        else:
            # No check command, just confirm existence
            result = RequirementCheckResult(
                success=True,
                message=f"{requirement.name} installed",
                fix_instructions=None,
                warning=False,
                from_cache=False,
            )

        # Cache the result
        self._cache[cache_key] = (result, datetime.now())
        return result

    async def _check_coding_agent(
        self, requirement: CommandRequirement
    ) -> RequirementCheckResult:
        """
        Check if at least one coding agent is installed.

        Args:
            requirement: The command requirement

        Returns:
            RequirementCheckResult indicating if any coding agent is available
        """
        # Import here to avoid circular imports
        from worker.agents import AgentDetector

        detector = AgentDetector()
        agents = detector.detect_all()

        installed_agents = [a for a in agents if a.installed]

        if installed_agents:
            agent_names = [a.config.name for a in installed_agents]
            return RequirementCheckResult(
                success=True,
                message=f"Coding agent(s) installed: {', '.join(agent_names)}",
                fix_instructions=None,
                warning=False,
                from_cache=False,
            )
        else:
            return RequirementCheckResult(
                success=False,
                message="No coding agent installed",
                fix_instructions=self._get_install_instructions(requirement),
                warning=not requirement.required,
                from_cache=False,
            )

    async def _check_gh_auth(
        self, requirement: CommandRequirement
    ) -> RequirementCheckResult:
        """
        Check if GitHub CLI is authenticated.

        Args:
            requirement: The command requirement

        Returns:
            RequirementCheckResult indicating if gh is authenticated
        """
        # First check if gh is installed
        if not shutil.which("gh"):
            return RequirementCheckResult(
                success=False,
                message="GitHub CLI (gh) not installed",
                fix_instructions=self._get_install_instructions(requirement),
                warning=not requirement.required,
                from_cache=False,
            )

        # Check authentication status
        try:
            await self._run_check_command("gh auth status")
            return RequirementCheckResult(
                success=True,
                message="GitHub CLI authenticated",
                fix_instructions=None,
                warning=False,
                from_cache=False,
            )
        except RuntimeError as e:
            error_msg = str(e)
            # Check if it's an auth error
            if (
                "gh auth login" in error_msg.lower()
                or "not logged" in error_msg.lower()
            ):
                return RequirementCheckResult(
                    success=False,
                    message="GitHub CLI not authenticated",
                    fix_instructions="Run: gh auth login",
                    warning=not requirement.required,
                    from_cache=False,
                )
            # Other error
            return RequirementCheckResult(
                success=False,
                message=f"GitHub CLI auth check failed: {error_msg}",
                fix_instructions="Run: gh auth login",
                warning=not requirement.required,
                from_cache=False,
            )

    async def _check_claude_auth(
        self, requirement: CommandRequirement
    ) -> RequirementCheckResult:
        """
        Check if Claude CLI is installed and can be used.

        Note: This check only verifies Claude CLI is installed. Actual API
        authentication is verified when the coding agent runs. If auth fails,
        users will see: "Run: claude setup-token"

        Args:
            requirement: The command requirement

        Returns:
            RequirementCheckResult indicating if Claude CLI is available
        """
        # Check if claude is installed
        if not shutil.which("claude"):
            return RequirementCheckResult(
                success=False,
                message="Claude CLI not installed",
                fix_instructions=self._get_install_instructions(requirement),
                warning=not requirement.required,
                from_cache=False,
            )

        # Verify claude can run by checking version
        try:
            await self._run_check_command("claude --version")
            return RequirementCheckResult(
                success=True,
                message="Claude CLI installed",
                fix_instructions=None,
                warning=False,
                from_cache=False,
            )
        except RuntimeError as e:
            return RequirementCheckResult(
                success=False,
                message=f"Claude CLI check failed: {e}",
                fix_instructions="Run: claude setup-token\nOr set ANTHROPIC_API_KEY environment variable",
                warning=not requirement.required,
                from_cache=False,
            )

    async def _run_check_command(self, command: str) -> str:
        """
        Run a check command and return its output.

        Args:
            command: The command to run (e.g., "git --version")

        Returns:
            The command output (stdout)

        Raises:
            RuntimeError: If the command fails with details about the failure
        """
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
        except OSError as e:
            # OSError can occur if the shell itself fails to execute
            raise RuntimeError(f"Failed to execute command: {e}") from e

        if process.returncode != 0:
            # Decode with utf-8 and fallback to replace errors for Windows compatibility
            error_msg = ""
            if stderr:
                error_msg = stderr.decode("utf-8", errors="replace").strip()
            if not error_msg and stdout:
                # Some commands output errors to stdout
                error_msg = stdout.decode("utf-8", errors="replace").strip()
            if not error_msg:
                error_msg = f"Command exited with code {process.returncode}"
            raise RuntimeError(error_msg)

        return stdout.decode("utf-8", errors="replace").strip()

    def _get_install_instructions(self, requirement: CommandRequirement) -> str:
        """
        Get OS-specific installation instructions.

        Args:
            requirement: The command requirement

        Returns:
            Formatted installation instructions for the current OS
        """
        if not requirement.install_instructions:
            return f"Please install {requirement.name}"

        # Get current OS
        current_os = platform.system().lower()
        os_map = {
            "darwin": "darwin",
            "linux": "linux",
            "windows": "windows",
        }
        os_key = os_map.get(current_os)

        # Get instructions for current OS
        if os_key and os_key in requirement.install_instructions:
            return requirement.install_instructions[os_key]

        # Fallback: show all available instructions
        if requirement.install_instructions:
            instructions = "\n".join(
                f"  {os_name}: {cmd}"
                for os_name, cmd in requirement.install_instructions.items()
            )
            return f"Install {requirement.name}:\n{instructions}"

        return f"Please install {requirement.name}"

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the check result cache."""
        cls._cache.clear()
