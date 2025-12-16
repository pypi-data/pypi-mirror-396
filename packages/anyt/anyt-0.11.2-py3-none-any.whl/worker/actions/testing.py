"""
Testing and build workflow actions.
"""

import asyncio
import re
from typing import Any, Dict

from rich.markup import escape

from cli.commands.console import console
from .base import Action
from ..context import ExecutionContext


class TestAction(Action):
    """Execute tests and create test results artifact."""

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute tests and capture results."""
        command = params.get("command", "pytest")
        args = params.get("args", "")

        # Build test command
        cmd = f"{command} {args}" if args else command

        # Execute tests
        console.print(f"  [dim]Running tests: {escape(cmd)}[/dim]")

        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )

        stdout, stderr = await process.communicate()

        # Combine output
        output = stdout.decode() + stderr.decode()

        # Parse test results (basic parsing)
        passed, failed, skipped = self._parse_test_output(output)
        total_tests = passed + failed + skipped
        success = process.returncode == 0

        return {
            "success": success,
            "exit_code": process.returncode,
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "output": output,
        }

    def _parse_test_output(self, output: str) -> tuple[int, int, int]:
        """Parse test output to extract counts."""
        passed = failed = skipped = 0

        # Try to parse pytest output
        if "passed" in output or "failed" in output:
            # Look for patterns like "5 passed, 2 failed, 1 skipped"
            match = re.search(r"(\d+)\s+passed", output)
            if match:
                passed = int(match.group(1))

            match = re.search(r"(\d+)\s+failed", output)
            if match:
                failed = int(match.group(1))

            match = re.search(r"(\d+)\s+skipped", output)
            if match:
                skipped = int(match.group(1))

        return passed, failed, skipped


class BuildAction(Action):
    """Execute build and create build output artifact."""

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute build command and capture output."""
        command = params.get("command", "make build")
        args = params.get("args", "")

        # Build command
        cmd = f"{command} {args}" if args else command

        # Execute build
        console.print(f"  [dim]Running build: {escape(cmd)}[/dim]")

        import time

        start_time = time.time()

        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )

        stdout, stderr = await process.communicate()

        duration = time.time() - start_time

        # Combine output
        output = stdout.decode() + stderr.decode()

        # Check for warnings (simple heuristic)
        warnings_count = output.lower().count("warning")

        success = process.returncode == 0

        return {
            "success": success,
            "exit_code": process.returncode,
            "duration": duration,
            "warnings_count": warnings_count,
            "output": output,
        }
