"""
djb app name detection - Auto-detect app name from Django settings.

Provides functions to read DJB_APP_NAME from Django settings without
requiring a full Django setup.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

logger = logging.getLogger(__name__)


def get_app_name(repo_root: Path | None = None) -> str | None:
    """Get the DJB_APP_NAME from Django settings.

    Attempts to read DJB_APP_NAME using multiple strategies:
    1. From Django settings if Django is configured
    2. By parsing the settings file directly

    Args:
        repo_root: Project root directory (default: cwd)

    Returns:
        The app name if found, None otherwise
    """
    if repo_root is None:
        repo_root = Path.cwd()

    # Strategy 1: Try to get from Django settings if available
    app_name = _get_from_django_settings()
    if app_name:
        return app_name

    # Strategy 2: Parse settings file directly
    return _parse_settings_file(repo_root)


def _get_from_django_settings() -> str | None:
    """Try to get DJB_APP_NAME from Django settings.

    Only works if Django is properly configured.
    """
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
    if not settings_module:
        return None

    try:
        from django.conf import settings

        return getattr(settings, "DJB_APP_NAME", None)
    except ImportError:
        logger.debug("Django not installed, cannot read settings")
        return None
    except Exception as e:
        # Django may raise various errors if not properly configured
        logger.debug("Failed to read Django settings: %s", e)
        return None


def _parse_settings_file(repo_root: Path) -> str | None:
    """Parse DJB_APP_NAME directly from settings.py file.

    This works without requiring Django to be configured.
    """
    # Try to find the settings module from the environment or detect it
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "")

    if settings_module:
        # Convert module path to file path (e.g., "myproject.settings" -> "myproject/settings.py")
        settings_path = repo_root / settings_module.replace(".", "/")
        if not settings_path.suffix:
            settings_path = settings_path.with_suffix(".py")
    else:
        # Try to detect settings file from common patterns
        settings_path = _find_settings_file(repo_root)

    if not settings_path or not settings_path.exists():
        return None

    try:
        content = settings_path.read_text()
    except OSError as e:
        logger.debug("Failed to read settings file %s: %s", settings_path, e)
        return None

    # Look for DJB_APP_NAME = "value" or DJB_APP_NAME = 'value'
    match = re.search(r'DJB_APP_NAME\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)

    return None


def _find_settings_file(repo_root: Path) -> Path | None:
    """Try to find the Django settings file in common locations."""
    # Check for pyproject.toml to find the package name
    pyproject_path = repo_root / "pyproject.toml"
    if pyproject_path.exists():
        try:
            import tomllib

            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
            project_name = data.get("project", {}).get("name")
            if project_name:
                # Try the project name as the settings module
                settings_path = repo_root / project_name / "settings.py"
                if settings_path.exists():
                    return settings_path
        except (OSError, tomllib.TOMLDecodeError) as e:
            logger.debug("Failed to parse pyproject.toml: %s", e)

    # Common fallback patterns
    for pattern in ["*/settings.py", "settings.py", "config/settings.py"]:
        matches = list(repo_root.glob(pattern))
        # Filter out venv directories
        matches = [m for m in matches if ".venv" not in str(m) and "venv" not in str(m)]
        if matches:
            return matches[0]

    return None
