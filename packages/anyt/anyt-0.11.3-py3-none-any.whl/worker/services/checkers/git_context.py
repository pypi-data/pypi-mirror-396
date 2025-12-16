"""Git context requirement checker."""

from __future__ import annotations

import asyncio
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import ClassVar

from worker.models.workflow_requirements import (
    GitContextRequirement,
    GitContextType,
    RequirementCheckResult,
)


class GitContextChecker:
    """Checker for git repository context requirements."""

    # Cache for check results (class-level to share across instances)
    _cache: ClassVar[dict[str, tuple[RequirementCheckResult, datetime]]] = {}
    _default_ttl: ClassVar[timedelta] = timedelta(minutes=5)

    async def check(
        self, requirement: GitContextRequirement, use_cache: bool = True
    ) -> RequirementCheckResult:
        """
        Check if git context requirements are met.

        Args:
            requirement: The git context requirement to check
            use_cache: Whether to use cached results (default: True)

        Returns:
            RequirementCheckResult with success status and instructions
        """
        cache_key = f"git_context:{requirement.context_type}:{requirement.value or ''}"

        # Check cache if enabled
        if use_cache and cache_key in self._cache:
            cached_result, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < self._default_ttl:
                # Return cached result with from_cache=True
                cached_result.from_cache = True
                return cached_result

        # Route to appropriate check based on context type
        if requirement.context_type == GitContextType.REPOSITORY:
            result = await self._check_repository(requirement)
        elif requirement.context_type == GitContextType.REMOTE:
            result = await self._check_remote(requirement)
        else:  # GitContextType.BRANCH
            result = await self._check_branch(requirement)

        # Cache the result
        self._cache[cache_key] = (result, datetime.now())
        return result

    async def _check_repository(
        self, requirement: GitContextRequirement
    ) -> RequirementCheckResult:
        """Check if current directory is a git repository."""
        # Check for .git directory
        if Path(".git").exists():
            return RequirementCheckResult(
                success=True,
                message="Git repository detected",
                fix_instructions=None,
                warning=False,
                from_cache=False,
            )

        return RequirementCheckResult(
            success=False,
            message="Not a git repository",
            fix_instructions="Initialize a git repository:\n  git init",
            warning=not requirement.required,
            from_cache=False,
        )

    async def _check_remote(
        self, requirement: GitContextRequirement
    ) -> RequirementCheckResult:
        """Check if a specific git remote exists."""
        # requirement.value is guaranteed to be set by Pydantic validation
        assert requirement.value is not None

        try:
            # Run custom check command if provided
            if requirement.check_command:
                await self._run_command(requirement.check_command)
            else:
                # Default: check if remote exists
                await self._run_command(f"git remote get-url {requirement.value}")

            return RequirementCheckResult(
                success=True,
                message=f"Git remote '{requirement.value}' configured",
                fix_instructions=None,
                warning=False,
                from_cache=False,
            )
        except (OSError, subprocess.CalledProcessError):
            # OSError: Command execution failed
            # CalledProcessError: Git command returned non-zero
            return RequirementCheckResult(
                success=False,
                message=f"Git remote '{requirement.value}' not found",
                fix_instructions=f"Add remote:\n  git remote add {requirement.value} <url>",
                warning=not requirement.required,
                from_cache=False,
            )

    async def _check_branch(
        self, requirement: GitContextRequirement
    ) -> RequirementCheckResult:
        """Check if a specific git branch exists."""
        # requirement.value is guaranteed to be set by Pydantic validation
        assert requirement.value is not None

        try:
            # Check if branch exists
            if requirement.check_command:
                await self._run_command(requirement.check_command)
            else:
                # Default: check if branch exists locally or remotely
                await self._run_command(
                    f"git show-ref --verify --quiet refs/heads/{requirement.value}"
                )

            return RequirementCheckResult(
                success=True,
                message=f"Git branch '{requirement.value}' exists",
                fix_instructions=None,
                warning=False,
                from_cache=False,
            )
        except (OSError, subprocess.CalledProcessError):
            # OSError: Command execution failed
            # CalledProcessError: Git command returned non-zero
            return RequirementCheckResult(
                success=False,
                message=f"Git branch '{requirement.value}' not found",
                fix_instructions=f"Create branch:\n  git checkout -b {requirement.value}",
                warning=not requirement.required,
                from_cache=False,
            )

    async def _run_command(self, command: str) -> str:
        """
        Run a git command and return its output.

        Args:
            command: The command to run

        Returns:
            The command output (stdout)

        Raises:
            Exception: If the command fails
        """
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode().strip() if stderr else "Command failed"
            raise Exception(error_msg)

        return stdout.decode().strip()

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the check result cache."""
        cls._cache.clear()
