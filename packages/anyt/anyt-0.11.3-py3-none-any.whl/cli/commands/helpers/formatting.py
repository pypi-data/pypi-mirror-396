"""Text and data formatting utilities."""

from datetime import datetime
from typing import Optional

__all__ = [
    "format_priority",
    "format_relative_time",
    "truncate_text",
]


def format_priority(priority: int) -> str:
    """Format priority as visual dots.

    Priority scale: -2 (lowest) to 2 (highest)
    """
    if priority >= 2:
        return "●●●"
    elif priority == 1:
        return "●●○"
    elif priority == 0:
        return "●○○"
    elif priority == -1:
        return "○○○"
    else:  # -2 or lower
        return "○○○"


def format_relative_time(dt_str: Optional[str]) -> str:
    """Format datetime string as relative time (e.g., '2h ago')."""
    if not dt_str:
        return "—"

    try:
        # Parse ISO format datetime
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo)
        delta = now - dt

        seconds = int(delta.total_seconds())

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m ago"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours}h ago"
        elif seconds < 604800:
            days = seconds // 86400
            return f"{days}d ago"
        else:
            weeks = seconds // 604800
            return f"{weeks}w ago"
    except Exception:  # noqa: BLE001 - Intentionally broad: fallback to raw string on any parse error
        # Return raw string if parsing fails - display is best-effort
        return dt_str


def truncate_text(text: str, max_length: int = 40) -> str:
    """Truncate text to max_length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 1] + "…"
