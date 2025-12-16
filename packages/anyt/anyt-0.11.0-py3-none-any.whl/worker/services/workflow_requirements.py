"""Service for checking workflow requirements."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from worker.models.workflow_requirements import (
    RequirementCheckResult,
    WorkflowRequirements,
)
from worker.services.checkers import (
    CommandChecker,
    EnvVarChecker,
    FileSystemChecker,
    GitContextChecker,
)


class WorkflowCheckResults(BaseModel):
    """Results from checking all workflow requirements."""

    workflow_name: str = Field(..., description="Name of the workflow checked")
    results: list[tuple[str, RequirementCheckResult]] = Field(
        default_factory=list, description="List of (requirement_name, result) tuples"
    )
    passed: int = Field(0, description="Number of passed checks")
    failed: int = Field(0, description="Number of failed checks")
    warnings: int = Field(0, description="Number of warnings")
    from_cache: bool = Field(False, description="Whether results came from cache")

    model_config = {"frozen": False, "arbitrary_types_allowed": True}

    def is_success(self) -> bool:
        """Check if all required checks passed (warnings don't count as failures)."""
        return self.failed == 0


class WorkflowRequirementsService:
    """Service for checking workflow requirements."""

    def __init__(self, workspace_dir: Path | None = None):
        """Initialize the service.

        Args:
            workspace_dir: Optional workspace directory (defaults to current directory)
        """
        self.workspace_dir = workspace_dir or Path.cwd()
        self.command_checker = CommandChecker()
        self.env_var_checker = EnvVarChecker()
        self.git_context_checker = GitContextChecker()
        self.file_system_checker = FileSystemChecker()

    async def check_requirements(
        self,
        requirements: WorkflowRequirements,
        workflow_name: str,
        force: bool = False,
    ) -> WorkflowCheckResults:
        """Check all requirements for a workflow.

        Args:
            requirements: The workflow requirements to check
            workflow_name: Name of the workflow (for display)
            force: If True, bypass cache and force fresh checks

        Returns:
            WorkflowCheckResults with all check results
        """
        results: list[tuple[str, RequirementCheckResult]] = []
        passed = 0
        failed = 0
        warnings = 0
        all_from_cache = True  # Track if all results came from cache

        # Check command requirements
        for cmd_req in requirements.commands:
            result = await self.command_checker.check(cmd_req, use_cache=not force)
            results.append((cmd_req.name, result))

            if not result.from_cache:
                all_from_cache = False

            if result.success:
                passed += 1
            elif result.warning:
                warnings += 1
            else:
                failed += 1

        # Check environment variable requirements
        for env_req in requirements.env_vars:
            result = await self.env_var_checker.check(env_req, use_cache=not force)
            results.append((env_req.name, result))

            if not result.from_cache:
                all_from_cache = False

            if result.success:
                passed += 1
            elif result.warning:
                warnings += 1
            else:
                failed += 1

        # Check git context requirements
        for git_req in requirements.git_context:
            result = await self.git_context_checker.check(git_req, use_cache=not force)
            # Create a descriptive name for the git requirement
            if git_req.value:
                req_name = f"Git {git_req.context_type.value}: {git_req.value}"
            else:
                req_name = f"Git {git_req.context_type.value}"
            results.append((req_name, result))

            if not result.from_cache:
                all_from_cache = False

            if result.success:
                passed += 1
            elif result.warning:
                warnings += 1
            else:
                failed += 1

        # Check file system requirements
        for fs_req in requirements.file_system:
            result = await self.file_system_checker.check(fs_req, use_cache=not force)
            req_name = f"{fs_req.fs_type.value}: {fs_req.path}"
            results.append((req_name, result))

            if not result.from_cache:
                all_from_cache = False

            if result.success:
                passed += 1
            elif result.warning:
                warnings += 1
            else:
                failed += 1

        return WorkflowCheckResults(
            workflow_name=workflow_name,
            results=results,
            passed=passed,
            failed=failed,
            warnings=warnings,
            from_cache=all_from_cache and len(results) > 0,
        )

    def clear_cache(self) -> None:
        """Clear all cached check results."""
        # CommandChecker uses class-level cache, so we need to clear it directly
        # Other checkers don't have caches currently
        CommandChecker._cache.clear()
