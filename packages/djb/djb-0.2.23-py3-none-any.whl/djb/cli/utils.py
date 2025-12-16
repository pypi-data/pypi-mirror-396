"""Utility functions for djb CLI."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import click

from djb.cli.logging import get_logger

logger = get_logger(__name__)


def run_cmd(
    cmd: list[str],
    cwd: Path | None = None,
    label: str | None = None,
    done_msg: str | None = None,
    fail_msg: str | None = None,
    halt_on_fail: bool = True,
    quiet: bool = False,
) -> subprocess.CompletedProcess:
    """Run a shell command with optional error handling.

    Args:
        cmd: Command and arguments to run
        cwd: Working directory
        label: Human-readable label (logged with logger.next)
        done_msg: Success message (logged with logger.done)
        fail_msg: Failure message (logged with logger.fail if halt_on_fail=False)
        halt_on_fail: Whether to raise ClickException on failure
        quiet: Suppress all logging output (except for halt_on_fail errors)

    Returns:
        CompletedProcess with stdout/stderr as text
    """
    if label and not quiet:
        logger.next(label)
    logger.debug(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        if halt_on_fail:
            logger.error(f"{label or 'Command'} failed with exit code {result.returncode}")
            if result.stderr:
                logger.debug(result.stderr)
            raise click.ClickException(f"{label or 'Command'} failed")
        elif fail_msg and not quiet:
            logger.fail(fail_msg)
            if result.stderr:
                logger.info(f"  {result.stderr.strip()}")
    if done_msg and result.returncode == 0 and not quiet:
        logger.done(done_msg)
    return result


def check_cmd(cmd: list[str], cwd: Path | None = None) -> bool:
    """Check if a command succeeds (returns True if exit code is 0).

    Useful for checking if something is installed or available.
    """
    result = subprocess.run(cmd, cwd=cwd, capture_output=True)
    return result.returncode == 0


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
