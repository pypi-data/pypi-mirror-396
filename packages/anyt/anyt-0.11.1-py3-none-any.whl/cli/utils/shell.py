"""Shell detection and configuration utilities."""

import os
import sys
from pathlib import Path


def detect_shell() -> tuple[str, Path]:
    """Detect current shell and config file location.

    Supports Unix shells (zsh, bash, fish) and Windows (PowerShell, cmd).

    Returns:
        Tuple of (shell_name, config_path)

    Examples:
        >>> shell_name, config_path = detect_shell()
        >>> shell_name
        'zsh'
        >>> config_path
        PosixPath('/Users/user/.zshrc')
    """
    # Windows detection
    if sys.platform == "win32":
        # Check for PowerShell vs cmd
        # PSModulePath is typically set in PowerShell environments
        if os.environ.get("PSModulePath"):
            # PowerShell - use profile location
            # PowerShell Core: ~/Documents/PowerShell/Microsoft.PowerShell_profile.ps1
            # Windows PowerShell: ~/Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1
            ps_core_profile = (
                Path.home()
                / "Documents"
                / "PowerShell"
                / "Microsoft.PowerShell_profile.ps1"
            )
            ps_win_profile = (
                Path.home()
                / "Documents"
                / "WindowsPowerShell"
                / "Microsoft.PowerShell_profile.ps1"
            )

            # Prefer PowerShell Core if its profile exists
            if ps_core_profile.exists():
                return "powershell", ps_core_profile
            elif ps_win_profile.exists():
                return "powershell", ps_win_profile
            else:
                # Default to PowerShell Core location (will be created)
                return "powershell", ps_core_profile
        else:
            # Cmd.exe - no standard profile, use a placeholder
            return "cmd", Path.home() / ".anyt" / "env.bat"

    # Unix shell detection
    shell = os.environ.get("SHELL", "")

    if "zsh" in shell:
        return "zsh", Path.home() / ".zshrc"
    elif "bash" in shell:
        # Check which exists: .bashrc or .bash_profile
        bashrc = Path.home() / ".bashrc"
        bash_profile = Path.home() / ".bash_profile"
        return "bash", bashrc if bashrc.exists() else bash_profile
    elif "fish" in shell:
        return "fish", Path.home() / ".config" / "fish" / "config.fish"
    else:
        return "unknown", Path.home() / ".profile"


def get_shell_export_command(shell_name: str, api_key: str) -> str:
    """Get the shell-specific export command for setting API key.

    Args:
        shell_name: Name of the shell (zsh, bash, fish, powershell, cmd, unknown)
        api_key: The API key value to export

    Returns:
        Shell-specific command to export the API key

    Examples:
        >>> get_shell_export_command("zsh", "anyt_agent_xyz")
        'export ANYT_API_KEY=anyt_agent_xyz'
        >>> get_shell_export_command("fish", "anyt_agent_xyz")
        'set -x ANYT_API_KEY anyt_agent_xyz'
        >>> get_shell_export_command("powershell", "anyt_agent_xyz")
        '$env:ANYT_API_KEY = "anyt_agent_xyz"'
    """
    if shell_name == "fish":
        return f"set -x ANYT_API_KEY {api_key}"
    elif shell_name == "powershell":
        return f'$env:ANYT_API_KEY = "{api_key}"'
    elif shell_name == "cmd":
        return f"set ANYT_API_KEY={api_key}"
    else:
        return f"export ANYT_API_KEY={api_key}"


def get_persistence_command(shell_name: str, config_path: Path, api_key: str) -> str:
    """Get command to persist API key to shell profile.

    Args:
        shell_name: Name of the shell (zsh, bash, fish, powershell, cmd, unknown)
        config_path: Path to shell config file
        api_key: The API key value to persist

    Returns:
        Command to add API key to shell profile

    Examples:
        >>> get_persistence_command("zsh", Path("~/.zshrc"), "anyt_agent_xyz")
        "echo 'export ANYT_API_KEY=anyt_agent_xyz' >> ~/.zshrc"
    """
    export_cmd = get_shell_export_command(shell_name, api_key)

    if shell_name == "powershell":
        # PowerShell: Add-Content or >> redirection
        return f"Add-Content -Path \"{config_path}\" -Value '{export_cmd}'"
    elif shell_name == "cmd":
        # cmd: echo to batch file
        return f'echo {export_cmd}>> "{config_path}"'
    else:
        # Unix shells
        return f"echo '{export_cmd}' >> {config_path}"


def get_source_command(shell_name: str, config_path: Path) -> str:
    """Get command to reload shell configuration.

    Args:
        shell_name: Name of the shell (zsh, bash, fish, powershell, cmd, unknown)
        config_path: Path to shell config file

    Returns:
        Command to reload shell config

    Examples:
        >>> get_source_command("zsh", Path("~/.zshrc"))
        'source ~/.zshrc'
        >>> get_source_command("powershell", Path("profile.ps1"))
        '. profile.ps1'
    """
    if shell_name == "powershell":
        return f'. "{config_path}"'
    elif shell_name == "cmd":
        return f'call "{config_path}"'
    else:
        return f"source {config_path}"


def get_permanent_env_instructions(shell_name: str, api_key: str) -> str:
    """Get platform-specific instructions for permanently setting environment variable.

    Args:
        shell_name: Name of the shell
        api_key: The API key value

    Returns:
        Human-readable instructions for permanently setting the API key
    """
    if shell_name == "powershell":
        return (
            "To set permanently (user scope):\n"
            f'  [Environment]::SetEnvironmentVariable("ANYT_API_KEY", "{api_key}", "User")\n'
            "\n"
            "Or via System Settings:\n"
            "  1. Open 'Edit environment variables for your account'\n"
            "  2. Click 'New' under User variables\n"
            "  3. Variable name: ANYT_API_KEY\n"
            f"  4. Variable value: {api_key}"
        )
    elif shell_name == "cmd":
        return (
            "To set permanently:\n"
            f"  setx ANYT_API_KEY {api_key}\n"
            "\n"
            "Or via System Settings:\n"
            "  1. Open 'Edit environment variables for your account'\n"
            "  2. Click 'New' under User variables\n"
            "  3. Variable name: ANYT_API_KEY\n"
            f"  4. Variable value: {api_key}"
        )
    else:
        shell_name_display, config_path = detect_shell()
        export_cmd = get_shell_export_command(shell_name, api_key)
        return (
            f"Add to your shell profile ({config_path}):\n"
            f"  {export_cmd}\n"
            "\n"
            f"Then reload:\n"
            f"  source {config_path}"
        )
