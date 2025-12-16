"""
djb local configuration - User-specific settings stored locally.

Stores user configuration in ~/.djb/config.yaml. This file is NOT committed
to the repository and contains user-specific settings like email.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def get_config_dir() -> Path:
    """Get the djb configuration directory (~/.djb)."""
    return Path.home() / ".djb"


def get_config_path() -> Path:
    """Get the djb configuration file path (~/.djb/config.yaml)."""
    return get_config_dir() / "config.yaml"


def load_config() -> dict[str, Any]:
    """Load the local configuration file.

    Returns an empty dict if the file doesn't exist.
    """
    config_path = get_config_path()
    if not config_path.exists():
        return {}

    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
        return data if data else {}


def save_config(config: dict[str, Any]) -> None:
    """Save the local configuration file."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    config_path = get_config_path()
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def get_name() -> str | None:
    """Get the configured user name."""
    config = load_config()
    return config.get("name")


def set_name(name: str) -> None:
    """Set the user name in local config."""
    config = load_config()
    config["name"] = name
    save_config(config)


def get_email() -> str | None:
    """Get the configured user email."""
    config = load_config()
    return config.get("email")


def set_email(email: str) -> None:
    """Set the user email in local config."""
    config = load_config()
    config["email"] = email
    save_config(config)
