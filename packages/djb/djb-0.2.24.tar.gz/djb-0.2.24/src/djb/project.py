"""
djb project detection - Find the project root directory.

Provides utilities to locate the project root by searching for pyproject.toml
with a djb dependency. Searches current directory and parents.
"""

from __future__ import annotations

import os
import re
import tomllib
from collections.abc import Callable
from pathlib import Path

from djb.core.exceptions import ProjectNotFound


def find_pyproject_root(
    start_path: Path | None = None,
    *,
    predicate: Callable[[Path], bool] | None = None,
) -> Path:
    """Find the nearest directory containing pyproject.toml that matches predicate.

    Walks up from start_path (or cwd) looking for pyproject.toml files.
    If a predicate is provided, the directory must also satisfy the predicate.

    Args:
        start_path: Starting directory for search. Defaults to current working directory.
        predicate: Optional function to test each candidate directory.
                   If provided, directory must satisfy predicate(path) == True.
                   If None, just checks for pyproject.toml existence.

    Returns:
        Path to the directory containing pyproject.toml (that matches predicate).

    Raises:
        FileNotFoundError: If no matching pyproject.toml is found.
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    while current != current.parent:
        if (current / "pyproject.toml").exists():
            if predicate is None or predicate(current):
                return current
        current = current.parent

    raise FileNotFoundError(f"Could not find pyproject.toml starting from {start_path}")


def _is_djb_project(path: Path) -> bool:
    """Check if a directory is a djb project (has pyproject.toml with djb dependency)."""
    pyproject_path = path / "pyproject.toml"

    if not pyproject_path.is_file():
        return False

    try:
        with open(pyproject_path, "rb") as f:
            pyproject = tomllib.load(f)
    except tomllib.TOMLDecodeError:
        return False

    # Check for djb in dependencies
    # Match "djb" followed by version specifier, extras bracket, whitespace, or end
    # Excludes packages like "djb-tools" or "djb_something"
    if (
        "project" in pyproject
        and "dependencies" in pyproject["project"]
        and isinstance(pyproject["project"]["dependencies"], list)
    ):
        for dep in pyproject["project"]["dependencies"]:
            if re.match(r"^djb(?:[<>=!~\[\s]|$)", dep):
                return True

    return False


def find_project_root(
    start_path: Path | None = None,
    *,
    fallback_to_cwd: bool = False,
) -> Path:
    """Find the project root directory.

    Searches for a djb project by:
    1. Checking DJB_PROJECT_DIR environment variable
    2. Searching current directory and parents for pyproject.toml with djb dependency

    Args:
        start_path: Starting directory for search. Defaults to current working directory.
        fallback_to_cwd: If True, return cwd when no project is found instead of raising.

    Returns:
        Path to the project root directory.

    Raises:
        ProjectNotFound: If no djb project is found and fallback_to_cwd is False.
    """
    # Check environment variable first
    env_project_dir = os.getenv("DJB_PROJECT_DIR")
    if env_project_dir:
        path = Path(env_project_dir)
        if _is_djb_project(path):
            return path
        # Environment variable set but invalid - still raise ProjectNotFound

    # Reuse find_pyproject_root with djb-specific predicate
    try:
        return find_pyproject_root(start_path, predicate=_is_djb_project)
    except FileNotFoundError:
        if fallback_to_cwd:
            return Path.cwd()
        raise ProjectNotFound()
