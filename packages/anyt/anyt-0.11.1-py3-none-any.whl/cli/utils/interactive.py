# pyright: reportPrivateImportUsage=false
# pyright: reportArgumentType=false
"""Interactive prompt utilities using InquirerPy.

This module provides reusable helper functions for interactive prompts
using InquirerPy with arrow key navigation, replacing the old Rich-based
number selection prompts.
"""

from __future__ import annotations

import sys
from typing import Any, TypeVar, Sequence

import asyncio

import nest_asyncio
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.utils import get_style

# Allow nested event loops for InquirerPy prompts called from async contexts.
# This is needed because InquirerPy uses prompt_toolkit which calls
# loop.run_until_complete() internally, which fails if a loop is already running.
#
# On Windows with Python 3.8+, ProactorEventLoop is the default and is required
# for subprocess support. We do NOT change the event loop policy here to avoid
# breaking subprocess functionality in the worker.
#
# Python 3.12+ requires an explicit event loop before nest_asyncio.apply()
# We must explicitly pass the loop to nest_asyncio.apply() to avoid issues
# on Windows where asyncio.get_event_loop() may return None or fail.
#
# The "cannot create weak reference to 'NoneType' object" error on Windows
# occurs when nest_asyncio tries to patch a non-existent or invalid loop.
import warnings

_nest_loop = None
try:
    _nest_loop = asyncio.get_running_loop()
except RuntimeError:
    # No running loop - try to get or create one for nest_asyncio to patch
    try:
        # Suppress DeprecationWarning on Python 3.10+ when no loop exists
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            _nest_loop = asyncio.get_event_loop()
    except RuntimeError:
        pass  # Will create new loop below

# Ensure we have a valid loop - create one if needed
if _nest_loop is None:
    _nest_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_nest_loop)

# Apply nest_asyncio to allow nested event loops
# Pass the loop explicitly to avoid nest_asyncio calling get_event_loop() again
# which could fail on Windows with certain Python versions
nest_asyncio.apply(_nest_loop)

# Custom theme to match Rich's cyan/green styling
# Must be converted via get_style() for InquirerPy prompts
_ANYT_STYLE_DICT: dict[str, str] = {
    "questionmark": "fg:#00d7ff bold",  # cyan
    "question": "fg:#ffffff bold",
    "answer": "fg:#00ff00",  # green
    "pointer": "fg:#00d7ff bold",  # cyan
    "highlighted": "fg:#00d7ff bold",  # cyan
    "selected": "fg:#00ff00",  # green
    "separator": "fg:#808080",
    "instruction": "fg:#808080",
    "text": "fg:#ffffff",
    "disabled": "fg:#808080",
    "validator": "fg:#ff5555 bold",
    "marker": "fg:#00ff00",  # green checkbox marker
    "fuzzy_prompt": "fg:#00d7ff",  # cyan
    "fuzzy_info": "fg:#808080",
    "fuzzy_match": "fg:#00ff00 bold",  # green for fuzzy matches
}

# Convert to InquirerPy Style object
ANYT_STYLE = get_style(_ANYT_STYLE_DICT)


T = TypeVar("T")


def is_interactive() -> bool:
    """Check if the current environment supports interactive prompts.

    Returns:
        True if stdin is a TTY, False otherwise (e.g., in CI/automation).
    """
    return sys.stdin.isatty()


def select_one(
    choices: Sequence[Choice] | Sequence[str] | Sequence[dict[str, Any]],
    message: str = "Select one:",
    default: Any | None = None,
    instruction: str = "(Use arrow keys to navigate, Enter to select)",
) -> Any:
    """Single-select with arrow navigation.

    Args:
        choices: List of Choice objects, strings, or dicts
        message: Prompt message
        default: Default selected value
        instruction: Help text shown below prompt

    Returns:
        Selected value

    Raises:
        KeyboardInterrupt: If user presses Ctrl+C
    """
    return inquirer.select(
        message=message,
        choices=choices,
        default=default,
        instruction=instruction,
        style=ANYT_STYLE,
        qmark="?",
    ).execute()


def select_many(
    choices: Sequence[Choice] | Sequence[str],
    message: str = "Select options:",
    default: list[Any] | None = None,
    instruction: str = "(Space to toggle, Enter to confirm)",
    min_selection: int = 0,
    max_selection: int | None = None,
) -> list[Any]:
    """Multi-select checkbox with arrow navigation.

    Args:
        choices: List of Choice objects or strings
        message: Prompt message
        default: List of default selected values
        instruction: Help text shown below prompt
        min_selection: Minimum number of selections required
        max_selection: Maximum number of selections allowed (None for unlimited)

    Returns:
        List of selected values

    Raises:
        KeyboardInterrupt: If user presses Ctrl+C
    """
    return inquirer.checkbox(
        message=message,
        choices=choices,
        default=default,
        instruction=instruction,
        style=ANYT_STYLE,
        qmark="?",
        validate=lambda result: (
            len(result) >= min_selection
            and (max_selection is None or len(result) <= max_selection)
        ),
        invalid_message=f"Please select between {min_selection} and {max_selection or 'unlimited'} options",
    ).execute()


def confirm(
    message: str = "Confirm?",
    default: bool = True,
    instruction: str = "",
) -> bool:
    """Yes/No confirmation prompt.

    Args:
        message: Prompt message
        default: Default value (True = Yes, False = No)
        instruction: Help text shown below prompt

    Returns:
        True if confirmed, False otherwise

    Raises:
        KeyboardInterrupt: If user presses Ctrl+C
    """
    return inquirer.confirm(
        message=message,
        default=default,
        style=ANYT_STYLE,
        qmark="?",
    ).execute()


def text_input(
    message: str = "Enter value:",
    default: str = "",
    validate: Any | None = None,
    instruction: str = "",
) -> str:
    """Text input prompt.

    Args:
        message: Prompt message
        default: Default value
        validate: Optional validator function
        instruction: Help text shown below prompt

    Returns:
        User-entered text

    Raises:
        KeyboardInterrupt: If user presses Ctrl+C
    """
    return inquirer.text(
        message=message,
        default=default,
        validate=validate,
        style=ANYT_STYLE,
        qmark="?",
    ).execute()


def fuzzy_select(
    choices: Sequence[Choice] | Sequence[str],
    message: str = "Select one:",
    default: Any | None = None,
    instruction: str = "(Type to filter, arrow keys to navigate)",
) -> Any:
    """Single-select with fuzzy search filtering.

    Best for large lists where users may want to type to filter.

    Args:
        choices: List of Choice objects or strings
        message: Prompt message
        default: Default selected value
        instruction: Help text shown below prompt

    Returns:
        Selected value

    Raises:
        KeyboardInterrupt: If user presses Ctrl+C
    """
    return inquirer.fuzzy(
        message=message,
        choices=choices,
        default=default,
        instruction=instruction,
        style=ANYT_STYLE,
        qmark="?",
    ).execute()


def secret_input(
    message: str = "Enter secret:",
    validate: Any | None = None,
    instruction: str = "",
    transformer: Any | None = None,
) -> str:
    """Secret/password input prompt that masks input with asterisks.

    Args:
        message: Prompt message
        validate: Optional validator function
        instruction: Help text shown below prompt
        transformer: Optional function to transform displayed result

    Returns:
        User-entered secret text

    Raises:
        KeyboardInterrupt: If user presses Ctrl+C
    """
    return inquirer.secret(
        message=message,
        validate=validate,
        instruction=instruction,
        transformer=transformer or (lambda _: "[hidden]"),
        style=ANYT_STYLE,
        qmark="?",
    ).execute()
