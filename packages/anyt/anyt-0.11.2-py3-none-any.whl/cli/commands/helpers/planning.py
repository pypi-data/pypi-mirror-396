"""Planning helper utilities for CLI commands.

This module provides utilities for handling implementation plan content,
including reading from stdin, files, and validating mutual exclusivity.
"""

import sys
from pathlib import Path
from typing import Optional

import typer

from cli.commands.console import console
from cli.commands.formatters import output_json


class PlanContentError(Exception):
    """Raised when plan content resolution fails."""

    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        self.message = message
        super().__init__(message)


def resolve_plan_content(
    plan: Optional[str],
    plan_file: Optional[str],
    json_output: bool = False,
) -> Optional[str]:
    """Resolve plan content from --plan or --plan-file options.

    Handles:
    - Mutual exclusivity check (--plan vs --plan-file)
    - Stdin reading when plan == "-"
    - File reading with existence validation
    - Direct content passthrough

    Args:
        plan: Plan content or "-" for stdin
        plan_file: Path to file containing plan content
        json_output: Whether to output errors in JSON format

    Returns:
        The resolved plan content, or None if neither option provided

    Raises:
        typer.Exit: If validation fails or file not found
    """
    # Mutual exclusivity check
    if plan and plan_file:
        if json_output:
            output_json(
                {
                    "error": "ValidationError",
                    "message": "Cannot specify both --plan and --plan-file",
                },
                success=False,
            )
        else:
            console.print(
                "[red]Error:[/red] Cannot specify both --plan and --plan-file"
            )
        raise typer.Exit(1)

    # Read from stdin
    if plan == "-":
        return sys.stdin.read().strip()

    # Direct content
    if plan:
        return plan

    # Read from file
    if plan_file:
        plan_path = Path(plan_file)
        if not plan_path.exists():
            if json_output:
                output_json(
                    {
                        "error": "FileNotFound",
                        "message": f"Plan file not found: {plan_file}",
                    },
                    success=False,
                )
            else:
                console.print(f"[red]Error:[/red] Plan file not found: {plan_file}")
            raise typer.Exit(1)
        return plan_path.read_text(encoding="utf-8").strip()

    # Neither option provided
    return None
