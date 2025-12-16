"""
Secrets management for AnyTask Worker workflows.

Provides secure storage and retrieval of workflow secrets using keyring.
"""

import re
from typing import Any, Dict, List, Optional, cast

import keyring
from keyring.errors import KeyringError


class SecretsManager:
    """Manage workflow secrets using system keyring."""

    SERVICE_NAME = "anyt-worker"

    def __init__(self) -> None:
        """Initialize the secrets manager."""
        # Verify keyring is available
        try:
            keyring.get_keyring()
        except KeyringError as e:
            raise RuntimeError(
                f"Keyring not available: {e}. "
                "Please ensure you have a supported keyring backend installed."
            ) from e

    def set_secret(self, name: str, value: str) -> None:
        """
        Store a secret in the keyring.

        Args:
            name: Secret name (e.g., 'PRODUCTION_API_KEY')
            value: Secret value to store

        Raises:
            ValueError: If name or value is empty
            KeyringError: If keyring operation fails
        """
        if not name or not name.strip():
            raise ValueError("Secret name cannot be empty")
        if not value or not value.strip():
            raise ValueError("Secret value cannot be empty")

        try:
            keyring.set_password(self.SERVICE_NAME, name, value)
        except KeyringError as e:
            raise KeyringError(f"Failed to store secret '{name}': {e}") from e

    def get_secret(self, name: str) -> Optional[str]:
        """
        Retrieve a secret from the keyring.

        Args:
            name: Secret name to retrieve

        Returns:
            Secret value if found, None otherwise

        Raises:
            KeyringError: If keyring operation fails
        """
        if not name or not name.strip():
            raise ValueError("Secret name cannot be empty")

        try:
            return keyring.get_password(self.SERVICE_NAME, name)
        except KeyringError as e:
            raise KeyringError(f"Failed to retrieve secret '{name}': {e}") from e

    def delete_secret(self, name: str) -> bool:
        """
        Delete a secret from the keyring.

        Args:
            name: Secret name to delete

        Returns:
            True if secret was deleted, False if not found

        Raises:
            KeyringError: If keyring operation fails
        """
        if not name or not name.strip():
            raise ValueError("Secret name cannot be empty")

        try:
            # Check if secret exists
            if self.get_secret(name) is None:
                return False

            keyring.delete_password(self.SERVICE_NAME, name)
            return True
        except KeyringError as e:
            raise KeyringError(f"Failed to delete secret '{name}': {e}") from e

    def list_secrets(self) -> List[str]:
        """
        List all stored secret names.

        Note: This relies on keyring backend support. Some backends may not
        support listing credentials.

        Returns:
            List of secret names

        Raises:
            NotImplementedError: If keyring backend doesn't support listing
        """
        # Note: keyring doesn't have a standard API for listing all credentials
        # This would need backend-specific implementation
        # For now, we'll maintain a separate index
        raise NotImplementedError(
            "Listing secrets is not supported by the keyring API. "
            "Consider using a metadata file to track secret names."
        )

    def interpolate_secrets(self, value: str) -> str:
        """
        Replace ${{ secrets.NAME }} placeholders with actual secret values.

        Args:
            value: String containing secret placeholders

        Returns:
            String with secrets replaced

        Raises:
            ValueError: If a referenced secret is not found
            KeyringError: If keyring operation fails

        Example:
            >>> manager = SecretsManager()
            >>> manager.set_secret("API_KEY", "secret123")
            >>> result = manager.interpolate_secrets("Key: ${{ secrets.API_KEY }}")
            >>> print(result)
            "Key: secret123"
        """

        def replace_secret(match: "re.Match[str]") -> str:
            secret_name = match.group(1).strip()
            secret_value = self.get_secret(secret_name)

            if secret_value is None:
                raise ValueError(
                    f"Secret '{secret_name}' not found. "
                    f"Use 'anyt worker secret set {secret_name}' to add it."
                )

            return secret_value

        # Match ${{ secrets.SECRET_NAME }} with optional whitespace
        pattern = r"\$\{\{\s*secrets\.([A-Za-z_][A-Za-z0-9_]*)\s*\}\}"
        return re.sub(pattern, replace_secret, value)

    def interpolate_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively interpolate secrets in a dictionary.

        Args:
            data: Dictionary that may contain secret placeholders

        Returns:
            Dictionary with secrets interpolated

        Raises:
            ValueError: If a referenced secret is not found
            KeyringError: If keyring operation fails
        """
        result: Dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.interpolate_secrets(value)
            elif isinstance(value, dict):
                result[key] = self.interpolate_dict(value)
            elif isinstance(value, list):
                value_list: list[Any] = cast(list[Any], value)  # type: ignore[redundant-cast]
                result[key] = [
                    self.interpolate_secrets(item) if isinstance(item, str) else item
                    for item in value_list
                ]
            else:
                result[key] = value
        return result

    def mask_secret(self, value: str) -> str:
        """
        Mask a secret value for logging.

        Args:
            value: Secret value to mask

        Returns:
            Masked value (e.g., "***")
        """
        if not value:
            return value
        if len(value) <= 4:
            return "***"
        return f"{value[:2]}***{value[-2:]}"
