"""
Git-related workflow actions.
"""

import asyncio
import shutil
from pathlib import Path
from typing import Any, Dict

from .base import Action
from ..context import ExecutionContext


class GitCloneAction(Action):
    """Git clone action for cloning repositories in workflows."""

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Clone a git repository.

        Args:
            params: Action parameters
                - url: Repository URL (required)
                - path: Destination directory (default: workspace_dir)
                - branch: Branch to checkout after clone (optional)
                - depth: Clone depth for shallow clone (default: 1)
                - clean: If True, remove existing directory before clone (default: True)

        Returns:
            Dict with cloned status, path, and branch info
        """
        url = params.get("url")
        if not url:
            raise ValueError("url parameter is required for git-clone action")

        path = params.get("path")
        if path:
            dest_dir = Path(path)
            if not dest_dir.is_absolute():
                dest_dir = ctx.workspace_dir / dest_dir
        else:
            dest_dir = ctx.workspace_dir

        branch = params.get("branch")
        depth = params.get("depth", 1)
        clean = params.get("clean", True)

        # Clean existing directory if requested
        if clean and dest_dir.exists():
            shutil.rmtree(dest_dir)

        # Ensure parent directory exists
        dest_dir.parent.mkdir(parents=True, exist_ok=True)

        # Build clone command
        clone_cmd = ["git", "clone"]
        if depth:
            clone_cmd.extend(["--depth", str(depth)])
        if branch:
            clone_cmd.extend(["--branch", branch])
        clone_cmd.extend([url, str(dest_dir)])

        # Execute clone (suppress output to hide credentials in URL)
        process = await asyncio.create_subprocess_exec(
            *clone_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        _, stderr = await process.communicate()

        if process.returncode != 0:
            # Sanitize error message (remove potential credentials)
            error_msg = stderr.decode().replace(url, "[REDACTED]")
            raise RuntimeError(f"Git clone failed: {error_msg}")

        result: Dict[str, Any] = {
            "cloned": True,
            "path": str(dest_dir),
        }

        # Get current branch
        process = await asyncio.create_subprocess_shell(
            "git rev-parse --abbrev-ref HEAD",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=dest_dir,
        )
        stdout, _ = await process.communicate()
        if process.returncode == 0:
            result["branch"] = stdout.decode().strip()

        return result


class CheckoutAction(Action):
    """Git checkout action."""

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Checkout a git branch."""
        branch = params.get("branch", "main")
        clean = params.get("clean", False)

        commands: list[str] = []
        if clean:
            commands.append("git reset --hard")
            commands.append("git clean -fd")
        commands.append(f"git checkout {branch}")
        commands.append("git pull origin {branch}")

        for cmd in commands:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=ctx.workspace_dir,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise RuntimeError(f"Git command failed: {stderr.decode()}")

        return {"branch": branch, "clean": clean}


class GitCommitAction(Action):
    """Git commit and optionally push action."""

    # Protected branches that should never be force-pushed
    PROTECTED_BRANCHES = {"main", "master", "develop", "production", "staging"}

    def _is_protected_branch(self, branch: str) -> bool:
        """Check if a branch is protected and should not be force-pushed."""
        # Check exact matches
        if branch in self.PROTECTED_BRANCHES:
            return True
        # Check prefixes (release/*, hotfix/*)
        protected_prefixes = ("release/", "hotfix/")
        return branch.startswith(protected_prefixes)

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Commit changes to git and optionally push.

        Args:
            params: Action parameters
                - message: Commit message (default: "Automated commit")
                - add: Files to add - "all" or specific files (default: "all")
                - push: Whether to push after commit (default: False)
                - branch: Branch to push to (optional, uses current branch)
                - force: Use --force-with-lease for push (default: False)
                - pull_rebase: Pull with rebase before push if needed (default: True)
                - force_task_branch: Force push task branches if rebase fails (default: True)
                    Only applies to non-protected branches (not main/master/develop/etc)

        Returns:
            Dict with commit_hash, committed status, and pushed status
        """
        message = params.get("message", "Automated commit")
        add = params.get("add", "all")
        push = params.get("push", False)
        branch = params.get("branch")
        force = params.get("force", False)
        pull_rebase = params.get("pull_rebase", True)
        force_task_branch = params.get("force_task_branch", True)

        # Configure git user (required for commits)
        await asyncio.create_subprocess_shell(
            "git config user.name 'AnyTask System Worker'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )
        await asyncio.create_subprocess_shell(
            "git config user.email 'worker@anyt.dev'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )

        # Add files
        if add == "all":
            add_cmd = "git add -A"
        else:
            add_cmd = f"git add {add}"

        process = await asyncio.create_subprocess_shell(
            add_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )
        await process.communicate()

        # Commit
        commit_cmd: list[str] = ["git", "commit", "-m", message]
        process = await asyncio.create_subprocess_exec(
            *commit_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            # Check if it's just "nothing to commit"
            if b"nothing to commit" in stdout or b"nothing to commit" in stderr:
                return {"commit_hash": None, "committed": False, "pushed": False}
            raise RuntimeError(f"Git commit failed: {stderr.decode()}")

        # Get commit hash
        process = await asyncio.create_subprocess_shell(
            "git rev-parse --short HEAD",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )
        stdout, _ = await process.communicate()
        commit_hash = stdout.decode().strip()

        result = {"commit_hash": commit_hash, "committed": True, "pushed": False}

        # Push if requested
        if push:
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
                    raise RuntimeError(
                        f"Failed to get current branch: {stderr.decode()}"
                    )

                branch = stdout.decode().strip()

            # Push to remote
            # Use --force-with-lease if force=true (safe for retries)
            push_cmd = ["git", "push", "-u", "origin", branch]
            if force:
                push_cmd.append("--force-with-lease")

            process = await asyncio.create_subprocess_exec(
                *push_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=ctx.workspace_dir,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode()
                # Check if push failed due to remote having newer commits
                needs_sync = (
                    "fetch first" in error_msg
                    or "non-fast-forward" in error_msg
                    or "failed to push" in error_msg
                )

                if needs_sync and pull_rebase:
                    # Try to pull with rebase and retry push
                    rebase_cmd = ["git", "pull", "--rebase", "origin", branch]
                    process = await asyncio.create_subprocess_exec(
                        *rebase_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=ctx.workspace_dir,
                    )
                    _, rebase_stderr = await process.communicate()

                    rebase_failed = process.returncode != 0

                    if rebase_failed:
                        # Rebase failed (likely conflicts)
                        # Abort the rebase to clean up state
                        await asyncio.create_subprocess_exec(
                            "git",
                            "rebase",
                            "--abort",
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE,
                            cwd=ctx.workspace_dir,
                        )

                        # Check if we can force push (task branch only)
                        if force_task_branch and not self._is_protected_branch(branch):
                            # Fetch to update local tracking refs (needed for --force-with-lease)
                            await asyncio.create_subprocess_exec(
                                "git",
                                "fetch",
                                "origin",
                                branch,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE,
                                cwd=ctx.workspace_dir,
                            )

                            # Force push with lease - safe for task branches
                            force_push_cmd = [
                                "git",
                                "push",
                                "-u",
                                "origin",
                                branch,
                                "--force-with-lease",
                            ]
                            process = await asyncio.create_subprocess_exec(
                                *force_push_cmd,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE,
                                cwd=ctx.workspace_dir,
                            )
                            stdout, stderr = await process.communicate()

                            if process.returncode != 0:
                                # If still fails with stale info, use plain --force
                                # This is a task branch so it's safe
                                if "stale info" in stderr.decode():
                                    force_push_cmd[-1] = "--force"
                                    process = await asyncio.create_subprocess_exec(
                                        *force_push_cmd,
                                        stdout=asyncio.subprocess.PIPE,
                                        stderr=asyncio.subprocess.PIPE,
                                        cwd=ctx.workspace_dir,
                                    )
                                    stdout, stderr = await process.communicate()
                                    if process.returncode != 0:
                                        raise RuntimeError(
                                            f"Git force push failed: {stderr.decode()}"
                                        )
                                else:
                                    raise RuntimeError(
                                        f"Git force push failed: {stderr.decode()}"
                                    )

                            result["force_pushed"] = True
                            result["pushed"] = True
                            result["branch"] = branch
                            return result
                        else:
                            # Protected branch - can't force push
                            raise RuntimeError(
                                f"Git pull --rebase failed on protected branch "
                                f"'{branch}': {rebase_stderr.decode()}"
                            )

                    # Rebase succeeded - retry push
                    process = await asyncio.create_subprocess_exec(
                        *push_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=ctx.workspace_dir,
                    )
                    stdout, stderr = await process.communicate()

                    if process.returncode != 0:
                        raise RuntimeError(
                            f"Git push failed after rebase: {stderr.decode()}"
                        )

                    result["rebased"] = True
                elif (
                    needs_sync
                    and force_task_branch
                    and not self._is_protected_branch(branch)
                ):
                    # pull_rebase is disabled but force_task_branch is enabled
                    # Go straight to force push for task branches

                    # Fetch to update local tracking refs (needed for --force-with-lease)
                    await asyncio.create_subprocess_exec(
                        "git",
                        "fetch",
                        "origin",
                        branch,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=ctx.workspace_dir,
                    )

                    force_push_cmd = [
                        "git",
                        "push",
                        "-u",
                        "origin",
                        branch,
                        "--force-with-lease",
                    ]
                    process = await asyncio.create_subprocess_exec(
                        *force_push_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=ctx.workspace_dir,
                    )
                    stdout, stderr = await process.communicate()

                    if process.returncode != 0:
                        # If still fails with stale info, use plain --force
                        # This is a task branch so it's safe
                        if "stale info" in stderr.decode():
                            force_push_cmd[-1] = "--force"
                            process = await asyncio.create_subprocess_exec(
                                *force_push_cmd,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE,
                                cwd=ctx.workspace_dir,
                            )
                            stdout, stderr = await process.communicate()
                            if process.returncode != 0:
                                raise RuntimeError(
                                    f"Git force push failed: {stderr.decode()}"
                                )
                        else:
                            raise RuntimeError(
                                f"Git force push failed: {stderr.decode()}"
                            )

                    result["force_pushed"] = True
                else:
                    raise RuntimeError(f"Git push failed: {error_msg}")

            result["pushed"] = True
            result["branch"] = branch

        return result
