"""
djb CLI - Main command-line interface.

Provides subcommands for secrets management, deployment, and development.
"""

from __future__ import annotations

import os
from pathlib import Path

import click

from djb import __version__
from djb.cli.context import CliContext
from djb.cli.deploy import deploy
from djb.cli.dependencies import dependencies
from djb.cli.editable import editable_djb
from djb.cli.health import health
from djb.cli.init import init
from djb.cli.logging import Colors, get_logger, setup_logging
from djb.cli.publish import publish
from djb.cli.secrets import secrets
from djb.cli.superuser import sync_superuser
from djb.config import DjbConfig, get_config
from djb.types import Mode, Target

logger = get_logger(__name__)


def print_banner(config: DjbConfig) -> None:
    """Print the djb banner showing current mode and target.

    Colors:
    - development: green
    - staging: cyan/blue
    - production: red
    """
    mode_colors = {
        Mode.DEVELOPMENT: Colors.GREEN,
        Mode.STAGING: Colors.CYAN,
        Mode.PRODUCTION: Colors.RED,
    }

    mode_color = mode_colors.get(config.mode, "")
    mode_str = f"{mode_color}{config.mode}{Colors.RESET}"
    target_str = str(config.target)

    logger.info(f"[djb] mode: {mode_str} | target: {target_str}")


@click.group()
@click.version_option(version=__version__, prog_name="djb")
@click.option(
    "--log-level",
    type=click.Choice(["error", "warning", "info", "note", "debug"], case_sensitive=False),
    default="info",
    help="Set logging verbosity level",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed output (e.g., error messages on failure)",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress non-essential output",
)
@click.option(
    "--frontend",
    "scope_frontend",
    is_flag=True,
    help="Limit scope to frontend tasks only",
)
@click.option(
    "--backend",
    "scope_backend",
    is_flag=True,
    help="Limit scope to backend tasks only",
)
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Project root directory (default: auto-detect)",
)
@click.option(
    "--project-name",
    type=str,
    default=None,
    help="Project name (default: from pyproject.toml)",
)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["development", "staging", "production"], case_sensitive=False),
    default=None,
    help="Deployment mode (persists to config when set)",
)
@click.option(
    "--target",
    "-t",
    type=click.Choice(["heroku"], case_sensitive=False),
    default=None,
    help="Deployment target platform",
)
@click.pass_context
def djb_cli(
    ctx: click.Context,
    log_level: str,
    verbose: bool,
    quiet: bool,
    scope_frontend: bool,
    scope_backend: bool,
    project_dir: Path | None,
    project_name: str | None,
    mode: str | None,
    target: str | None,
):
    """djb - Django + Bun deployment platform"""
    # Set up logging first
    setup_logging(log_level)

    # Load configuration
    config = get_config(project_root=project_dir)

    # Apply CLI overrides
    cli_overrides = {}
    if project_dir is not None:
        cli_overrides["project_dir"] = project_dir
    if project_name is not None:
        cli_overrides["project_name"] = project_name
    if mode is not None:
        cli_overrides["mode"] = Mode(mode.lower())
    if target is not None:
        cli_overrides["target"] = Target(target.lower())

    if cli_overrides:
        config = config.with_overrides(**cli_overrides)

    # Persist mode if explicitly set via CLI
    if mode is not None:
        config.save_mode()

    # Store in context for subcommands
    ctx.ensure_object(CliContext)
    assert isinstance(ctx.obj, CliContext)
    ctx.obj.log_level = log_level
    ctx.obj.verbose = verbose
    ctx.obj.quiet = quiet
    ctx.obj.scope_frontend = scope_frontend
    ctx.obj.scope_backend = scope_backend
    ctx.obj.config = config

    # Print banner (unless nested invocation or quiet mode)
    if not os.environ.get("DJB_NESTED") and not quiet:
        print_banner(config)


# Add subcommands
djb_cli.add_command(init)
djb_cli.add_command(secrets)
djb_cli.add_command(deploy)
djb_cli.add_command(dependencies)
djb_cli.add_command(health)
djb_cli.add_command(publish)
djb_cli.add_command(editable_djb)
djb_cli.add_command(sync_superuser)


def main():
    """Entry point for djb CLI."""
    djb_cli()


if __name__ == "__main__":
    main()
