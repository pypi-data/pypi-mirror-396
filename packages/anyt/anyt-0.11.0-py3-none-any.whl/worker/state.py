"""Worker runtime state management."""

import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class CurrentTask(BaseModel):
    """Current task being worked on."""

    task_id: int
    identifier: str
    started_at: str


class WorkerStats(BaseModel):
    """Worker statistics."""

    tasks_completed: int = 0
    tasks_failed: int = 0


class WorkerState(BaseModel):
    """Runtime worker state."""

    agent_id: str
    pid: Optional[int] = None
    status: str = "stopped"  # running, stopped, error
    started_at: Optional[str] = None
    current_task: Optional[CurrentTask] = None
    stats: WorkerStats = Field(default_factory=WorkerStats)

    @property
    def state_path(self) -> Path:
        """Path to state file."""
        return Path.cwd() / ".anyt" / "workers" / f"{self.agent_id}.state.json"

    @classmethod
    def load(cls, agent_id: str) -> "WorkerState":
        """Load worker state from file."""
        state_path = Path.cwd() / ".anyt" / "workers" / f"{agent_id}.state.json"
        if not state_path.exists():
            # Return default state
            return cls(agent_id=agent_id)

        with open(state_path, encoding="utf-8") as f:
            data = json.load(f)

        return cls(**data)

    def save(self) -> None:
        """Save worker state to file."""
        state_path = self.state_path
        state_path.parent.mkdir(parents=True, exist_ok=True)

        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2)

    def update_stats(self, completed: int = 0, failed: int = 0) -> None:
        """Update statistics."""
        self.stats.tasks_completed += completed
        self.stats.tasks_failed += failed
        self.save()
