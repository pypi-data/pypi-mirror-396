"""Utility functions for managing .gitignore files."""

from pathlib import Path


def is_git_repository(directory: Path) -> bool:
    """Check if the given directory is a git repository.

    Args:
        directory: Path to check for git repository

    Returns:
        True if directory contains a .git folder, False otherwise
    """
    git_dir = directory / ".git"
    return git_dir.exists() and git_dir.is_dir()


def is_pattern_in_gitignore(gitignore_path: Path, pattern: str) -> bool:
    """Check if a pattern is already in the gitignore file.

    Args:
        gitignore_path: Path to the .gitignore file
        pattern: Pattern to check for (e.g., ".anyt")

    Returns:
        True if the pattern exists in the file, False otherwise
    """
    if not gitignore_path.exists():
        return False

    content = gitignore_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check for exact match or with trailing slash (directory pattern)
    patterns_to_check = [pattern, f"{pattern}/"]
    for line in lines:
        stripped = line.strip()
        if stripped in patterns_to_check:
            return True

    return False


def add_pattern_to_gitignore(gitignore_path: Path, pattern: str) -> bool:
    """Add a pattern to the gitignore file.

    Args:
        gitignore_path: Path to the .gitignore file
        pattern: Pattern to add (e.g., ".anyt")

    Returns:
        True if pattern was added, False if already present
    """
    if is_pattern_in_gitignore(gitignore_path, pattern):
        return False

    # Ensure pattern ends with / for directory matching
    if not pattern.endswith("/"):
        pattern = f"{pattern}/"

    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding="utf-8")
        # Ensure there's a newline before our pattern if file doesn't end with one
        if content and not content.endswith("\n"):
            content += "\n"
        content += f"{pattern}\n"
        gitignore_path.write_text(content, encoding="utf-8")
    else:
        # Create new file with the pattern
        gitignore_path.write_text(f"{pattern}\n", encoding="utf-8")

    return True


def ensure_anyt_in_gitignore(directory: Path) -> tuple[bool, str]:
    """Ensure .anyt is in .gitignore for a git repository.

    This function implements the following logic:
    1. If not a git repository: no action
    2. If git repository with .gitignore: add .anyt if not present
    3. If git repository without .gitignore: create it with .anyt

    Args:
        directory: The directory to check (should be the project root)

    Returns:
        Tuple of (action_taken, message)
        - action_taken: True if any change was made
        - message: Description of what was done
    """
    if not is_git_repository(directory):
        return False, "Not a git repository, no action taken"

    gitignore_path = directory / ".gitignore"
    pattern = ".anyt"

    if gitignore_path.exists():
        if is_pattern_in_gitignore(gitignore_path, pattern):
            return False, ".anyt already in .gitignore"
        else:
            add_pattern_to_gitignore(gitignore_path, pattern)
            return True, "Added .anyt/ to existing .gitignore"
    else:
        add_pattern_to_gitignore(gitignore_path, pattern)
        return True, "Created .gitignore with .anyt/"
