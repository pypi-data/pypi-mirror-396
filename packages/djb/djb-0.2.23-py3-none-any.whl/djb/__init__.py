"""
djb - Django + Bun deployment platform

A simplified, self-contained deployment platform for Django applications.
"""

from importlib.metadata import version

__version__ = version("djb")

# Export logging utilities for use by other projects
from djb.cli.logging import (
    setup_logging,
    get_logger,
    Level,
    CliLogger,
)

__all__ = [
    "setup_logging",
    "get_logger",
    "Level",
    "CliLogger",
]
