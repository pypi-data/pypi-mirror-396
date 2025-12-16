"""
djb - Django + Bun deployment platform

A simplified, self-contained deployment platform for Django applications.
This is the beachresort25-integrated version of djb.
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
