"""
GitHub-related workflow actions.
"""

import asyncio
from typing import Any, Dict

from rich.markup import escape

from cli.commands.console import console

from .base import Action
from ..context import ExecutionContext


class CreatePullRequestAction(Action):
    """Create a GitHub pull request."""

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Create a pull request using GitHub CLI.

        Args:
            params: Action parameters
                - title: PR title (optional, uses task title)
                - body: PR body (optional, uses task description)
                - base: Base branch (default: main)
                - head: Head branch (default: current branch)
                - draft: Create as draft (default: false)
                - labels: Comma-separated labels (optional)
                - assignees: Comma-separated assignees (optional)

        Returns:
            Dict with PR URL and number
        """
        task = ctx.task
        task_id = task.get("identifier", "N/A")
        task_title = task.get("title", "Automated PR")
        task_description = task.get("description", "")

        # Build PR parameters
        pr_title = params.get("title", task_title)
        pr_body = params.get("body") or self._build_pr_body(
            task_id, task_title, task_description, ctx
        )
        base_branch = params.get("base", "main")
        head_branch = params.get("head")
        is_draft = params.get("draft", False)
        labels = params.get("labels", "")
        assignees = params.get("assignees", "")

        # Get current branch if head not specified
        if not head_branch:
            process = await asyncio.create_subprocess_shell(
                "git rev-parse --abbrev-ref HEAD",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=ctx.workspace_dir,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise RuntimeError(f"Failed to get current branch: {stderr.decode()}")

            head_branch = stdout.decode().strip()

        # Check if head branch is same as base branch
        if head_branch == base_branch:
            reason = (
                f"Head branch '{head_branch}' is same as base branch '{base_branch}'"
            )
            console.print(f"  [yellow]⊘ Skipped:[/yellow] {escape(reason)}")
            return {
                "pr_url": None,
                "pr_number": None,
                "created": False,
                "exists": False,
                "skipped": True,
                "reason": reason,
            }

        # Push current branch first (gh pr create will handle the actual PR creation)
        # We skip pre-flight commit checks as they can give false negatives with
        # forked repos, shallow clones, etc. Let gh handle the error if no commits.
        push_cmd = f"git push -u origin {head_branch}"
        process = await asyncio.create_subprocess_shell(
            push_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )
        await process.communicate()

        if process.returncode != 0:
            # If push fails, it might already exist - that's ok
            pass

        # Build gh pr create command
        gh_cmd = [
            "gh",
            "pr",
            "create",
            "--title",
            pr_title,
            "--body",
            pr_body,
            "--base",
            base_branch,
            "--head",
            head_branch,
        ]

        if is_draft:
            gh_cmd.append("--draft")

        if labels:
            gh_cmd.extend(["--label", labels])

        if assignees:
            gh_cmd.extend(["--assignee", assignees])

        # Create PR
        process = await asyncio.create_subprocess_exec(
            *gh_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode()
            # Check if PR already exists
            if "already exists" in error_msg.lower():
                # Get existing PR URL
                pr_url = await self._get_existing_pr_url(head_branch, ctx)
                console.print(f"  [dim]PR already exists:[/dim] {escape(pr_url)}")
                return {
                    "pr_url": pr_url,
                    "pr_number": self._extract_pr_number(pr_url),
                    "created": False,
                    "exists": True,
                }
            # Check if no commits between branches (GraphQL error)
            if "no commits between" in error_msg.lower():
                reason = f"No commits between '{base_branch}' and '{head_branch}'"
                console.print(f"  [yellow]⊘ Skipped:[/yellow] {escape(reason)}")
                return {
                    "pr_url": None,
                    "pr_number": None,
                    "created": False,
                    "exists": False,
                    "skipped": True,
                    "reason": reason,
                }
            # Check if error is due to missing labels - retry without labels
            if "not found" in error_msg.lower() and labels:
                # Retry without labels
                gh_cmd_no_labels = [
                    "gh",
                    "pr",
                    "create",
                    "--title",
                    pr_title,
                    "--body",
                    pr_body,
                    "--base",
                    base_branch,
                    "--head",
                    head_branch,
                ]

                if is_draft:
                    gh_cmd_no_labels.append("--draft")

                if assignees:
                    gh_cmd_no_labels.extend(["--assignee", assignees])

                # Retry PR creation without labels
                process = await asyncio.create_subprocess_exec(
                    *gh_cmd_no_labels,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=ctx.workspace_dir,
                )

                stdout, stderr = await process.communicate()

                if process.returncode != 0:
                    raise RuntimeError(f"Failed to create PR: {stderr.decode()}")
                # If successful, continue to parse PR URL below
            else:
                raise RuntimeError(f"Failed to create PR: {error_msg}")

        # Parse PR URL from output
        pr_url = stdout.decode().strip().split("\n")[-1]

        console.print(f"  [green]✓ Created PR:[/green] {escape(pr_url)}")

        return {
            "pr_url": pr_url,
            "pr_number": self._extract_pr_number(pr_url),
            "created": True,
            "exists": False,
            "branch": head_branch,
        }

    def _build_pr_body(
        self,
        task_id: str,
        task_title: str,
        task_description: str,
        ctx: ExecutionContext,
    ) -> str:
        """Build default PR body from task information."""
        return f"""## Summary

Implements: {task_id} - {task_title}

## Description

{task_description}

## Changes

This PR was automatically created by the AnyTask Worker.

## Test Plan

- [ ] Review automated changes
- [ ] Verify tests pass
- [ ] Manual testing if needed

---

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>

Closes: {task_id}
"""

    async def _get_existing_pr_url(self, branch: str, ctx: ExecutionContext) -> str:
        """Get URL of existing PR for branch."""
        process = await asyncio.create_subprocess_shell(
            f"gh pr view {branch} --json url -q .url",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )
        stdout, _ = await process.communicate()
        return stdout.decode().strip()

    def _extract_pr_number(self, pr_url: str) -> str:
        """Extract PR number from URL."""
        try:
            return pr_url.rstrip("/").split("/")[-1]
        except (IndexError, AttributeError):
            return "unknown"


class MergePullRequestAction(Action):
    """Merge a GitHub pull request."""

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Merge a pull request using GitHub CLI.

        Args:
            params: Action parameters
                - pr_number: PR number to merge (required)
                - merge_method: Merge method - squash, merge, or rebase (default: squash)
                - delete_branch: Delete branch after merge (default: true)
                - auto: Enable auto-merge (default: false)

        Returns:
            Dict with merge status and PR number
        """
        pr_number = params.get("pr_number")
        if not pr_number:
            raise ValueError("pr_number is required for merging PR")

        merge_method = params.get("merge_method", "squash")
        delete_branch = params.get("delete_branch", True)
        auto = params.get("auto", False)

        # Validate merge method
        valid_methods = ["squash", "merge", "rebase"]
        if merge_method not in valid_methods:
            raise ValueError(
                f"Invalid merge_method: {merge_method}. "
                f"Must be one of: {', '.join(valid_methods)}"
            )

        # Build merge command
        if auto:
            # Enable auto-merge
            gh_cmd = [
                "gh",
                "pr",
                "merge",
                str(pr_number),
                f"--{merge_method}",
                "--auto",
            ]
        else:
            # Merge immediately
            gh_cmd = [
                "gh",
                "pr",
                "merge",
                str(pr_number),
                f"--{merge_method}",
            ]

        if delete_branch:
            gh_cmd.append("--delete-branch")

        # Execute merge
        process = await asyncio.create_subprocess_exec(
            *gh_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode()
            # Check if PR is already merged
            if (
                "already merged" in error_msg.lower()
                or "not found" in error_msg.lower()
            ):
                return {
                    "merged": True,
                    "pr_number": pr_number,
                    "already_merged": True,
                    "merge_method": merge_method,
                }
            raise RuntimeError(f"Failed to merge PR #{pr_number}: {error_msg}")

        return {
            "merged": True,
            "pr_number": pr_number,
            "already_merged": False,
            "merge_method": merge_method,
            "branch_deleted": delete_branch,
        }


class GitPushAction(Action):
    """Push commits to remote repository."""

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Push current branch to remote.

        Args:
            params: Action parameters
                - branch: Branch to push (optional, uses current)
                - force: Force push (default: false)
                - set-upstream: Set upstream tracking (default: true)

        Returns:
            Dict with push status and branch name
        """
        branch = params.get("branch")
        force = params.get("force", False)
        set_upstream = params.get("set-upstream", True)

        # Get current branch if not specified
        if not branch:
            process = await asyncio.create_subprocess_shell(
                "git rev-parse --abbrev-ref HEAD",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=ctx.workspace_dir,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise RuntimeError(f"Failed to get current branch: {stderr.decode()}")

            branch = stdout.decode().strip()

        # Build push command
        push_cmd = ["git", "push"]

        if set_upstream:
            push_cmd.extend(["-u", "origin", branch])
        else:
            push_cmd.extend(["origin", branch])

        if force:
            push_cmd.append("--force")

        # Execute push
        process = await asyncio.create_subprocess_exec(
            *push_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"Git push failed: {stderr.decode()}")

        return {
            "branch": branch,
            "pushed": True,
            "force": force,
        }
