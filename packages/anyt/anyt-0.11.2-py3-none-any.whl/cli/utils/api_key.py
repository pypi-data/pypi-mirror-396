"""API key validation utilities."""


def mask_api_key(api_key: str) -> str:
    """Mask an API key for display purposes.

    Shows first 16 characters and last 4 characters, masking the rest.

    Args:
        api_key: The API key to mask

    Returns:
        Masked API key string

    Examples:
        >>> mask_api_key("anyt_agent_1234567890abcdefghijklmno")
        'anyt_agent_12345...lmno'
        >>> mask_api_key("short")
        '***'
    """
    if not api_key or len(api_key) < 20:
        return "***"
    return f"{api_key[:16]}...{api_key[-4:]}"


def validate_api_key_format(api_key: str) -> bool:
    """Validate API key format.

    API keys must:
    - Start with 'anyt_agent_'
    - Be at least 20 characters long

    Args:
        api_key: The API key to validate

    Returns:
        True if valid format, False otherwise

    Examples:
        >>> validate_api_key_format("anyt_agent_1234567890abcdef")
        True
        >>> validate_api_key_format("invalid_key")
        False
        >>> validate_api_key_format("anyt_agent_short")
        False
    """
    if not api_key:
        return False
    return api_key.startswith("anyt_agent_") and len(api_key) > 20


def get_api_key_setup_message(shell_name: str, config_path: str) -> str:
    """Get formatted setup message for API key configuration.

    Args:
        shell_name: Name of the detected shell
        config_path: Path to shell config file

    Returns:
        Formatted message with setup instructions
    """
    export_example = (
        "set -x ANYT_API_KEY=anyt_agent_..."
        if shell_name == "fish"
        else "export ANYT_API_KEY=anyt_agent_..."
    )

    message = f"""
[yellow]✗ ANYT_API_KEY environment variable not set[/yellow]

To use AnyTask CLI, you need an API key.

[bold cyan]How to get your API key:[/bold cyan]
  1. Visit [link]https://anyt.dev/home/settings/api-keys[/link]
  2. Click "Create API Key"
  3. Copy the generated key (starts with anyt_agent_...)

[bold cyan]Set the API key temporarily (this session only):[/bold cyan]
  {export_example}

[bold cyan]Or add to your shell profile for persistence:[/bold cyan]
  # For {shell_name} ({config_path})
  echo '{export_example}' >> {config_path}
  source {config_path}

Then run [bold]anyt init[/bold] again.
"""
    return message.strip()


def get_invalid_api_key_message(api_key: str) -> str:
    """Get error message for invalid API key format.

    Args:
        api_key: The invalid API key

    Returns:
        Formatted error message
    """
    message = f"""
[yellow]✗ Invalid API key format[/yellow]

The provided API key does not match the expected format.

[bold cyan]Expected format:[/bold cyan]
  - Must start with 'anyt_agent_'
  - Must be at least 20 characters long

[bold cyan]Your API key:[/bold cyan]
  {api_key[:20]}... (truncated)

Please verify your API key at [link]https://anyt.dev/home/settings/api-keys[/link]
"""
    return message.strip()
