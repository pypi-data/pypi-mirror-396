"""Dependency management command."""

from __future__ import annotations

import click

from djb.cli.context import CliContext
from djb.cli.logging import get_logger
from djb.cli.utils import run_streaming

logger = get_logger(__name__)


def _get_cli_context(ctx: click.Context) -> CliContext:
    """Get the CliContext from click context, with type assertion."""
    assert isinstance(ctx.obj, CliContext), "Expected CliContext at ctx.obj"
    return ctx.obj


@click.command(name="dependencies")
@click.option(
    "--bump",
    is_flag=True,
    help="Upgrade to the latest available versions (uv lock --upgrade --latest for backend, bun update --latest for frontend).",
)
@click.pass_context
def dependencies(ctx: click.Context, bump: bool) -> None:
    """Refresh dependencies for frontend and/or backend.

    Updates lock files and installs dependencies:

    \b
    Backend (--backend):
      • Runs uv lock --upgrade to update lockfile
      • Runs uv sync to install dependencies
      • With --bump: uses --latest to get newest versions

    \b
    Frontend (--frontend):
      • Runs bun install to sync dependencies
      • With --bump: runs bun update --latest

    \b
    Examples:
      djb --backend dependencies                 # Refresh backend only
      djb --frontend dependencies                # Refresh frontend only
      djb --backend --frontend dependencies      # Refresh both
      djb --backend dependencies --bump          # Upgrade to latest versions
    """
    cli_ctx = _get_cli_context(ctx)
    scope_frontend = cli_ctx.scope_frontend
    scope_backend = cli_ctx.scope_backend

    if not scope_frontend and not scope_backend:
        raise click.ClickException(
            "Specify --frontend and/or --backend to choose which deps to refresh."
        )

    assert cli_ctx.config is not None
    project_dir = cli_ctx.config.project_dir
    assert project_dir is not None

    if scope_backend:
        bump_str = "yes" if bump else "no"
        logger.info(f"Refreshing Python deps with uv (bump={bump_str})...")
        lock_cmd = ["uv", "lock", "--upgrade"]
        if bump:
            lock_cmd.append("--latest")
        returncode, _, _ = run_streaming(lock_cmd, cwd=project_dir, label="uv lock")
        if returncode != 0:
            raise click.ClickException("uv lock failed")

        returncode, _, _ = run_streaming(["uv", "sync"], cwd=project_dir, label="uv sync")
        if returncode != 0:
            raise click.ClickException("uv sync failed")

        logger.done("Backend dependencies refreshed.")

    if scope_frontend:
        bump_str = "yes" if bump else "no"
        logger.info(f"Refreshing frontend deps with Bun (bump={bump_str})...")
        frontend_dir = project_dir / "frontend"
        # Reuse the existing Bun helper script to keep logic in one place
        cmd = ["bun", "run", "refresh-deps"]
        if bump:
            cmd.append("--bump")
        returncode, _, _ = run_streaming(cmd, cwd=frontend_dir, label="frontend refresh-deps")
        if returncode != 0:
            raise click.ClickException("frontend refresh-deps failed")

        logger.done("Frontend dependencies refreshed.")
