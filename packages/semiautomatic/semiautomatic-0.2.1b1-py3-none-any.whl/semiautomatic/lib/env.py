"""
Environment utilities for semiautomatic.

Provides project root detection and automatic .env loading.

Library usage:
    from semiautomatic.lib.env import find_project_root, load_project_env

    # Find project root
    root = find_project_root()

    # Load .env (called automatically on import)
    load_project_env()

    # Get required env var with helpful error
    api_key = require_env("FAL_KEY")
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_MARKERS = (".git", "pyproject.toml", "uv.lock")


# ---------------------------------------------------------------------------
# Project Root Detection
# ---------------------------------------------------------------------------

def find_project_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find project root by looking for common markers.

    Walks up the directory tree from start_path looking for .git,
    pyproject.toml, or uv.lock.

    Args:
        start_path: Starting directory. Defaults to this file's location.

    Returns:
        Path to project root, or None if not found.
    """
    if start_path is None:
        current = Path(__file__).resolve().parent
    else:
        current = Path(start_path).resolve()

    while current != current.parent:
        if any((current / marker).exists() for marker in PROJECT_MARKERS):
            return current
        current = current.parent

    return None


# ---------------------------------------------------------------------------
# Environment Loading
# ---------------------------------------------------------------------------

def load_project_env(start_path: Optional[Path] = None) -> bool:
    """
    Find and load .env file from project root.

    Works from any subdirectory within the project.

    Args:
        start_path: Starting directory for project root search.

    Returns:
        True if .env was found and loaded, False otherwise.
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        # python-dotenv not installed, skip silently
        return False

    project_root = find_project_root(start_path)

    if project_root is None:
        return False

    env_path = project_root / ".env"

    if not env_path.exists():
        return False

    load_dotenv(dotenv_path=env_path)
    return True


def require_env(name: str, description: Optional[str] = None) -> str:
    """
    Get a required environment variable.

    Args:
        name: Environment variable name.
        description: Optional description for error message.

    Returns:
        The environment variable value.

    Raises:
        EnvironmentError: If the variable is not set.
    """
    value = os.environ.get(name)

    if not value:
        msg = f"{name} environment variable not set."
        if description:
            msg += f" {description}"
        else:
            msg += f" Add {name}=... to your .env file."
        raise EnvironmentError(msg)

    return value


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get an optional environment variable.

    Args:
        name: Environment variable name.
        default: Default value if not set.

    Returns:
        The environment variable value or default.
    """
    return os.environ.get(name, default)


# ---------------------------------------------------------------------------
# Auto-load on import
# ---------------------------------------------------------------------------

# Load .env automatically when this module is imported
load_project_env()
