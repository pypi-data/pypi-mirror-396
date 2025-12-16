"""Enhanced error handling for API client validation errors."""

from typing import Any
from pydantic import ValidationError


def format_enum_validation_error(error: ValidationError, data: dict[str, Any]) -> str:
    """Format enum validation errors with helpful context.

    Args:
        error: Pydantic validation error
        data: The data that failed validation

    Returns:
        Formatted error message with context
    """
    errors = error.errors()

    # Check if this is an enum validation error
    enum_errors = [e for e in errors if e.get("type") == "enum"]

    if not enum_errors:
        # Not an enum error, return standard message
        return str(error)

    # Build helpful error message
    lines = ["API returned data that doesn't match expected enum values:\n"]

    for err in enum_errors:
        field: tuple[int | str, ...] = err.get("loc", ())
        field_name = ".".join(str(f) for f in field)
        input_value = err.get("input")
        ctx = err.get("ctx", {})
        expected_values = ctx.get("expected", "unknown")

        lines.append(f"Field: {field_name}")
        lines.append(f"  Received: {input_value!r}")
        lines.append(f"  Expected one of: {expected_values}")

        # Get actual value from data
        try:
            actual: Any = data
            for key in field:
                if isinstance(key, str):
                    actual = actual[key]
                else:
                    actual = actual[int(key)]
            lines.append(f"  Full context: {actual!r}")
        except (KeyError, TypeError, IndexError):
            pass

        lines.append("")

    lines.append("This usually means:")
    lines.append("  1. The backend API schema has changed")
    lines.append("  2. Your local enum definitions are out of sync")
    lines.append("")
    lines.append("To fix:")
    lines.append("  1. Run: make validate-enums")
    lines.append("  2. Update src/cli/models/common.py with missing enum values")
    lines.append("  3. Or regenerate client: make generate-client")

    return "\n".join(lines)


class EnumValidationError(Exception):
    """Raised when API returns enum value not in our models."""

    def __init__(self, field: str, received: str, expected: list[str]):
        self.field = field
        self.received = received
        self.expected = expected
        super().__init__(
            f"API returned {field}={received!r} but expected one of: {expected}"
        )
