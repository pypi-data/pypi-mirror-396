"""
djb CLI logging - Consistent progress output with verbosity control.

Provides a structured logging system for CLI commands with different log levels
and consistent formatting.
"""

from __future__ import annotations

import logging
import sys
from enum import IntEnum

# Custom log levels
NOTE_LEVEL = logging.INFO + 5


class Level(IntEnum):
    """Custom log levels with prefixes for CLI output."""

    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    NOTE = NOTE_LEVEL
    DEBUG = logging.DEBUG

    @classmethod
    def from_string(cls, level_str: str) -> int:
        """Convert string to log level."""
        level_map = {
            "error": cls.ERROR,
            "warning": cls.WARNING,
            "info": cls.INFO,
            "note": cls.NOTE,
            "debug": cls.DEBUG,
        }
        return level_map.get(level_str.lower(), cls.NOTE)


class CliFormatter(logging.Formatter):
    """Custom formatter that adds prefixes based on log level."""

    PREFIXES = {
        logging.ERROR: "✗ ",
        logging.WARNING: "⚠️  ",
        logging.INFO: "",
        NOTE_LEVEL: "",
        logging.DEBUG: "  ",
    }

    def format(self, record):
        prefix = self.PREFIXES.get(record.levelno, "")
        # Store original message
        original_msg = record.msg
        # Add prefix to message
        record.msg = f"{prefix}{original_msg}"
        # Format the record
        result = super().format(record)
        # Restore original message
        record.msg = original_msg
        return result


class FlushingStreamHandler(logging.StreamHandler):
    """Stream handler that flushes after each emit.

    This ensures output is visible immediately, which is important
    when running in environments like Heroku dynos where output
    might be buffered.
    """

    def emit(self, record):
        super().emit(record)
        self.flush()


class CliLogger:
    """
    CLI logger with custom methods for different types of output.
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(f"djb.cli.{name}")

    def error(self, msg: str):
        """Log an error message (✗ prefix)."""
        self.logger.error(msg)

    def warning(self, msg: str):
        """Log a warning message (⚠️ prefix)."""
        self.logger.warning(msg)

    def info(self, msg: str):
        """Log an info message (no prefix)."""
        self.logger.info(msg)

    def note(self, msg: str = ""):
        """Log a note (no prefix, NOTE level)."""
        self.logger.log(NOTE_LEVEL, msg)

    def debug(self, msg: str):
        """Log a debug message (indented)."""
        self.logger.debug(msg)

    def next(self, msg: str):
        """Log a next step message (adds '...' suffix)."""
        if not msg.endswith("..."):
            msg = f"{msg}..."
        self.logger.info(msg)

    def done(self, msg: str):
        """Log a completion message (✓ prefix)."""
        self.logger.info(f"✓ {msg}")

    def skip(self, msg: str):
        """Log a skip message (→ prefix)."""
        self.logger.info(f"⏭️  {msg}")


def setup_logging(level: str = "note"):
    """
    Set up logging for djb CLI commands.

    Args:
        level: Log level string (error, warning, info, note, debug)
    """
    log_level = Level.from_string(level)

    # Add NOTE level to logging module
    logging.addLevelName(NOTE_LEVEL, "NOTE")

    # Create handler with custom formatter
    # Use FlushingStreamHandler to ensure output is visible immediately
    # (important for Heroku dynos and other buffered environments)
    handler = FlushingStreamHandler(sys.stdout)
    handler.setFormatter(CliFormatter("%(message)s"))
    handler.setLevel(logging.DEBUG)  # Handler should process all levels

    # Configure root djb.cli logger
    cli_logger = logging.getLogger("djb.cli")
    cli_logger.setLevel(log_level)
    cli_logger.handlers.clear()
    cli_logger.addHandler(handler)
    cli_logger.propagate = False

    # Ensure child loggers inherit from parent
    # This is important for get_logger() to work properly


def get_logger(name: str) -> CliLogger:
    """Get a CliLogger instance for the given name."""
    return CliLogger(name)
