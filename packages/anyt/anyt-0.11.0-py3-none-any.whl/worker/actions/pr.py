"""
Pull request workflow actions for AnyTask integration.
"""

import asyncio
import json
import logging
from typing import Any, Dict

from rich.markup import escape

from cli.client.pull_requests import PullRequestsAPIClient
from cli.commands.console import console
from cli.config import get_effective_api_config
from cli.utils.errors import is_debug_mode
from sdk.generated.models.CIConclusion import CIConclusion
from sdk.generated.models.CIStatus import CIStatus
from sdk.generated.models.PRStatus import PRStatus
from sdk.generated.models.ReviewStatus import ReviewStatus
from sdk.generated.models.UpdatePRRequest import UpdatePRRequest

from ..context import ExecutionContext
from .base import Action

logger = logging.getLogger(__name__)


def _debug(message: str) -> None:
    """Print debug message if ANYT_DEBUG is enabled."""
    if is_debug_mode():
        console.print(f"  [dim]DEBUG: {escape(message)}[/dim]")


class PullRequestRegisterAction(Action):
    """Register a pull request in AnyTask after creation.

    This action should be called after creating a GitHub PR to track it
    in the AnyTask system, linking it to the current task.
    """

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Register a pull request in the AnyTask backend.

        Args:
            params: Action parameters
                - pr_number: GitHub PR number (required)
                - pr_url: URL to the PR on GitHub (required)
                - head_branch: Source branch name (required)
                - base_branch: Target branch name (required)
                - head_sha: SHA of the head commit (required)
                - pr_status: PR status - draft, open, merged, closed (optional)

        Returns:
            Dict with:
                - pr_id: ID of the registered PR in AnyTask (or None if failed)
                - registered: Boolean indicating if registration succeeded
                - error: Error message if registration failed (optional)
        """
        # Debug: Log entry and all received parameters
        _debug("PullRequestRegisterAction.execute() called")
        _debug(f"Received params: {params}")
        _debug(f"Context task: {ctx.task}")
        _debug(f"Context workspace_id: {ctx.workspace_id}")

        # Get required parameters
        pr_number = params.get("pr_number")
        pr_url = params.get("pr_url")
        head_branch = params.get("head_branch")
        base_branch = params.get("base_branch")
        head_sha = params.get("head_sha")
        pr_status_str = params.get("pr_status")

        _debug("Extracted values:")
        _debug(f"  pr_number={pr_number} (type={type(pr_number).__name__})")
        _debug(f"  pr_url={pr_url}")
        _debug(f"  head_branch={head_branch}")
        _debug(f"  base_branch={base_branch}")
        _debug(f"  head_sha={head_sha}")

        # Validate required parameters
        if not pr_number:
            _debug("Validation failed - pr_number is missing")
            return self._failure_result("pr_number is required")
        if not pr_url:
            _debug("Validation failed - pr_url is missing")
            return self._failure_result("pr_url is required")
        if not head_branch:
            _debug("Validation failed - head_branch is missing")
            return self._failure_result("head_branch is required")
        if not base_branch:
            _debug("Validation failed - base_branch is missing")
            return self._failure_result("base_branch is required")
        if not head_sha:
            _debug("Validation failed - head_sha is missing")
            return self._failure_result("head_sha is required")

        # Get task identifier from context
        task_identifier = ctx.task.get("identifier")
        _debug(f"task_identifier={task_identifier}")
        if not task_identifier:
            _debug("Validation failed - no task identifier in context")
            logger.warning("No task identifier in context, cannot register PR")
            return self._failure_result("No task identifier in context")

        _debug("All validations passed, proceeding...")

        # Convert pr_status string to enum if provided, default to "open"
        pr_status: PRStatus = PRStatus.OPEN  # Default for newly created PRs
        if pr_status_str:
            try:
                pr_status = PRStatus(pr_status_str)
            except ValueError:
                logger.warning(
                    f"Invalid pr_status: {pr_status_str}, using default 'open'"
                )
        _debug(f"pr_status={pr_status.value}")

        # Get API client configuration
        _debug("Creating API client...")
        try:
            client = self._create_client(ctx)
            _debug("API client created successfully")
        except ValueError as e:
            _debug(f"Failed to create API client: {e}")
            logger.warning(f"Failed to create API client: {e}")
            return self._failure_result(str(e))

        # Register the PR
        try:
            # Get base URL for logging
            api_config = get_effective_api_config()
            base_url = api_config.get("api_url", "")

            _debug("About to make API call")
            _debug(f"api_config={api_config}")
            _debug(
                f"POST {base_url}/v1/workspaces/{ctx.workspace_id}"
                f"/pull-requests/tasks/{task_identifier}/pull-requests"
            )
            _debug(f"  pr_number: {pr_number}")
            _debug(f"  pr_url: {pr_url}")
            _debug(f"  head_branch: {head_branch}")
            _debug(f"  base_branch: {base_branch}")
            _debug(f"  head_sha: {head_sha[:12] if head_sha else 'None'}...")
            _debug(f"  pr_status: {pr_status.value}")

            _debug("Calling client.create_pr()...")
            pr = await client.create_pr(
                identifier=task_identifier,
                pr_number=int(pr_number),
                pr_url=pr_url,
                head_branch=head_branch,
                base_branch=base_branch,
                head_sha=head_sha,
                pr_status=pr_status,
            )
            _debug("client.create_pr() returned successfully")
            _debug(f"  pr_id: {pr.id}")
            _debug(f"  task_id: {pr.task_id}")
            _debug(f"  workspace_id: {pr.workspace_id}")

            console.print(
                f"  [green]✓ Registered PR #{pr_number}[/green] in AnyTask (id: {pr.id})"
            )

            return {
                "pr_id": pr.id,
                "registered": True,
            }

        except Exception as e:
            # Log warning but don't fail the workflow
            logger.warning(f"Failed to register PR in AnyTask: {e}")
            console.print("  [red]✗ Failed to register PR in AnyTask[/red]")
            console.print(f"  [dim]  Error: {type(e).__name__}: {escape(str(e))}[/dim]")
            # Show more details for HTTP errors
            if hasattr(e, "status_code"):
                console.print(
                    f"  [dim]  Status code: {getattr(e, 'status_code')}[/dim]"
                )
            # Show full traceback in debug mode
            if is_debug_mode():
                import traceback

                console.print(
                    f"  [dim]  Traceback: {escape(traceback.format_exc())}[/dim]"
                )
            return self._failure_result(str(e))

    def _create_client(self, ctx: ExecutionContext) -> PullRequestsAPIClient:
        """Create the PullRequestsAPIClient with appropriate credentials.

        Supports both workspace API key and worker token authentication.

        Args:
            ctx: Execution context

        Returns:
            Configured PullRequestsAPIClient

        Raises:
            ValueError: If no valid credentials available
        """
        # Get workspace config if available
        workspace_id = ctx.workspace_id

        # Get API configuration
        api_config = get_effective_api_config()
        base_url = api_config.get("api_url")
        api_key = api_config.get("api_key")

        if not base_url:
            raise ValueError("API base URL not configured")

        if not api_key:
            raise ValueError("No authentication credentials available")

        return PullRequestsAPIClient(
            base_url=base_url,
            api_key=api_key,
            workspace_id=workspace_id,
        )

    def _failure_result(self, error: str) -> Dict[str, Any]:
        """Create a failure result dictionary.

        Args:
            error: Error message

        Returns:
            Dict with registered=False and error message
        """
        return {
            "pr_id": None,
            "registered": False,
            "error": error,
        }


class PullRequestUpdateAction(Action):
    """Update a pull request record in AnyTask.

    This action updates an existing PR record with new status information,
    typically used by monitoring workflows to track PR lifecycle.
    """

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Update a pull request record in the AnyTask backend.

        Args:
            params: Action parameters
                - pr_id: ID of the PR in AnyTask (required)
                - pr_status: PR status (draft, open, merged, closed)
                - review_status: Review status (pending, approved, changes_requested, dismissed)
                - ci_status: CI status (pending, success, failure, error)
                - ci_conclusion: CI conclusion (success, failure, neutral, etc.)
                - mergeable: Whether PR is mergeable
                - mergeable_state: GitHub mergeable state string
                - merge_commit_sha: SHA of merge commit (if merged)
                - head_sha: Current head SHA

        Returns:
            Dict with:
                - updated: Boolean indicating if update succeeded
                - pr_id: ID of the updated PR
                - error: Error message if update failed (optional)
        """
        # Get required parameter
        pr_id = params.get("pr_id")
        if not pr_id:
            return self._failure_result("pr_id is required")

        # Get task identifier from context (required for task-scoped endpoint)
        task_identifier = ctx.task.get("identifier")
        if not task_identifier:
            logger.warning("No task identifier in context, cannot update PR")
            return self._failure_result("No task identifier in context")

        # Build update request with optional fields
        update_fields: Dict[str, Any] = {}

        # PR status
        pr_status_str = params.get("pr_status")
        if pr_status_str:
            try:
                update_fields["pr_status"] = PRStatus(pr_status_str)
            except ValueError:
                logger.warning(f"Invalid pr_status: {pr_status_str}, ignoring")

        # Review status
        review_status_str = params.get("review_status")
        if review_status_str:
            try:
                update_fields["review_status"] = ReviewStatus(review_status_str)
            except ValueError:
                logger.warning(f"Invalid review_status: {review_status_str}, ignoring")

        # CI status
        ci_status_str = params.get("ci_status")
        if ci_status_str:
            try:
                update_fields["ci_status"] = CIStatus(ci_status_str)
            except ValueError:
                logger.warning(f"Invalid ci_status: {ci_status_str}, ignoring")

        # CI conclusion
        ci_conclusion_str = params.get("ci_conclusion")
        if ci_conclusion_str:
            try:
                update_fields["ci_conclusion"] = CIConclusion(ci_conclusion_str)
            except ValueError:
                logger.warning(f"Invalid ci_conclusion: {ci_conclusion_str}, ignoring")

        # Boolean/string fields
        if "mergeable" in params:
            update_fields["mergeable"] = bool(params["mergeable"])
        if "mergeable_state" in params:
            update_fields["mergeable_state"] = params["mergeable_state"]
        if "merge_commit_sha" in params:
            update_fields["merge_commit_sha"] = params["merge_commit_sha"]
        if "head_sha" in params:
            update_fields["head_sha"] = params["head_sha"]

        # Review counts
        if "review_count" in params:
            update_fields["review_count"] = int(params["review_count"])
        if "approved_count" in params:
            update_fields["approved_count"] = int(params["approved_count"])
        if "changes_requested_count" in params:
            update_fields["changes_requested_count"] = int(
                params["changes_requested_count"]
            )

        # CI check counts
        if "ci_check_runs_total" in params:
            update_fields["ci_check_runs_total"] = int(params["ci_check_runs_total"])
        if "ci_check_runs_completed" in params:
            update_fields["ci_check_runs_completed"] = int(
                params["ci_check_runs_completed"]
            )
        if "ci_check_runs_failed" in params:
            update_fields["ci_check_runs_failed"] = int(params["ci_check_runs_failed"])

        if not update_fields:
            return self._failure_result("No update fields provided")

        # Get API client
        try:
            client = self._create_client(ctx)
        except ValueError as e:
            logger.warning(f"Failed to create API client: {e}")
            return self._failure_result(str(e))

        # Update the PR
        try:
            update_request = UpdatePRRequest(**update_fields)
            await client.update_pr(
                identifier=task_identifier,
                pr_id=int(pr_id),
                updates=update_request,
            )

            console.print(f"  [green]✓ Updated PR #{pr_id}[/green] in AnyTask")

            return {
                "updated": True,
                "pr_id": pr_id,
            }

        except Exception as e:
            logger.warning(f"Failed to update PR in AnyTask: {e}")
            console.print(
                f"  [yellow]⚠ Could not update PR in AnyTask:[/yellow] {escape(str(e))}"
            )
            return self._failure_result(str(e))

    def _create_client(self, ctx: ExecutionContext) -> PullRequestsAPIClient:
        """Create the PullRequestsAPIClient with appropriate credentials."""
        workspace_id = ctx.workspace_id
        api_config = get_effective_api_config()
        base_url = api_config.get("api_url")
        api_key = api_config.get("api_key")

        if not base_url:
            raise ValueError("API base URL not configured")
        if not api_key:
            raise ValueError("No authentication credentials available")

        return PullRequestsAPIClient(
            base_url=base_url,
            api_key=api_key,
            workspace_id=workspace_id,
        )

    def _failure_result(self, error: str) -> Dict[str, Any]:
        """Create a failure result dictionary."""
        return {
            "updated": False,
            "pr_id": None,
            "error": error,
        }


class PullRequestSyncAction(Action):
    """Sync pull request state from GitHub to AnyTask.

    This action queries GitHub for the current state of a PR and updates
    the corresponding record in AnyTask, used for reconciliation workflows.
    """

    # Mapping from GitHub states to backend enums
    GITHUB_STATE_MAP = {
        "OPEN": PRStatus.OPEN,
        "MERGED": PRStatus.MERGED,
        "CLOSED": PRStatus.CLOSED,
    }

    GITHUB_REVIEW_MAP = {
        "APPROVED": ReviewStatus.APPROVED,
        "CHANGES_REQUESTED": ReviewStatus.CHANGES_REQUESTED,
        "REVIEW_REQUIRED": ReviewStatus.PENDING,
        "": ReviewStatus.PENDING,  # No review decision yet
    }

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Sync PR state from GitHub to AnyTask backend.

        Args:
            params: Action parameters
                - pr_id: ID of the PR in AnyTask (required)
                - pr_number: GitHub PR number (required if not using pr_url)
                - repo: GitHub repo in owner/repo format (optional, uses current)

        Returns:
            Dict with:
                - synced: Boolean indicating if sync succeeded
                - pr_status: Current PR status
                - review_status: Current review status
                - ci_status: Current CI status
                - error: Error message if sync failed (optional)
        """
        pr_id = params.get("pr_id")
        pr_number = params.get("pr_number")

        if not pr_id:
            return self._failure_result("pr_id is required")
        if not pr_number:
            return self._failure_result("pr_number is required")

        # Get task identifier from context (required for task-scoped endpoint)
        task_identifier = ctx.task.get("identifier")
        if not task_identifier:
            logger.warning("No task identifier in context, cannot sync PR")
            return self._failure_result("No task identifier in context")

        repo = params.get("repo")

        # Fetch PR data from GitHub
        try:
            gh_data = await self._fetch_github_pr(pr_number, repo, ctx)
        except Exception as e:
            logger.warning(f"Failed to fetch PR from GitHub: {e}")
            return self._failure_result(f"GitHub fetch failed: {e}")

        # Map GitHub data to backend update fields
        update_fields = self._map_github_to_backend(gh_data)

        if not update_fields:
            return self._failure_result("No mappable data from GitHub")

        # Get API client and update
        try:
            client = self._create_client(ctx)
            update_request = UpdatePRRequest(**update_fields)
            await client.update_pr(
                identifier=task_identifier,
                pr_id=int(pr_id),
                updates=update_request,
            )

            pr_status = update_fields.get("pr_status")
            review_status = update_fields.get("review_status")
            ci_status = update_fields.get("ci_status")

            console.print(
                f"  [green]✓ Synced PR #{pr_number}[/green] "
                f"(status={pr_status}, review={review_status}, ci={ci_status})"
            )

            return {
                "synced": True,
                "pr_id": pr_id,
                "pr_status": pr_status.value if pr_status else None,
                "review_status": review_status.value if review_status else None,
                "ci_status": ci_status.value if ci_status else None,
            }

        except Exception as e:
            logger.warning(f"Failed to sync PR to AnyTask: {e}")
            return self._failure_result(str(e))

    async def _fetch_github_pr(
        self, pr_number: int | str, repo: str | None, ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Fetch PR data from GitHub using gh CLI.

        Args:
            pr_number: GitHub PR number
            repo: Optional repo in owner/repo format
            ctx: Execution context

        Returns:
            Dict with GitHub PR data

        Raises:
            RuntimeError: If gh command fails
        """
        # Build gh command
        gh_cmd = [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--json",
            "state,reviewDecision,statusCheckRollup,mergeable,isDraft,mergeCommit,headRefOid",
        ]

        if repo:
            gh_cmd.extend(["--repo", repo])

        process = await asyncio.create_subprocess_exec(
            *gh_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"gh pr view failed: {stderr.decode()}")

        return json.loads(stdout.decode())  # type: ignore[no-any-return]

    def _map_github_to_backend(self, gh_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map GitHub PR data to backend update fields.

        Args:
            gh_data: Raw GitHub PR data from gh CLI

        Returns:
            Dict with fields for UpdatePRRequest
        """
        update_fields: Dict[str, Any] = {}

        # Map PR state
        state = gh_data.get("state", "")
        if gh_data.get("isDraft"):
            update_fields["pr_status"] = PRStatus.DRAFT
        elif state in self.GITHUB_STATE_MAP:
            update_fields["pr_status"] = self.GITHUB_STATE_MAP[state]

        # Map review decision
        review_decision = gh_data.get("reviewDecision") or ""
        if review_decision in self.GITHUB_REVIEW_MAP:
            update_fields["review_status"] = self.GITHUB_REVIEW_MAP[review_decision]
        else:
            update_fields["review_status"] = ReviewStatus.PENDING

        # Map CI status from statusCheckRollup
        status_checks = gh_data.get("statusCheckRollup") or []
        ci_status, ci_conclusion, check_stats = self._process_status_checks(
            status_checks
        )
        if ci_status:
            update_fields["ci_status"] = ci_status
        if ci_conclusion:
            update_fields["ci_conclusion"] = ci_conclusion
        if check_stats:
            update_fields.update(check_stats)

        # Map mergeable
        mergeable = gh_data.get("mergeable")
        if mergeable is not None:
            # GitHub returns "MERGEABLE", "CONFLICTING", "UNKNOWN"
            update_fields["mergeable"] = mergeable == "MERGEABLE"
            update_fields["mergeable_state"] = mergeable

        # Map merge commit SHA
        merge_commit = gh_data.get("mergeCommit")
        if merge_commit and isinstance(merge_commit, dict):
            update_fields["merge_commit_sha"] = merge_commit.get("oid")

        # Map head SHA
        head_oid = gh_data.get("headRefOid")
        if head_oid:
            update_fields["head_sha"] = head_oid

        return update_fields

    def _process_status_checks(
        self, status_checks: list[Dict[str, Any]]
    ) -> tuple[CIStatus | None, CIConclusion | None, Dict[str, int] | None]:
        """Process GitHub status check rollup into CI status.

        Args:
            status_checks: List of status check objects from GitHub

        Returns:
            Tuple of (ci_status, ci_conclusion, check_stats_dict)
        """
        if not status_checks:
            return None, None, None

        total = len(status_checks)
        completed = 0
        failed = 0
        has_pending = False

        for check in status_checks:
            status = check.get("status", "")
            conclusion = check.get("conclusion", "")

            if status == "COMPLETED":
                completed += 1
                if conclusion in ("FAILURE", "ERROR", "TIMED_OUT"):
                    failed += 1
            elif status in ("QUEUED", "IN_PROGRESS", "PENDING"):
                has_pending = True

        # Determine overall CI status
        if has_pending or completed < total:
            ci_status = CIStatus.PENDING
            ci_conclusion = None
        elif failed > 0:
            ci_status = CIStatus.FAILURE
            ci_conclusion = CIConclusion.FAILURE
        else:
            ci_status = CIStatus.SUCCESS
            ci_conclusion = CIConclusion.SUCCESS

        check_stats = {
            "ci_check_runs_total": total,
            "ci_check_runs_completed": completed,
            "ci_check_runs_failed": failed,
        }

        return ci_status, ci_conclusion, check_stats

    def _create_client(self, ctx: ExecutionContext) -> PullRequestsAPIClient:
        """Create the PullRequestsAPIClient with appropriate credentials."""
        workspace_id = ctx.workspace_id
        api_config = get_effective_api_config()
        base_url = api_config.get("api_url")
        api_key = api_config.get("api_key")

        if not base_url:
            raise ValueError("API base URL not configured")
        if not api_key:
            raise ValueError("No authentication credentials available")

        return PullRequestsAPIClient(
            base_url=base_url,
            api_key=api_key,
            workspace_id=workspace_id,
        )

    def _failure_result(self, error: str) -> Dict[str, Any]:
        """Create a failure result dictionary."""
        return {
            "synced": False,
            "pr_id": None,
            "pr_status": None,
            "review_status": None,
            "ci_status": None,
            "error": error,
        }
