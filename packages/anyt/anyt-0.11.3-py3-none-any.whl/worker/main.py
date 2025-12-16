"""
Worker CLI entry point.

This module provides the main entry point for the AnyTask Worker CLI.
"""

from worker.commands import app


def main() -> None:
    """Main entry point for the worker CLI."""
    app()


if __name__ == "__main__":
    main()
