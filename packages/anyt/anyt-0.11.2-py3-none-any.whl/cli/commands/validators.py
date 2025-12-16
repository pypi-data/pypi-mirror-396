"""Centralized validation functions for CLI commands.

This module consolidates validation logic for priority, status, and other common
input validation patterns used across CLI commands.
"""

from typing import Optional

from cli.commands.formatters import output_json
from cli.models.common import Priority, Status

from .task.helpers import console


def validate_priority(
    priority: Optional[int],
    json_output: bool = False,
) -> bool:
    """Validate priority value is within range.

    Args:
        priority: Priority value to validate (must be -2 to 2)
        json_output: Whether to output JSON format

    Returns:
        True if valid or None, False otherwise (and outputs error message)
    """
    if priority is not None and (priority < -2 or priority > 2):
        if json_output:
            output_json(
                {
                    "error": "ValidationError",
                    "message": "Invalid priority value",
                    "details": "Priority must be between -2 and 2",
                },
                success=False,
            )
        else:
            console.print("[red]Error:[/red] Invalid priority value")
            console.print("  Priority must be between -2 and 2")
        return False
    return True


def validate_status(
    status: Optional[str],
    json_output: bool = False,
) -> tuple[bool, Optional[Status]]:
    """Validate and convert status string to enum.

    Args:
        status: Status string to validate
        json_output: Whether to output JSON format

    Returns:
        Tuple of (is_valid, Status enum or None)
        - (True, None) if status is None (not provided)
        - (True, Status) if status is valid
        - (False, None) if status is invalid (error message already output)
    """
    if status is None:
        return True, None

    try:
        return True, Status(status)
    except ValueError:
        valid_statuses = ", ".join([s.value for s in Status])
        if json_output:
            output_json(
                {
                    "error": "ValidationError",
                    "message": f"Invalid status '{status}'. Valid statuses: {valid_statuses}",
                },
                success=False,
            )
        else:
            console.print(f"[red]Error:[/red] Invalid status '{status}'")
            console.print(f"Valid statuses: {valid_statuses}")
        return False, None


def validate_priority_for_create(
    priority: int,
    json_output: bool = False,
) -> bool:
    """Validate priority value for task creation (required, with verbose help).

    Args:
        priority: Priority value to validate (must be -2 to 2)
        json_output: Whether to output JSON format

    Returns:
        True if valid, False otherwise (and outputs error message with level descriptions)
    """
    if priority < -2 or priority > 2:
        if json_output:
            output_json(
                {
                    "error": "ValidationError",
                    "message": "Invalid priority value",
                    "details": "Priority must be between -2 and 2\n  -2: Lowest\n  -1: Low\n   0: Normal (default)\n   1: High\n   2: Highest",
                },
                success=False,
            )
        else:
            console.print("[red]Error:[/red] Invalid priority value")
            console.print()
            console.print("  Priority must be between -2 and 2")
            console.print("    -2: Lowest")
            console.print("    -1: Low")
            console.print("     0: Normal (default)")
            console.print("     1: High")
            console.print("     2: Highest")
        return False
    return True


def to_priority_enum(priority: Optional[int]) -> Optional[Priority]:
    """Convert validated priority value to enum.

    Args:
        priority: Validated priority value (-2 to 2) or None

    Returns:
        Priority enum or None if not provided

    Note:
        Call validate_priority() first to ensure valid input.
    """
    if priority is None:
        return None
    return Priority(priority)


def to_status_enum(status: Optional[str]) -> Optional[Status]:
    """Convert validated status string to enum.

    Args:
        status: Validated status string or None

    Returns:
        Status enum or None if not provided

    Note:
        Call validate_status() first to ensure valid input.
    """
    if status is None:
        return None
    return Status(status)
