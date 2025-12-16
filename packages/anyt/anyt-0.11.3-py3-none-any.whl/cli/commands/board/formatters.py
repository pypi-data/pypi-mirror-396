"""Output formatting helpers for summary command."""

import json
from typing import Any, Optional


def format_summary_json(
    period: str,
    done_tasks: list[dict[str, Any]],
    active_tasks: list[dict[str, Any]],
    blocked_tasks: list[dict[str, Any]],
    backlog_tasks: list[dict[str, Any]],
    total: int,
) -> str:
    """Format summary data as JSON output."""
    high_priority_backlog = sorted(
        backlog_tasks, key=lambda t: t.get("priority", 0), reverse=True
    )[:3]
    done_count = len(done_tasks)
    progress_pct = int((done_count / total) * 100) if total > 0 else 0

    return json.dumps(
        {
            "success": True,
            "data": {
                "period": period,
                "done_tasks": done_tasks[:5],
                "active_tasks": active_tasks[:5],
                "blocked_tasks": blocked_tasks,
                "next_priorities": high_priority_backlog,
                "summary": {
                    "total": total,
                    "done": len(done_tasks),
                    "active": len(active_tasks),
                    "backlog": len(backlog_tasks),
                    "blocked": len(blocked_tasks),
                    "progress_pct": progress_pct,
                },
            },
            "message": None,
        }
    )


def format_error_json(error: str, message: Optional[str] = None) -> str:
    """Format error response as JSON."""
    return json.dumps(
        {
            "success": False,
            "error": error,
            "message": message or error,
        }
    )
