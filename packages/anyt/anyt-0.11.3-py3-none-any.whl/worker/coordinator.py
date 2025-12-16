"""
Task coordinator - main worker loop that polls for tasks and executes workflows.
"""

import asyncio
import os
import shutil
import stat
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from rich.markup import escape
from rich.table import Table

from cli.commands.console import console
from cli.client.comments import CommentsAPIClient
from cli.client.projects import ProjectsAPIClient
from cli.client.tasks import TasksAPIClient
from cli.client.workspaces import WorkspacesAPIClient
from cli.models.common import Status
from cli.models.wrappers.task import Task
from cli.services.task_service import TaskService

from sdk.generated.models.CodingAgentSettings import CodingAgentSettings
from sdk.generated.models.CodingAgentType import CodingAgentType
from sdk.generated.services.async_Coding_Agent_Configuration_service import (
    getWorkspaceCodingAgentConfig,
)

from .cache import CacheManager
from .executor.core import WorkflowExecutor
from .workflow_models import Workflow


class TaskCoordinator:
    """
    Coordinates task polling and workflow execution.

    Similar to the bash script but with:
    - Smart polling with exponential backoff
    - Workflow-based execution
    - Better error handling
    - Structured logging
    """

    def __init__(
        self,
        workspace_dir: Path,
        workspace_id: int,
        workflows_dir: Optional[Path] = None,
        workflow_file: Optional[Path] = None,
        poll_interval: int = 5,
        max_backoff: int = 60,
        project_id: int | None = None,
        clone_repos: bool = False,
        cleanup_workspaces: bool = True,
        coding_agents: Optional[List[str]] = None,
    ):
        """
        Initialize task coordinator.

        Args:
            workspace_dir: Working directory for task execution
            workspace_id: ID of the workspace to operate in (required)
            workflows_dir: Directory containing workflow definitions
            workflow_file: Specific workflow file to run (if specified, runs ONLY this workflow)
            poll_interval: Base polling interval in seconds
            max_backoff: Maximum backoff interval in seconds
            project_id: Optional project ID to scope suggestions to a specific project
            clone_repos: If True, clone project repositories for task execution
            cleanup_workspaces: If True, cleanup task workspaces after execution (default: True)
            coding_agents: List of coding agent types to filter tasks by (e.g., ["claude", "codex"])
        """
        self.workspace_dir = workspace_dir
        self.workspace_id = workspace_id
        self.workflows_dir = workflows_dir or workspace_dir / ".anyt" / "workflows"
        self.workflow_file = workflow_file
        self.poll_interval = poll_interval
        self.max_backoff = max_backoff
        self.project_id = project_id
        self.clone_repos = clone_repos
        self.cleanup_workspaces = cleanup_workspaces
        self.coding_agents = coding_agents
        self.current_backoff: float = float(poll_interval)

        # Load API key from config if available
        self.api_key = self._load_api_key()

        # Debug: Log API key status
        if self.api_key:
            key_preview = (
                f"{self.api_key[:15]}..." if len(self.api_key) > 15 else self.api_key
            )
            console.print(f"[dim]Loaded API key: {key_preview}[/dim]")
        else:
            console.print(
                "[yellow]Warning: No API key loaded - artifact uploads will fail[/yellow]"
            )

        # Initialize clients for repo cloning (optional)
        self.projects_client: Optional[ProjectsAPIClient] = None
        if clone_repos:
            self._init_clone_clients()

        # Initialize components
        self.cache_manager = CacheManager()

        self.executor = WorkflowExecutor(
            workspace_id=self.workspace_id,
            cache_manager=self.cache_manager,
            api_key=self.api_key,
        )
        self.task_client = TasksAPIClient.from_config()
        # Use workspace_id override to ensure task updates work even without local config
        self.task_service: TaskService = TaskService.with_workspace_id(
            self.workspace_id
        )
        self.comments_client = CommentsAPIClient.from_config()
        self.workspaces_client = WorkspacesAPIClient.from_config()

        # Cached names for display (fetched lazily)
        self._workspace_name: Optional[str] = None
        self._project_name: Optional[str] = None

        # Load workflows
        self.workflows: Dict[str, Workflow] = {}
        self._load_workflows()

        # Log project filter if configured
        if self.project_id:
            console.print(f"[dim]Project filter: {self.project_id}[/dim]")
        # projects_client can be set inside _init_clone_clients() via try/except
        projects_client_available = self.projects_client is not None
        if self.clone_repos and projects_client_available:
            console.print("[dim]Repository cloning: enabled[/dim]")
        elif self.clone_repos:
            console.print(
                "[yellow]Warning: --clone-repos enabled but no clone client available. "
                "Ensure ANYT_API_KEY is set.[/yellow]"
            )

        # Statistics
        self.stats: Dict[str, Any] = {
            "tasks_processed": 0,
            "tasks_succeeded": 0,
            "tasks_failed": 0,
            "started_at": datetime.now(),
        }

    def _fix_yaml_boolean_keys(self, data: Dict[Any, Any]) -> Dict[str, Any]:
        """
        Fix YAML boolean key issue.

        YAML interprets 'on:' as boolean True. This function converts
        the boolean key back to the string 'on' for Pydantic model compatibility.

        Args:
            data: YAML parsed data (may contain boolean keys)

        Returns:
            Fixed data dict with string keys only
        """
        # Convert boolean keys to strings (YAML quirk: 'on:' becomes True)
        if True in data:
            data["on"] = data.pop(True)
        if False in data:
            data["off"] = data.pop(False)
        return data

    def _load_api_key(self) -> Optional[str]:
        """
        Load API key from config if available.

        Returns:
            API key string if available, None otherwise
        """
        try:
            from cli.config import get_effective_api_config

            api_config = get_effective_api_config()
            return api_config.get("api_key")
        except (ImportError, OSError, RuntimeError):
            # ImportError: config module not available
            # OSError/RuntimeError: config loading issues
            return None

    def _init_clone_clients(self) -> None:
        """
        Initialize API clients for repository cloning operations.

        Uses ANYT_API_KEY for agent workers (ProjectsAPIClient).

        Sets:
            self.projects_client: For agent workers
        """
        try:
            from cli.config import get_effective_api_config

            api_config = get_effective_api_config()
            api_key = api_config.get("api_key")
            api_url: str = api_config.get("api_url") or "https://api.anyt.dev"

            if api_key:
                self.projects_client = ProjectsAPIClient(
                    base_url=api_url, api_key=api_key
                )
                return

        except (ImportError, OSError, ValueError) as e:
            console.print(
                f"[yellow]Warning: Failed to initialize clone client: {e}[/yellow]"
            )

    def _get_api_config(self) -> Any:
        """
        Get APIConfig for generated API client calls.

        Returns:
            APIConfig instance with base_path set from config
        """
        try:
            from cli.config import get_effective_api_config
            from sdk.generated.api_config import APIConfig

            api_config = get_effective_api_config()
            api_url = api_config.get("api_url")

            if not api_url:
                raise RuntimeError("API URL not configured")

            return APIConfig(base_path=api_url, access_token=None)
        except (ImportError, OSError, ValueError) as e:
            # ImportError: SDK not available
            # OSError: File system errors
            # ValueError: Invalid configuration
            console.print(
                f"[yellow]Warning: Failed to load API config: {escape(str(e))}[/yellow]"
            )
            # Return default config as fallback
            from sdk.generated.api_config import APIConfig

            return APIConfig()

    def _load_workflows(self) -> None:
        """
        Load workflow definitions.

        If workflow_file is specified, loads ONLY that workflow (single workflow mode).
        Otherwise, loads ALL workflows from workflows_dir (multi-workflow mode).
        """
        # Single workflow mode - load only the specified workflow
        if self.workflow_file:
            try:
                with open(self.workflow_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    # Fix YAML boolean key issue (on: becomes True)
                    data = self._fix_yaml_boolean_keys(data)
                    workflow = Workflow(**data)
                    self.workflows[workflow.name] = workflow
                    console.print(
                        f"[dim]✓ Loaded workflow: {workflow.name} (single workflow mode)[/dim]"
                    )
                return
            except (OSError, yaml.YAMLError, TypeError, ValueError) as e:
                # OSError: File read errors
                # yaml.YAMLError: YAML parsing errors
                # TypeError/ValueError: Pydantic validation errors
                console.print(
                    f"[red]Error: Failed to load workflow {self.workflow_file}: {e}[/red]"
                )
                return

        # Multi-workflow mode - load all workflows from directory
        if not self.workflows_dir.exists():
            console.print(
                f"[yellow]Warning: Workflows directory not found: {self.workflows_dir}[/yellow]"
            )
            return

        for workflow_file in self.workflows_dir.glob("*.yaml"):
            try:
                with open(workflow_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    # Fix YAML boolean key issue (on: becomes True)
                    data = self._fix_yaml_boolean_keys(data)
                    workflow = Workflow(**data)
                    self.workflows[workflow.name] = workflow
                    console.print(f"[dim]✓ Loaded workflow: {workflow.name}[/dim]")
            except (OSError, yaml.YAMLError, TypeError, ValueError) as e:
                # OSError: File read errors
                # yaml.YAMLError: YAML parsing errors
                # TypeError/ValueError: Pydantic validation errors
                console.print(
                    f"[yellow]Warning: Failed to load workflow {workflow_file}: {e}[/yellow]"
                )

        if not self.workflows:
            console.print(
                "[yellow]Warning: No workflows loaded. Worker will not process tasks.[/yellow]"
            )

    async def _fetch_display_names(self) -> None:
        """Fetch workspace and project names for display purposes."""
        # Fetch workspace name
        try:
            workspace = await self.workspaces_client.get_workspace(self.workspace_id)
            self._workspace_name = workspace.name
        except Exception as e:
            console.print(f"[dim]Could not fetch workspace name: {e}[/dim]")
            self._workspace_name = None

        # Fetch project name if project_id is set
        if self.project_id is not None:
            try:
                # Initialize projects client if not already done
                if self.projects_client is None:
                    self.projects_client = ProjectsAPIClient.from_config()
                projects = await self.projects_client.list_projects(self.workspace_id)
                for project in projects:
                    if project.id == self.project_id:
                        self._project_name = project.name
                        break
            except Exception as e:
                console.print(f"[dim]Could not fetch project name: {e}[/dim]")
                self._project_name = None

    def _get_workspace_display(self) -> str:
        """Get display string for workspace (name or ID)."""
        if self._workspace_name:
            return f"{self._workspace_name} (ID: {self.workspace_id})"
        return str(self.workspace_id)

    def _get_project_display(self) -> str:
        """Get display string for project (name or ID)."""
        if self._project_name:
            return f"{self._project_name} (ID: {self.project_id})"
        return str(self.project_id)

    async def run(self) -> None:
        """Main worker loop."""
        console.print("\n[bold blue]AnyTask Claude Worker Started[/bold blue]")
        console.print(f"[dim]Workspace: {self.workspace_dir}[/dim]")
        console.print(f"[dim]Workflows: {len(self.workflows)}[/dim]")
        console.print(f"[dim]Poll interval: {self.poll_interval}s[/dim]")
        if self.coding_agents:
            console.print(f"[dim]Active agents: {', '.join(self.coding_agents)}[/dim]")
        console.print()

        # Fetch workspace and project names for display
        await self._fetch_display_names()

        try:
            while True:
                await self._poll_and_process()
                await asyncio.sleep(self.current_backoff)
        except KeyboardInterrupt:
            console.print("\n[yellow]Shutting down worker...[/yellow]")
            self._print_stats()

    async def _poll_and_process(self) -> None:
        """Poll for tasks and process them."""
        try:
            # Get suggested tasks
            console.print(
                f"[dim][{datetime.now().strftime('%H:%M:%S')}] Polling for tasks...[/dim]"
            )

            tasks = await self._get_suggested_tasks()

            if not tasks:
                # No tasks - increase backoff
                self.current_backoff = min(self.current_backoff * 1.5, self.max_backoff)
                console.print(
                    f"[dim]No tasks available. Next check in {int(self.current_backoff)}s[/dim]"
                )
                return

            # Reset backoff when tasks are found
            self.current_backoff = self.poll_interval

            # Process first task
            task = tasks[0]
            assigned_agent = task.get("assigned_coding_agent")
            if assigned_agent:
                console.print(
                    f"\n[bold green]Found task:[/bold green] {task['identifier']} - {task['title']} "
                    f"(agent: {assigned_agent})"
                )
            else:
                console.print(
                    f"\n[bold green]Found task:[/bold green] {task['identifier']} - {task['title']}"
                )

            # Find matching workflow
            workflow = self._find_workflow_for_task(task)
            if not workflow:
                console.print(
                    f"[yellow]No matching workflow for task {task['identifier']}[/yellow]"
                )
                return

            # Execute workflow
            await self._process_task(task, workflow)

            # Update stats
            self.stats["tasks_processed"] += 1

        except Exception as e:  # noqa: BLE001 - Intentionally broad: worker loop must not crash
            # Worker loop needs broad catch to remain resilient to unexpected errors
            console.print(f"[red]Error in worker loop:[/red] {escape(str(e))}")
            import traceback

            traceback.print_exc()

    async def _get_suggested_tasks(self) -> List[Dict[str, Any]]:
        """Get suggested tasks using backend's smart suggestion API.

        Uses the backend's suggestion algorithm to recommend tasks that are ready
        to work on (all dependencies complete). Results are automatically filtered
        by dependency status, sorted by priority, and filtered by coding agents
        if configured.

        If project_id is set, uses project-level suggestions.
        Otherwise uses workspace-level suggestions.

        Returns:
            List of task dictionaries (ready to work on)
        """
        try:
            # Call backend suggestion API
            # Use project-level suggest if project_id is available
            # Otherwise use workspace-level suggest
            if self.project_id is not None:
                console.print(
                    f"  [dim]Fetching suggestions from project {self._get_project_display()}[/dim]"
                )
                response = await self.task_client.suggest_project_tasks(
                    workspace_id=self.workspace_id,
                    project_id=self.project_id,
                    max_suggestions=10,
                    task_status="todo",  # Worker focuses on TODO tasks
                    include_assigned=True,  # Include assigned tasks
                    coding_agents=self.coding_agents,  # Filter by coding agents
                )
            else:
                console.print(
                    f"  [dim]Fetching suggestions from workspace {self._get_workspace_display()}[/dim]"
                )
                response = await self.task_client.suggest_tasks(
                    workspace_id=self.workspace_id,
                    max_suggestions=10,
                    status="todo",  # Worker focuses on TODO tasks
                    include_assigned=True,  # Include assigned tasks
                    coding_agents=self.coding_agents,  # Filter by coding agents
                )

            # Log suggestion metrics
            console.print(
                f"  [dim]Suggestions: {response.total_ready} ready, "
                f"{response.total_blocked} blocked[/dim]"
            )

            # Get all suggestions
            suggestions = response.suggestions

            # Convert to dict format and filter to only ready tasks
            # (is_ready=True means all dependencies are complete)
            ready_tasks: list[dict[str, Any]] = []
            for suggestion in suggestions:
                if suggestion.is_ready:
                    task_dict = suggestion.task.model_dump()

                    # Client-side filtering by assigned_coding_agent if configured
                    # This ensures we only process tasks matching our installed agents
                    if self.coding_agents:
                        assigned_agent = task_dict.get("assigned_coding_agent")
                        if assigned_agent and assigned_agent not in self.coding_agents:
                            console.print(
                                f"  [dim]Skipping {suggestion.task.identifier}: "
                                f"assigned to {assigned_agent} (not in {self.coding_agents})[/dim]"
                            )
                            continue

                    ready_tasks.append(task_dict)

                    # Log additional info for debugging
                    if suggestion.blocks and len(suggestion.blocks) > 0:
                        console.print(
                            f"  [dim]Task {suggestion.task.identifier} unblocks "
                            f"{len(suggestion.blocks)} other tasks[/dim]"
                        )

                    # Limit to 5 tasks as before
                    if len(ready_tasks) >= 5:
                        break

            return ready_tasks

        except Exception as e:  # noqa: BLE001 - Intentionally broad: API errors should not crash worker
            # Suggestion fetch is best-effort; return empty list on any error
            console.print(f"[red]Failed to fetch suggestions:[/red] {escape(str(e))}")
            return []

    def _find_workflow_for_task(self, task: Dict[str, Any]) -> Optional[Workflow]:
        """Find a workflow that matches the task."""
        # Try both 'labels' (from Task model) and 'label_names' (from legacy API responses)
        task_labels = set(task.get("labels", task.get("label_names", [])))
        task_status_raw = task.get("status")

        # Convert Status enum to string value for comparison
        task_status: Optional[str]
        if isinstance(task_status_raw, Status):
            task_status = task_status_raw.value
        elif isinstance(task_status_raw, str):
            task_status = task_status_raw
        else:
            task_status = None

        console.print(f"  [dim]Task labels: {list(task_labels)}[/dim]")
        console.print(f"  [dim]Task status: {task_status}[/dim]")

        for workflow in self.workflows.values():
            console.print(f"  [dim]Checking workflow: {workflow.name}[/dim]")
            required_labels: list[str] = []
            # Check task_created trigger
            if workflow.on.task_created:  # type: ignore[reportUnknownMemberType,unused-ignore]
                task_created_dict: dict[str, Any] = workflow.on.task_created

                required_labels.extend(task_created_dict.get("labels", []))
                console.print(
                    f"    [dim]task_created trigger requires labels: {required_labels}[/dim]"
                )
                if required_labels:
                    matches = any(label in task_labels for label in required_labels)
                    console.print(f"    [dim]Matches: {matches}[/dim]")
                    if not matches:
                        continue
                return workflow

            # Check task_updated trigger
            if workflow.on.task_updated:  # type: ignore[reportUnknownMemberType,unused-ignore]
                task_updated_dict: dict[str, Any] = workflow.on.task_updated

                required_statuses: list[str] = task_updated_dict.get("status", [])
                required_labels.extend(task_updated_dict.get("labels", []))

                console.print(
                    f"    [dim]task_updated trigger requires status: {required_statuses}, labels: {required_labels}[/dim]"
                )

                if required_statuses and task_status not in required_statuses:
                    console.print("    [dim]Status mismatch[/dim]")
                    continue
                if required_labels and not any(
                    label in task_labels for label in required_labels
                ):
                    console.print("    [dim]Labels mismatch[/dim]")
                    continue

                return workflow

        return None

    async def _get_clone_info(self, project_id: int) -> Optional[Any]:
        """
        Get repository clone information for a project.

        Uses ProjectsAPIClient for agent workers (ANYT_API_KEY).

        Args:
            project_id: ID of the project to get clone info for

        Returns:
            CloneInfo object if project has an associated repo, None otherwise
        """
        try:
            if self.projects_client and self.workspace_id:
                clone_info = await self.projects_client.get_clone_info(
                    self.workspace_id, project_id
                )
                return clone_info
            else:
                console.print(
                    "[dim]No clone client available for getting clone info[/dim]"
                )
                return None
        except Exception as e:  # noqa: BLE001 - Best-effort: clone info may not be available
            console.print(
                f"[dim]Clone info not available for project {project_id}: {e}[/dim]"
            )
            return None

    async def _get_coding_agent_settings(
        self, coding_agent_type: str
    ) -> Optional[CodingAgentSettings]:
        """
        Get coding agent settings from the backend.

        Args:
            coding_agent_type: The coding agent type string (e.g., "claude_code")

        Returns:
            CodingAgentSettings if found and has config, None otherwise
        """
        if not self.workspace_id:
            return None

        try:
            # Convert string to CodingAgentType enum
            agent_type = CodingAgentType(coding_agent_type)

            # Get API config
            from cli.config import get_effective_api_config
            from sdk.generated.api_config import APIConfig

            api_config = get_effective_api_config()
            api_url = api_config.get("api_url")
            api_key = api_config.get("api_key")

            if not api_url:
                return None

            config = APIConfig(base_path=api_url, access_token=None)

            # Fetch the coding agent config from the backend
            # Note: Pass agent_type.value because the generated SDK doesn't
            # properly convert enum to string in URL path interpolation
            agent_config = await getWorkspaceCodingAgentConfig(
                api_config_override=config,
                workspace_id=self.workspace_id,
                agent_type=agent_type.value,  # type: ignore[arg-type]
                X_API_Key=api_key,
            )

            # Return the settings if available
            if agent_config and agent_config.config:
                return agent_config.config

            return None
        except ValueError:
            # Invalid coding agent type string
            console.print(f"[dim]Unknown coding agent type: {coding_agent_type}[/dim]")
            return None
        except Exception as e:  # noqa: BLE001 - Best-effort: settings may not be configured
            console.print(f"[dim]Could not fetch coding agent settings: {e}[/dim]")
            return None

    async def _clone_repo(self, clone_url: str, repo_dir: Path) -> None:
        """
        Clone git repository for task execution (shallow clone).

        Args:
            clone_url: Git clone URL (includes authentication token)
            repo_dir: Directory to clone into

        Raises:
            subprocess.CalledProcessError: If git clone fails
        """
        # Remove existing directory if present
        if repo_dir.exists():
            shutil.rmtree(repo_dir)

        # Ensure parent directory exists
        repo_dir.parent.mkdir(parents=True, exist_ok=True)

        # Clone repository with shallow clone (suppress output to hide credentials)
        result = subprocess.run(
            ["git", "clone", "--depth", "1", clone_url, str(repo_dir)],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            # Sanitize error message (remove potential credentials)
            error_msg = result.stderr.replace(clone_url, "[REDACTED]")
            raise subprocess.CalledProcessError(
                result.returncode,
                ["git", "clone", "--depth", "1", "[REDACTED]", str(repo_dir)],
                output=result.stdout,
                stderr=error_msg,
            )

    async def _check_remote_branch_exists(
        self, repo_dir: Path, branch_name: str
    ) -> bool:
        """
        Check if a branch exists on the remote repository.

        Args:
            repo_dir: Repository directory
            branch_name: Name of the branch to check

        Returns:
            True if branch exists on remote, False otherwise
        """
        result = subprocess.run(
            ["git", "ls-remote", "--heads", "origin", branch_name],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        # If the branch exists, ls-remote will output a line with the ref
        return result.returncode == 0 and branch_name in result.stdout

    async def _checkout_existing_branch(self, repo_dir: Path, branch_name: str) -> None:
        """
        Fetch and checkout an existing remote branch.

        Args:
            repo_dir: Repository directory
            branch_name: Name of the branch to checkout

        Raises:
            subprocess.CalledProcessError: If git operations fail
        """
        # Fetch the specific branch from remote
        result = subprocess.run(
            ["git", "fetch", "origin", f"{branch_name}:{branch_name}"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                ["git", "fetch", "origin", f"{branch_name}:{branch_name}"],
                output=result.stdout,
                stderr=result.stderr,
            )

        # Checkout the fetched branch
        result = subprocess.run(
            ["git", "checkout", branch_name],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                ["git", "checkout", branch_name],
                output=result.stdout,
                stderr=result.stderr,
            )

    async def _create_task_branch(self, repo_dir: Path, branch_name: str) -> None:
        """
        Create and checkout a new git branch for the task.

        Args:
            repo_dir: Repository directory
            branch_name: Name of the branch to create (e.g., "dev-123")

        Raises:
            subprocess.CalledProcessError: If git checkout fails
        """
        # Create and checkout new branch from current HEAD
        result = subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                ["git", "checkout", "-b", branch_name],
                output=result.stdout,
                stderr=result.stderr,
            )

    async def _setup_task_branch(self, repo_dir: Path, branch_name: str) -> bool:
        """
        Set up the task branch - either checkout existing or create new.

        Checks if the branch exists on remote:
        - If exists: fetch and checkout the existing branch
        - If not exists: create a new branch from the default branch

        Args:
            repo_dir: Repository directory
            branch_name: Name of the branch (e.g., "dev-123")

        Returns:
            True if using an existing branch, False if created new

        Raises:
            subprocess.CalledProcessError: If git operations fail
        """
        # Check if branch exists on remote
        branch_exists = await self._check_remote_branch_exists(repo_dir, branch_name)

        if branch_exists:
            console.print(
                f"[cyan]Found existing branch on remote: {branch_name}[/cyan]"
            )
            await self._checkout_existing_branch(repo_dir, branch_name)
            console.print(
                f"[green]✓[/green] Checked out existing branch: {branch_name}"
            )
            return True
        else:
            console.print(f"[cyan]Creating new branch: {branch_name}[/cyan]")
            await self._create_task_branch(repo_dir, branch_name)
            console.print(f"[green]✓[/green] Created new branch: {branch_name}")
            return False

    async def _cleanup_task_workspace(self, task_workspace: Path) -> None:
        """
        Cleanup task workspace directory after execution.

        Args:
            task_workspace: Task-specific workspace directory to remove
        """
        if not task_workspace.exists():
            return

        def _handle_remove_readonly(func: Any, path: str, exc_info: Any) -> None:
            """Handle removal of read-only files on Windows.

            Git pack files are often read-only and locked on Windows.
            This handler removes the read-only flag and retries deletion.
            """
            # Clear the read-only flag and retry
            os.chmod(path, stat.S_IWRITE)
            func(path)

        try:
            if sys.platform == "win32":
                # On Windows, use onerror handler to deal with read-only Git files
                shutil.rmtree(task_workspace, onerror=_handle_remove_readonly)
            else:
                shutil.rmtree(task_workspace)
            console.print(f"[dim]Cleaned up workspace: {task_workspace}[/dim]")
        except Exception as e:  # noqa: BLE001 - Best-effort cleanup
            console.print(
                f"[yellow]Warning: Failed to cleanup {task_workspace}: {e}[/yellow]"
            )

    def _should_clone_repo(self, workflow: Workflow) -> bool:
        """Determine if repository should be cloned for this workflow.

        Cloning is enabled if:
        - Global --clone-repos flag is set, OR
        - Workflow settings specify clone_repo: true

        Also ensures clone clients are initialized when cloning is requested.

        Args:
            workflow: The workflow being executed

        Returns:
            True if repo should be cloned
        """
        # Check global flag (command-line override)
        if self.clone_repos:
            return True

        # Check workflow settings
        if workflow.settings and workflow.settings.clone_repo:
            # Lazy-initialize clone clients if not already done
            if not self.projects_client:
                self._init_clone_clients()
                if self.projects_client:
                    console.print("[dim]Clone client initialized[/dim]")
                else:
                    console.print(
                        "[yellow]Warning: Workflow requests clone_repo but clone client "
                        "could not be initialized. Ensure ANYT_API_KEY is set.[/yellow]"
                    )
                    return False
            return True

        return False

    def _should_cleanup_workspace(self, workflow: Workflow) -> bool:
        """Determine if task workspace should be cleaned up after execution.

        Cleanup happens only if both:
        - Global --no-cleanup flag is NOT set (cleanup_workspaces=True), AND
        - Workflow settings specify cleanup_workspace: true (default)

        Args:
            workflow: The workflow being executed

        Returns:
            True if workspace should be cleaned up
        """
        # Check global flag first
        if not self.cleanup_workspaces:
            return False

        # Check workflow settings (defaults to True)
        if workflow.settings and not workflow.settings.cleanup_workspace:
            return False

        return True

    async def _process_task(self, task: Dict[str, Any], workflow: Workflow) -> None:
        """Process a task using a workflow.

        If clone_repo is enabled (via workflow settings or --clone-repos flag)
        and the task's project has a linked repository, the repo will be cloned
        to a task-specific workspace directory and a branch will be created.

        Workflow execution happens in either:
        - The cloned task workspace (if clone_repo enabled and repo available)
        - The original workspace_dir (default, for local development)
        """
        identifier = task["identifier"]
        task_workspace: Optional[Path] = None
        cloned_repo = False

        # Determine if we should clone for this workflow
        should_clone = self._should_clone_repo(workflow)

        # Get assigned coding agent from task
        assigned_coding_agent = task.get("assigned_coding_agent")

        # Fetch coding agent settings from backend if agent is assigned
        coding_agent_settings: Optional[CodingAgentSettings] = None
        if assigned_coding_agent:
            coding_agent_settings = await self._get_coding_agent_settings(
                assigned_coding_agent
            )

        try:
            # Determine execution workspace
            execution_dir = self.workspace_dir

            # Clone repository if enabled and project has one
            if should_clone:
                project_id = self._get_project_id_from_task(task)
                if project_id:
                    clone_info = await self._get_clone_info(project_id)
                    if clone_info:
                        # Create task-specific workspace
                        task_workspace = self.workspace_dir / f"task-{identifier}"

                        console.print("[cyan]Cloning repository...[/cyan]")
                        await self._clone_repo(clone_info.clone_url, task_workspace)
                        console.print(
                            f"[green]✓[/green] Repository cloned to {task_workspace}"
                        )

                        # Set up task branch (checkout existing or create new)
                        branch_name = identifier.lower()
                        await self._setup_task_branch(task_workspace, branch_name)

                        execution_dir = task_workspace
                        cloned_repo = True
                    else:
                        console.print(
                            f"[dim]No repository linked to project {project_id}, "
                            f"using current directory[/dim]"
                        )
                else:
                    console.print(
                        "[dim]Task has no project, using current directory[/dim]"
                    )

            # Update task to active
            await self._update_task_status(identifier, Status.ACTIVE)

            # Execute workflow
            console.print(f"[cyan]Executing workflow in: {execution_dir}[/cyan]")
            execution = await self.executor.execute_workflow(
                workflow,
                task,
                execution_dir,
                coding_agent_settings=coding_agent_settings,
            )

            # Update stats based on execution result
            if execution.status == "success":
                assert isinstance(self.stats["tasks_succeeded"], int)
                self.stats["tasks_succeeded"] += 1
            else:
                # Workflow failed
                assert isinstance(self.stats["tasks_failed"], int)
                self.stats["tasks_failed"] += 1
                await self._update_task_status(identifier, Status.BLOCKED)
                console.print(
                    f"[yellow]Task {identifier} marked as BLOCKED due to workflow failure[/yellow]"
                )

        except Exception as e:  # noqa: BLE001 - Intentionally broad: must record all failures
            # Task processing needs broad catch to properly record failures
            console.print(f"\n[red]Failed to process task:[/red] {escape(str(e))}")
            assert isinstance(self.stats["tasks_failed"], int)
            self.stats["tasks_failed"] += 1

            # Update task to BLOCKED on exception
            try:
                await self._update_task_status(identifier, Status.BLOCKED)
                console.print(
                    f"[yellow]Task {identifier} marked as BLOCKED due to exception[/yellow]"
                )
            except Exception as status_error:  # noqa: BLE001 - Intentionally broad: best-effort status update
                # Status update is best-effort; don't mask original error
                console.print(
                    f"[red]Failed to update task status to blocked: {status_error}[/red]"
                )

            import traceback

            traceback.print_exc()

        finally:
            # Cleanup task workspace if cloned
            if (
                cloned_repo
                and task_workspace
                and self._should_cleanup_workspace(workflow)
            ):
                await self._cleanup_task_workspace(task_workspace)

    def _get_project_id_from_task(self, task: Dict[str, Any]) -> Optional[int]:
        """Extract project ID from task dict.

        Args:
            task: Task dictionary (may contain project as nested dict or project_id)

        Returns:
            Project ID if available, None otherwise
        """
        # Check for nested project object (common in API responses)
        project = task.get("project")
        if isinstance(project, dict):
            return project.get("id")

        # Fall back to direct project_id field
        return task.get("project_id")

    async def _update_task_status(self, task_id: str, status: Status) -> Task:
        """Update task status using TaskService."""
        try:
            return await self.task_service.update_task_status(task_id, status)
        except Exception as e:  # noqa: BLE001 - Re-raise after logging; need to catch all API errors
            # Log warning and re-raise to allow caller to handle
            console.print(
                f"[yellow]Warning: Failed to update task status: {e}[/yellow]"
            )
            raise

    def _print_stats(self) -> None:
        """Print worker statistics."""
        started_at = self.stats["started_at"]
        assert isinstance(started_at, datetime)
        uptime = datetime.now() - started_at
        hours = uptime.total_seconds() / 3600

        table = Table(title="Worker Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Uptime", f"{hours:.2f} hours")
        table.add_row("Tasks Processed", str(self.stats["tasks_processed"]))
        table.add_row("Tasks Succeeded", str(self.stats["tasks_succeeded"]))
        table.add_row("Tasks Failed", str(self.stats["tasks_failed"]))

        tasks_processed = self.stats["tasks_processed"]
        assert isinstance(tasks_processed, int)
        if tasks_processed > 0:
            tasks_succeeded = self.stats["tasks_succeeded"]
            assert isinstance(tasks_succeeded, int)
            success_rate = tasks_succeeded / tasks_processed * 100
            table.add_row("Success Rate", f"{success_rate:.1f}%")

        console.print()
        console.print(table)


async def main() -> None:
    """Entry point for the worker."""
    from cli.config import WorkspaceConfig

    workspace_dir = Path.cwd()
    ws_config = WorkspaceConfig.load(workspace_dir)
    if not ws_config:
        raise RuntimeError(
            f"No workspace config found at {workspace_dir}/.anyt/anyt.json. "
            "Initialize workspace with 'anyt init'"
        )

    coordinator = TaskCoordinator(
        workspace_dir=workspace_dir,
        workspace_id=ws_config.workspace_id,
    )
    await coordinator.run()


if __name__ == "__main__":
    from cli.utils.platform import run_async

    run_async(main())
