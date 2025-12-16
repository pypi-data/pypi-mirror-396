"""Secure API key storage using system keyring.

This module provides secure storage and retrieval of AnyTask API keys
using the system keyring (Keychain on macOS, Credential Manager on Windows, etc.).
"""

import keyring
from keyring.errors import KeyringError
from typing import Optional


class APIKeyStore:
    """Manage AnyTask API keys using system keyring."""

    SERVICE_NAME = "anytask-cli"
    KEY_NAME = "api_key"

    @classmethod
    def set_api_key(cls, api_key: str) -> None:
        """Store API key securely in system keyring.

        Args:
            api_key: The API key to store

        Raises:
            ValueError: If api_key is empty
            KeyringError: If keyring operation fails
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")

        try:
            keyring.set_password(cls.SERVICE_NAME, cls.KEY_NAME, api_key)
        except KeyringError as e:
            raise KeyringError(f"Failed to store API key: {e}") from e

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Retrieve API key from system keyring.

        Returns:
            API key if found, None otherwise

        Raises:
            KeyringError: If keyring operation fails
        """
        try:
            return keyring.get_password(cls.SERVICE_NAME, cls.KEY_NAME)
        except KeyringError as e:
            raise KeyringError(f"Failed to retrieve API key: {e}") from e

    @classmethod
    def delete_api_key(cls) -> bool:
        """Delete API key from system keyring.

        Returns:
            True if API key was deleted, False if not found

        Raises:
            KeyringError: If keyring operation fails
        """
        try:
            # Check if API key exists
            if cls.get_api_key() is None:
                return False

            keyring.delete_password(cls.SERVICE_NAME, cls.KEY_NAME)
            return True
        except KeyringError as e:
            raise KeyringError(f"Failed to delete API key: {e}") from e

    @classmethod
    def has_api_key(cls) -> bool:
        """Check if an API key is stored in keyring.

        Returns:
            True if API key exists, False otherwise
        """
        try:
            return cls.get_api_key() is not None
        except KeyringError:
            return False
