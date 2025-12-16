"""Utility functions for djb CLI."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import click


def run_command(
    cmd: list[str],
    cwd: Path | None = None,
    label: str | None = None,
    halt_on_fail: bool = True,
) -> int:
    """Run a shell command with optional error handling.

    Args:
        cmd: Command and arguments to run
        cwd: Working directory
        label: Human-readable label for the command
        halt_on_fail: Whether to raise ClickException on failure

    Returns:
        Command exit code
    """
    if label:
        click.echo(f"Running {label} ({' '.join(cmd)})")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0 and halt_on_fail:
        raise click.ClickException(
            f"{label or 'Command'} failed with exit code {result.returncode}"
        )
    return result.returncode


def flatten_dict(d: dict[str, Any], parent_key: str = "") -> dict[str, str]:
    """Flatten a nested dictionary into a flat dict with uppercase keys.

    Nested keys are joined with underscores. All values are converted to strings.

    Args:
        d: Dictionary to flatten
        parent_key: Prefix for all keys (used during recursion)

    Returns:
        Flat dictionary with uppercase keys

    Example:
        >>> flatten_dict({"db": {"host": "localhost", "port": 5432}})
        {"DB_HOST": "localhost", "DB_PORT": "5432"}
    """
    items: list[tuple[str, str]] = []
    for key, value in d.items():
        new_key = f"{parent_key}_{key}".upper() if parent_key else key.upper()
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key).items())
        else:
            items.append((new_key, str(value)))
    return dict(items)
