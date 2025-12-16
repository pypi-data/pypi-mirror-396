"""Environment variable requirement checker."""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta
from typing import ClassVar

from worker.models.workflow_requirements import (
    EnvVarRequirement,
    RequirementCheckResult,
)


class EnvVarChecker:
    """Checker for environment variable requirements."""

    # Cache for check results (class-level to share across instances)
    _cache: ClassVar[dict[str, tuple[RequirementCheckResult, datetime]]] = {}
    _default_ttl: ClassVar[timedelta] = timedelta(minutes=5)

    async def check(
        self, requirement: EnvVarRequirement, use_cache: bool = True
    ) -> RequirementCheckResult:
        """
        Check if an environment variable is set and optionally validate it.

        Args:
            requirement: The environment variable requirement to check
            use_cache: Whether to use cached results (default: True)

        Returns:
            RequirementCheckResult with success status and instructions
        """
        cache_key = f"env_var:{requirement.name}"

        # Check cache if enabled
        if use_cache and cache_key in self._cache:
            cached_result, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < self._default_ttl:
                # Return cached result with from_cache=True
                cached_result.from_cache = True
                return cached_result

        # Check if environment variable is set
        env_value = os.environ.get(requirement.name)
        if not env_value:
            result = RequirementCheckResult(
                success=False,
                message=f"{requirement.name} not set",
                fix_instructions=requirement.setup_instructions,
                warning=not requirement.required,
                from_cache=False,
            )
            self._cache[cache_key] = (result, datetime.now())
            return result

        # If check_command is provided, run it to validate
        if requirement.check_command:
            try:
                await self._run_check_command(requirement.check_command)
                result = RequirementCheckResult(
                    success=True,
                    message=f"{requirement.name} configured",
                    fix_instructions=None,
                    warning=False,
                    from_cache=False,
                )
            except (OSError, RuntimeError) as e:
                # OSError: Command execution failed
                # RuntimeError: Command-specific validation errors
                result = RequirementCheckResult(
                    success=False,
                    message=f"{requirement.name} set but validation failed: {e}",
                    fix_instructions=requirement.setup_instructions,
                    warning=not requirement.required,
                    from_cache=False,
                )
        else:
            # No check command, just confirm existence
            result = RequirementCheckResult(
                success=True,
                message=f"{requirement.name} set",
                fix_instructions=None,
                warning=False,
                from_cache=False,
            )

        # Cache the result
        self._cache[cache_key] = (result, datetime.now())
        return result

    async def _run_check_command(self, command: str) -> None:
        """
        Run a validation command for the environment variable.

        Args:
            command: The command to run (e.g., "gh auth status")

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
            error_msg = stderr.decode().strip() if stderr else "Validation failed"
            raise Exception(error_msg)

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the check result cache."""
        cls._cache.clear()
