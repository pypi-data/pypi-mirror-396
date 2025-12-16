"""AnyTask CLI - Command-line interface for AnyTask task management."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("anyt")
except PackageNotFoundError:
    # Package not installed, use development version
    __version__ = "0.0.0.dev"
