"""File system requirement checker."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import ClassVar

from worker.models.workflow_requirements import (
    FileSystemRequirement,
    FileSystemType,
    RequirementCheckResult,
)


def _is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


class FileSystemChecker:
    """Checker for file system requirements."""

    # Cache for check results (class-level to share across instances)
    _cache: ClassVar[dict[str, tuple[RequirementCheckResult, datetime]]] = {}
    _default_ttl: ClassVar[timedelta] = timedelta(minutes=5)

    async def check(
        self, requirement: FileSystemRequirement, use_cache: bool = True
    ) -> RequirementCheckResult:
        """
        Check if file system requirements are met.

        Args:
            requirement: The file system requirement to check
            use_cache: Whether to use cached results (default: True)

        Returns:
            RequirementCheckResult with success status and instructions
        """
        cache_key = f"file_system:{requirement.fs_type}:{requirement.path}"

        # Check cache if enabled
        if use_cache and cache_key in self._cache:
            cached_result, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < self._default_ttl:
                # Return cached result with from_cache=True
                cached_result.from_cache = True
                return cached_result

        path = Path(requirement.path)

        # Check existence based on type
        if requirement.fs_type == FileSystemType.DIRECTORY:
            result = await self._check_directory(path, requirement)
        else:  # FileSystemType.FILE
            result = await self._check_file(path, requirement)

        # Cache the result
        self._cache[cache_key] = (result, datetime.now())
        return result

    async def _check_directory(
        self, path: Path, requirement: FileSystemRequirement
    ) -> RequirementCheckResult:
        """Check if a directory exists and has correct permissions."""
        if not path.exists():
            if _is_windows():
                fix_cmd = f'mkdir "{requirement.path}"'
            else:
                fix_cmd = f"mkdir -p {requirement.path}"
            return RequirementCheckResult(
                success=False,
                message=f"Directory not found: {requirement.path}",
                fix_instructions=f"Create directory:\n  {fix_cmd}",
                warning=not requirement.required,
                from_cache=False,
            )

        if not path.is_dir():
            if _is_windows():
                fix_cmd = f'del "{requirement.path}" && mkdir "{requirement.path}"'
            else:
                fix_cmd = f"rm {requirement.path} && mkdir -p {requirement.path}"
            return RequirementCheckResult(
                success=False,
                message=f"Path exists but is not a directory: {requirement.path}",
                fix_instructions=f"Remove file and create directory:\n  {fix_cmd}",
                warning=not requirement.required,
                from_cache=False,
            )

        # Check permissions if specified
        if requirement.permissions:
            perm_check = self._check_permissions(path, requirement.permissions)
            if not perm_check.success:
                return perm_check

        return RequirementCheckResult(
            success=True,
            message=f"Directory exists: {requirement.path}",
            fix_instructions=None,
            warning=False,
            from_cache=False,
        )

    async def _check_file(
        self, path: Path, requirement: FileSystemRequirement
    ) -> RequirementCheckResult:
        """Check if a file exists and has correct permissions."""
        if not path.exists():
            if _is_windows():
                fix_cmd = f'type nul > "{requirement.path}"'
            else:
                fix_cmd = f"touch {requirement.path}"
            return RequirementCheckResult(
                success=False,
                message=f"File not found: {requirement.path}",
                fix_instructions=f"Create file:\n  {fix_cmd}",
                warning=not requirement.required,
                from_cache=False,
            )

        if not path.is_file():
            if _is_windows():
                fix_cmd = f'rmdir /s /q "{requirement.path}" && type nul > "{requirement.path}"'
            else:
                fix_cmd = f"rm -r {requirement.path} && touch {requirement.path}"
            return RequirementCheckResult(
                success=False,
                message=f"Path exists but is not a file: {requirement.path}",
                fix_instructions=f"Remove directory and create file:\n  {fix_cmd}",
                warning=not requirement.required,
                from_cache=False,
            )

        # Check permissions if specified
        if requirement.permissions:
            perm_check = self._check_permissions(path, requirement.permissions)
            if not perm_check.success:
                return perm_check

        return RequirementCheckResult(
            success=True,
            message=f"File exists: {requirement.path}",
            fix_instructions=None,
            warning=False,
            from_cache=False,
        )

    def _check_permissions(
        self, path: Path, required_perms: str
    ) -> RequirementCheckResult:
        """
        Check if path has required permissions.

        Args:
            path: The path to check
            required_perms: Required permissions string (e.g., 'r', 'rw', 'rwx')

        Returns:
            RequirementCheckResult indicating if permissions are correct
        """
        # Parse required permissions
        needs_read = "r" in required_perms
        needs_write = "w" in required_perms
        needs_execute = "x" in required_perms

        # Check actual permissions
        has_read = os.access(path, os.R_OK)
        has_write = os.access(path, os.W_OK)
        has_execute = os.access(path, os.X_OK)

        # Determine missing permissions
        missing = []
        if needs_read and not has_read:
            missing.append("read")
        if needs_write and not has_write:
            missing.append("write")
        if needs_execute and not has_execute:
            missing.append("execute")

        if missing:
            # Calculate permission code
            perm_code = 0
            if needs_read:
                perm_code += 4
            if needs_write:
                perm_code += 2
            if needs_execute:
                perm_code += 1

            # Platform-specific fix instructions
            if _is_windows():
                fix_instructions = (
                    f"Fix permissions for {path}:\n"
                    f"  1. Right-click the file/folder and select 'Properties'\n"
                    f"  2. Go to the 'Security' tab\n"
                    f"  3. Click 'Edit' and grant your user the required permissions"
                )
            else:
                fix_instructions = (
                    f"Fix permissions:\n  chmod u+{required_perms} {path}"
                )

            return RequirementCheckResult(
                success=False,
                message=f"Insufficient permissions for {path}: missing {', '.join(missing)}",
                fix_instructions=fix_instructions,
                warning=True,
                from_cache=False,
            )

        return RequirementCheckResult(
            success=True,
            message=f"Permissions OK: {path}",
            fix_instructions=None,
            warning=False,
            from_cache=False,
        )

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the check result cache."""
        cls._cache.clear()
