"""Global configuration management for AnyTask CLI.

This module provides management of global user configuration stored in ~/.anyt/auth.json.
This is separate from workspace-specific configuration stored in .anyt/anyt.json.
"""

import json
import os
import stat
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class GlobalAuthConfig(BaseModel):
    """Global authentication configuration stored in ~/.anyt/auth.json.

    This stores the API key in a user-readable-only JSON file in the home directory.
    This is the preferred persistent storage mechanism, with keyring as fallback.
    """

    api_key: Optional[str] = None

    @classmethod
    def get_config_dir(cls) -> Path:
        """Get the global config directory path.

        Uses ANYT_CONFIG_DIR env var if set (for testing), otherwise ~/.anyt/

        Returns:
            Path to the global config directory
        """
        env_dir = os.getenv("ANYT_CONFIG_DIR")
        if env_dir:
            return Path(env_dir)
        return Path.home() / ".anyt"

    @classmethod
    def get_config_path(cls) -> Path:
        """Get the path to the global auth config file.

        Returns:
            Path to ~/.anyt/auth.json (or test override)
        """
        return cls.get_config_dir() / "auth.json"

    @classmethod
    def load(cls) -> Optional["GlobalAuthConfig"]:
        """Load global auth configuration from file.

        Returns:
            GlobalAuthConfig if found and valid, None otherwise.
            Silently returns None on any error (file not found, invalid JSON, etc.)
        """
        config_path = cls.get_config_path()

        if not config_path.exists():
            return None

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return cls(**data)
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            # JSON parsing errors, file system errors, or Pydantic validation errors
            # Silently return None - this is best-effort loading
            return None

    def save(self) -> None:
        """Save global auth configuration to file with secure permissions.

        Creates the ~/.anyt directory if it doesn't exist.
        Sets file permissions to 0600 (user read/write only) for security.

        Raises:
            RuntimeError: If the file cannot be saved.
        """
        config_path = self.get_config_path()

        # Ensure directory exists with secure permissions
        config_dir = config_path.parent
        if not config_dir.exists():
            config_dir.mkdir(parents=True, mode=0o700)

        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.model_dump(exclude_none=True), f, indent=2)

            # Set secure permissions (user read/write only)
            # Windows doesn't support Unix-style permissions, so wrap in try/except
            try:
                os.chmod(config_path, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
            except (OSError, AttributeError):
                # AttributeError: stat.S_IRUSR not available on some platforms
                # OSError: chmod not supported (e.g., some Windows configurations)
                pass
        except OSError as e:
            raise RuntimeError(f"Failed to save global auth config: {e}")

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Get API key from global config file.

        Convenience method for loading config and extracting API key.

        Returns:
            API key if found in config, None otherwise.
        """
        config = cls.load()
        return config.api_key if config else None

    @classmethod
    def set_api_key(cls, api_key: str) -> None:
        """Set API key in global config file.

        Creates or updates the config file with the provided API key.

        Args:
            api_key: The API key to store.

        Raises:
            ValueError: If api_key is empty.
            RuntimeError: If the file cannot be saved.
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")

        config = GlobalAuthConfig(api_key=api_key)
        config.save()

    @classmethod
    def delete_api_key(cls) -> bool:
        """Delete API key by removing the config file.

        Returns:
            True if file was deleted, False if it didn't exist.
        """
        config_path = cls.get_config_path()
        if config_path.exists():
            config_path.unlink()
            return True
        return False

    @classmethod
    def has_api_key(cls) -> bool:
        """Check if an API key is stored in global config.

        Returns:
            True if API key exists in config, False otherwise.
        """
        api_key = cls.get_api_key()
        return api_key is not None and len(api_key) > 0
