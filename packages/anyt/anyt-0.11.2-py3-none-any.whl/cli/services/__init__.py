"""Service layer for AnyTask CLI.

The service layer encapsulates business logic and provides a clean interface
between CLI commands and API clients. Services handle:

- Business rules and validation
- Complex workflows combining multiple API calls
- Context resolution (workspace, project, etc.)
- Error handling and user-friendly messages

Services should be used by:
- CLI commands (src/cli/commands/)
- MCP server (src/anytask_mcp/)
- Future integrations

Services should NOT be used for:
- Simple pass-through operations (use clients directly)
- Pure UI/rendering logic (that belongs in commands)

Use direct imports:
    from cli.services.task_service import TaskService
    from cli.services.workspace_service import WorkspaceService
    from cli.services.base import BaseService
"""
