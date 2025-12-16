"""Domain model wrappers for dependency graph."""

from dataclasses import dataclass

from sdk.generated.models.DependencyGraphResponse import (
    DependencyGraphResponse as GeneratedResponse,
)
from sdk.generated.models.DependencyGraphNode import (
    DependencyGraphNode as GeneratedNode,
)
from sdk.generated.models.DependencyGraphEdge import (
    DependencyGraphEdge as GeneratedEdge,
)


@dataclass
class DependencyGraphNode:
    """Domain model for graph node."""

    id: str
    title: str
    status: str
    priority: int

    @classmethod
    def from_generated(cls, node: GeneratedNode) -> "DependencyGraphNode":
        """Convert from generated model."""
        return cls(
            id=node.id,
            title=node.title,
            status=node.status,
            priority=node.priority,
        )


@dataclass
class DependencyGraphEdge:
    """Domain model for graph edge."""

    from_task: str
    to_task: str
    blocking: bool

    @classmethod
    def from_generated(cls, edge: GeneratedEdge) -> "DependencyGraphEdge":
        """Convert from generated model."""
        return cls(
            from_task=edge.from_task,
            to_task=edge.to_task,
            blocking=edge.blocking,
        )


@dataclass
class DependencyGraphResponse:
    """Complete dependency graph."""

    nodes: list[DependencyGraphNode]
    edges: list[DependencyGraphEdge]

    @classmethod
    def from_generated(cls, response: GeneratedResponse) -> "DependencyGraphResponse":
        """Convert from generated model."""
        return cls(
            nodes=[DependencyGraphNode.from_generated(n) for n in response.nodes],
            edges=[DependencyGraphEdge.from_generated(e) for e in response.edges],
        )

    def get_blocked_tasks(self) -> set[str]:
        """Get set of task IDs that are blocked by incomplete dependencies.

        A task is blocked if it has at least one blocking dependency
        that is not in 'done' status.

        Returns:
            Set of task identifiers that are blocked
        """
        # Build dependency map: task_id -> list of tasks it depends on
        dependencies: dict[str, list[str]] = {}
        for edge in self.edges:
            if edge.blocking:
                if edge.from_task not in dependencies:
                    dependencies[edge.from_task] = []
                dependencies[edge.from_task].append(edge.to_task)

        # Build status map: task_id -> status
        node_status: dict[str, str] = {n.id: n.status for n in self.nodes}

        # Find blocked tasks
        blocked: set[str] = set()
        for task_id, deps in dependencies.items():
            # Check if any blocking dependency is not done
            if any(node_status.get(dep) != "done" for dep in deps):
                blocked.add(task_id)

        return blocked

    def get_blocking_tasks(self, task_id: str) -> list[DependencyGraphNode]:
        """Get list of incomplete tasks blocking the given task.

        Args:
            task_id: Task identifier to check

        Returns:
            List of DependencyGraphNode representing incomplete blocking tasks
        """
        # Find dependencies for this task
        blocking_ids: list[str] = []
        for edge in self.edges:
            if edge.from_task == task_id and edge.blocking:
                blocking_ids.append(edge.to_task)

        # Get node info for blocking tasks
        node_map: dict[str, DependencyGraphNode] = {n.id: n for n in self.nodes}
        blocking_tasks: list[DependencyGraphNode] = []
        for dep_id in blocking_ids:
            node = node_map.get(dep_id)
            if node and node.status != "done":
                blocking_tasks.append(node)

        return blocking_tasks
