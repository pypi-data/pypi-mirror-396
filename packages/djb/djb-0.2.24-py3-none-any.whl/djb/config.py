"""
djb configuration - Unified configuration system for djb CLI.

Configuration is loaded with the following priority (highest to lowest):
1. CLI flags (applied via with_overrides())
2. Environment variables (DJB_ prefix)
3. Config file (.djb/config.yaml)
4. Default values

The config file is stored in .djb/config.yaml within the project root.
This file is NOT committed to the repository and contains user-specific
settings like name, email, and persisted mode/target preferences.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from djb.project import find_project_root
from djb.types import Mode, Target

__all__ = [
    # Main API
    "DjbConfig",
    "get_config",
    # Config file helpers
    "get_config_dir",
    "get_config_path",
    "load_config_file",
    "save_config_file",
    "get_project_name_from_pyproject",
    # Simple get/set helpers for common config values
    "get_name",
    "set_name",
    "get_email",
    "set_email",
    "get_project_name",
    "set_project_name",
]


def get_config_dir(project_root: Path | None = None) -> Path:
    """Get the djb configuration directory (.djb/ in project root).

    Args:
        project_root: Project root path. Defaults to auto-detected project root.

    Returns:
        Path to .djb/ directory in the project.
    """
    if project_root is None:
        project_root = find_project_root(fallback_to_cwd=True)
    return project_root / ".djb"


def get_config_path(project_root: Path | None = None) -> Path:
    """Get the djb configuration file path (.djb/config.yaml).

    Args:
        project_root: Project root path. Defaults to auto-detected project root.

    Returns:
        Path to .djb/config.yaml in the project.
    """
    return get_config_dir(project_root) / "config.yaml"


def load_config_file(project_root: Path | None = None) -> dict[str, Any]:
    """Load the local configuration file.

    Args:
        project_root: Project root path. Defaults to auto-detected project root.

    Returns:
        Configuration dict, or empty dict if the file doesn't exist.
    """
    config_path = get_config_path(project_root)
    if not config_path.exists():
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data if data else {}


def save_config_file(config: dict[str, Any], project_root: Path | None = None) -> None:
    """Save the local configuration file.

    Args:
        config: Configuration dict to save.
        project_root: Project root path. Defaults to auto-detected project root.
    """
    config_dir = get_config_dir(project_root)
    config_dir.mkdir(parents=True, exist_ok=True)

    config_path = get_config_path(project_root)
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def get_project_name_from_pyproject(project_root: Path | None = None) -> str | None:
    """Read the project name from pyproject.toml.

    Args:
        project_root: Project root path. Defaults to auto-detected project root.

    Returns:
        Project name from pyproject.toml, or None if not found.
    """
    if project_root is None:
        project_root = find_project_root(fallback_to_cwd=True)

    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        return None

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data.get("project", {}).get("name")
    except (tomllib.TOMLDecodeError, OSError):
        return None


def _get_env_value(key: str) -> str | None:
    """Get an environment variable with DJB_ prefix."""
    return os.getenv(f"DJB_{key.upper()}")


@dataclass
class DjbConfig:
    """Unified configuration for djb CLI.

    Loads configuration from multiple sources with priority:
    1. CLI flags (via with_overrides())
    2. Environment variables (DJB_ prefix)
    3. Config file (.djb/config.yaml)
    4. Defaults (including pyproject.toml for project_name)
    """

    # The four globals
    project_dir: Path | None = None
    project_name: str | None = None
    mode: Mode = Mode.DEVELOPMENT
    target: Target = Target.HEROKU

    # User identity (existing)
    name: str | None = None
    email: str | None = None

    # Internal: tracks which fields were explicitly set via CLI
    _cli_overrides: dict[str, Any] = field(default_factory=dict, repr=False)

    def with_overrides(self, **kwargs: Any) -> "DjbConfig":
        """Create a new config with CLI overrides applied.

        Args:
            **kwargs: Override values from CLI flags.

        Returns:
            New DjbConfig with overrides applied.
        """
        # Start with current values
        new_values = {
            "project_dir": self.project_dir,
            "project_name": self.project_name,
            "mode": self.mode,
            "target": self.target,
            "name": self.name,
            "email": self.email,
        }
        # Apply overrides (only non-None values)
        cli_overrides = {}
        for key, value in kwargs.items():
            if value is not None:
                new_values[key] = value
                cli_overrides[key] = value

        new_config = DjbConfig(**new_values)
        new_config._cli_overrides = cli_overrides
        return new_config

    def save(self, project_root: Path | None = None) -> None:
        """Save current configuration to .djb/config.yaml.

        Only saves fields that should be persisted (not project_dir).

        Args:
            project_root: Project root path. Defaults to self.project_dir.
        """
        if project_root is None:
            project_root = self.project_dir

        # Load existing config to preserve unknown fields
        existing = load_config_file(project_root)

        # Update with current values (only persistable fields)
        existing["name"] = self.name
        existing["email"] = self.email
        existing["project_name"] = self.project_name
        existing["mode"] = str(self.mode)
        existing["target"] = str(self.target)

        # Remove None values
        existing = {k: v for k, v in existing.items() if v is not None}

        save_config_file(existing, project_root)

    def save_mode(self, project_root: Path | None = None) -> None:
        """Save only the mode to config file.

        Used when --mode is explicitly passed to persist it.

        Args:
            project_root: Project root path. Defaults to self.project_dir.
        """
        if project_root is None:
            project_root = self.project_dir

        existing = load_config_file(project_root)
        existing["mode"] = str(self.mode)
        save_config_file(existing, project_root)


def get_config(project_root: Path | None = None) -> DjbConfig:
    """Get the djb configuration.

    This is the main entry point for loading configuration.
    Loads from (highest to lowest priority):
    1. Environment variables (DJB_ prefix)
    2. Config file (.djb/config.yaml)
    3. Default values

    Args:
        project_root: Project root path. Defaults to auto-detected.

    Returns:
        DjbConfig instance with all sources merged.
    """
    # Start with defaults
    config_values: dict[str, Any] = {}

    # Load from config file (lowest priority after defaults)
    file_config = load_config_file(project_root)

    # project_dir: env > file > default (cwd)
    if env_val := _get_env_value("PROJECT_DIR"):
        config_values["project_dir"] = Path(env_val)
    elif "project_dir" in file_config:
        config_values["project_dir"] = Path(file_config["project_dir"])
    else:
        config_values["project_dir"] = project_root or find_project_root(fallback_to_cwd=True)

    # project_name: env > file > pyproject.toml
    if env_val := _get_env_value("PROJECT_NAME"):
        config_values["project_name"] = env_val
    elif "project_name" in file_config:
        config_values["project_name"] = file_config["project_name"]
    else:
        config_values["project_name"] = get_project_name_from_pyproject(
            config_values.get("project_dir")
        )

    # mode: env > file > default
    config_values["mode"] = (
        Mode.parse(_get_env_value("MODE"))
        or Mode.parse(file_config.get("mode"))
        or Mode.DEVELOPMENT
    )

    # target: env > file > default
    config_values["target"] = (
        Target.parse(_get_env_value("TARGET"))
        or Target.parse(file_config.get("target"))
        or Target.HEROKU
    )

    # name: env > file
    if env_val := _get_env_value("NAME"):
        config_values["name"] = env_val
    else:
        config_values["name"] = file_config.get("name")

    # email: env > file
    if env_val := _get_env_value("EMAIL"):
        config_values["email"] = env_val
    else:
        config_values["email"] = file_config.get("email")

    return DjbConfig(**config_values)


# ============================================================================
# Simple get/set helpers for common config values
# ============================================================================


def get_name(project_root: Path | None = None) -> str | None:
    """Get the configured user name.

    Args:
        project_root: Project root path. Defaults to auto-detected project root.

    Returns:
        User name, or None if not configured.
    """
    config = load_config_file(project_root)
    return config.get("name")


def set_name(name: str, project_root: Path | None = None) -> None:
    """Set the user name in local config.

    Args:
        name: User name to set.
        project_root: Project root path. Defaults to auto-detected project root.
    """
    config = load_config_file(project_root)
    config["name"] = name
    save_config_file(config, project_root)


def get_email(project_root: Path | None = None) -> str | None:
    """Get the configured user email.

    Args:
        project_root: Project root path. Defaults to auto-detected project root.

    Returns:
        User email, or None if not configured.
    """
    config = load_config_file(project_root)
    return config.get("email")


def set_email(email: str, project_root: Path | None = None) -> None:
    """Set the user email in local config.

    Args:
        email: User email to set.
        project_root: Project root path. Defaults to auto-detected project root.
    """
    config = load_config_file(project_root)
    config["email"] = email
    save_config_file(config, project_root)


def get_project_name(project_root: Path | None = None) -> str | None:
    """Get the configured project name.

    Checks config file first, then falls back to pyproject.toml.

    Args:
        project_root: Project root path. Defaults to auto-detected project root.

    Returns:
        Project name, or None if not configured.
    """
    config = load_config_file(project_root)
    if name := config.get("project_name"):
        return name
    return get_project_name_from_pyproject(project_root)


def set_project_name(name: str, project_root: Path | None = None) -> None:
    """Set the project name in local config.

    Args:
        name: Project name to set.
        project_root: Project root path. Defaults to auto-detected project root.
    """
    config = load_config_file(project_root)
    config["project_name"] = name
    save_config_file(config, project_root)
