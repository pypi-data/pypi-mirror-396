"""
djb project detection - Find the project root directory.

Provides utilities to locate the project root by searching for pyproject.toml
with a djb dependency. Searches current directory and parents.
"""

from __future__ import annotations

import os
import re
import tomllib
from pathlib import Path

from djb.core.exceptions import ProjectNotFound


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
    if (
        "project" in pyproject
        and "dependencies" in pyproject["project"]
        and isinstance(pyproject["project"]["dependencies"], list)
    ):
        for dep in pyproject["project"]["dependencies"]:
            if re.match(r"^\bdjb\b", dep):
                return True

    return False


def find_project_root(start_path: Path | None = None) -> Path:
    """Find the project root directory.

    Searches for a djb project by:
    1. Checking DJB_PROJECT_DIR environment variable
    2. Searching current directory and parents for pyproject.toml with djb dependency

    Args:
        start_path: Starting directory for search. Defaults to current working directory.

    Returns:
        Path to the project root directory.

    Raises:
        ProjectNotFound: If no djb project is found.
    """
    # Check environment variable first
    env_project_dir = os.getenv("DJB_PROJECT_DIR")
    if env_project_dir:
        path = Path(env_project_dir)
        if _is_djb_project(path):
            return path
        # Environment variable set but invalid - still raise ProjectNotFound

    # Search from start_path or cwd
    if start_path is None:
        start_path = Path.cwd()

    # Search current directory and parents
    for path in [start_path, *start_path.parents]:
        if _is_djb_project(path):
            return path

    raise ProjectNotFound()


def get_project_root_or_cwd() -> Path:
    """Get the project root, falling back to current working directory.

    This is a lenient version of find_project_root() that doesn't raise
    an exception if no project is found. Useful for commands that should
    work even outside a djb project.

    Returns:
        Path to the project root, or current working directory if not found.
    """
    try:
        return find_project_root()
    except ProjectNotFound:
        return Path.cwd()
