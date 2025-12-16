"""
djb CLI - Main command-line interface.

Provides subcommands for secrets management, deployment, and development.
"""

from __future__ import annotations

import click

from djb import __version__
from djb.cli.logging import setup_logging
from djb.cli.init import init
from djb.cli.secrets import secrets
from djb.cli.deploy import deploy
from djb.cli.publish import publish
from djb.cli.editable import editable_djb
from djb.cli.superuser import sync_superuser


@click.group()
@click.version_option(version=__version__, prog_name="djb")
@click.option(
    "--log-level",
    type=click.Choice(["error", "warning", "info", "note", "debug"], case_sensitive=False),
    default="info",
    help="Set logging verbosity level",
)
@click.pass_context
def djb_cli(ctx: click.Context, log_level: str):
    """djb - Django + Bun deployment platform"""
    # Set up logging
    setup_logging(log_level)
    # Store log level in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["log_level"] = log_level


# Add subcommands
djb_cli.add_command(init)
djb_cli.add_command(secrets)
djb_cli.add_command(deploy)
djb_cli.add_command(publish)
djb_cli.add_command(editable_djb)
djb_cli.add_command(sync_superuser)


def main():
    """Entry point for djb CLI."""
    djb_cli()


if __name__ == "__main__":
    main()
