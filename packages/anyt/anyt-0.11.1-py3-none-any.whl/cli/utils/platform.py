"""Cross-platform utilities for Windows, macOS, and Linux compatibility."""

import asyncio
import subprocess
import sys
from typing import Any


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def is_macos() -> bool:
    """Check if running on macOS."""
    return sys.platform == "darwin"


def is_linux() -> bool:
    """Check if running on Linux."""
    return sys.platform.startswith("linux")


def get_platform_name() -> str:
    """Get normalized platform name.

    Returns:
        One of: 'windows', 'macos', 'linux'
    """
    if is_windows():
        return "windows"
    elif is_macos():
        return "macos"
    else:
        return "linux"


def run_async(coro: Any) -> Any:
    """Run an async coroutine with asyncio.run().

    This is a simple wrapper around asyncio.run() for consistency.
    On Windows with Python 3.8+, ProactorEventLoop is the default
    and supports both HTTP clients (httpx) and subprocesses.

    Note: We do NOT change the event loop policy to SelectorEventLoop
    because that would break subprocess support on Windows.

    Args:
        coro: The coroutine to run

    Returns:
        The result of the coroutine

    Example:
        async def fetch_data():
            async with httpx.AsyncClient() as client:
                return await client.get(url)

        result = run_async(fetch_data())
    """
    return asyncio.run(coro)


def subprocess_run_detached(
    cmd: list[str],
    **kwargs: Any,
) -> subprocess.CompletedProcess[Any]:
    """Run a subprocess in a detached/background manner, cross-platform.

    On Unix, uses start_new_session=True to create a new process group.
    On Windows, uses CREATE_NEW_PROCESS_GROUP creation flag.

    Args:
        cmd: Command and arguments to run
        **kwargs: Additional arguments passed to subprocess.run()

    Returns:
        CompletedProcess instance
    """
    if is_windows():
        # Windows: use CREATE_NEW_PROCESS_GROUP flag
        creationflags = kwargs.pop("creationflags", 0)
        creationflags |= subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
        return subprocess.run(cmd, creationflags=creationflags, **kwargs)
    else:
        # Unix: use start_new_session
        return subprocess.run(cmd, start_new_session=True, **kwargs)


def get_file_permission_fix_command(path: str, permission: str = "rw") -> str | None:
    """Get platform-specific command to fix file permissions.

    Args:
        path: Path to the file
        permission: Permission string ('r', 'w', 'rw', 'x', 'rwx')

    Returns:
        Command string to fix permissions, or None if not applicable on Windows
    """
    if is_windows():
        # Windows doesn't use chmod; permissions are managed via ACLs
        # Return None to indicate no simple fix command available
        return None

    # Map permission string to chmod format
    perm_map = {
        "r": "u+r",
        "w": "u+w",
        "rw": "u+rw",
        "x": "u+x",
        "rwx": "u+rwx",
    }
    chmod_perm = perm_map.get(permission, f"u+{permission}")
    return f"chmod {chmod_perm} {path}"


def get_file_permission_instructions(path: str, permission: str = "rw") -> str:
    """Get platform-specific instructions for fixing file permissions.

    Args:
        path: Path to the file
        permission: Permission string ('r', 'w', 'rw', 'x', 'rwx')

    Returns:
        Human-readable instructions for fixing permissions
    """
    if is_windows():
        return (
            f"Fix permissions for {path}:\n"
            f"  1. Right-click the file and select 'Properties'\n"
            f"  2. Go to the 'Security' tab\n"
            f"  3. Click 'Edit' and ensure your user has the required permissions"
        )

    cmd = get_file_permission_fix_command(path, permission)
    return f"Fix permissions:\n  {cmd}"
