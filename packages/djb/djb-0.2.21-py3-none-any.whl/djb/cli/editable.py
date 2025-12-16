"""
djb editable-djb CLI - Install/uninstall djb in editable mode.

This command uses `uv add --editable` which modifies pyproject.toml to add
a [tool.uv.sources] section. This ensures that `uv sync` and `uv run` respect
the editable installation and don't overwrite it with the PyPI version.

IMPORTANT: Do NOT use `uv pip install -e ./djb` as this bypasses pyproject.toml
and will be overwritten by `uv sync` or `uv run`.
"""

from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path

import click


def get_djb_version_specifier(repo_root: Path) -> str | None:
    """Get the djb version specifier from pyproject.toml dependencies.

    Returns the version specifier (e.g., ">=0.2.6") or None if not found.
    """
    pyproject_path = repo_root / "pyproject.toml"
    if not pyproject_path.exists():
        return None

    content = pyproject_path.read_text()

    # Match patterns like "djb>=0.2.6" or 'djb>=0.2.6'
    match = re.search(r'["\']djb(>=[\d.]+)["\']', content)
    if match:
        return match.group(1)

    return None


def find_djb_dir(repo_root: Path | None = None) -> Path | None:
    """Find the djb directory relative to repo_root or cwd."""
    if repo_root is None:
        repo_root = Path.cwd()

    # Check if djb/ exists in the directory
    if (repo_root / "djb" / "pyproject.toml").exists():
        return repo_root / "djb"

    # Check if we're inside the djb directory
    if (repo_root / "pyproject.toml").exists():
        content = (repo_root / "pyproject.toml").read_text()
        if 'name = "djb"' in content:
            return repo_root

    return None


def _get_djb_source_config(pyproject_path: Path) -> dict | None:
    """Get the djb source configuration from pyproject.toml.

    Reads [tool.uv.sources.djb] from pyproject.toml if present.

    Returns:
        The djb source dict if configured, None otherwise.
    """
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError):
        return None

    tool = data.get("tool", {})
    uv = tool.get("uv", {})
    sources = uv.get("sources", {})
    return sources.get("djb")


def is_djb_editable(repo_root: Path | None = None) -> bool:
    """Check if djb is currently installed in editable mode via pyproject.toml.

    This checks for a [tool.uv.sources] entry for djb with editable=true.
    """
    if repo_root is None:
        repo_root = Path.cwd()
    pyproject_path = repo_root / "pyproject.toml"
    if not pyproject_path.exists():
        return False

    djb_config = _get_djb_source_config(pyproject_path)
    if djb_config is None:
        return False
    return djb_config.get("editable", False)


def get_djb_source_path(repo_root: Path | None = None) -> str | None:
    """Get the path to the editable djb source if installed in editable mode."""
    if repo_root is None:
        repo_root = Path.cwd()
    pyproject_path = repo_root / "pyproject.toml"
    if not pyproject_path.exists():
        return None

    djb_config = _get_djb_source_config(pyproject_path)
    if djb_config is None or not djb_config.get("editable"):
        return None
    return djb_config.get("path")


def get_installed_djb_version(repo_root: Path | None = None) -> str | None:
    """Get the currently installed djb version."""
    if repo_root is None:
        repo_root = Path.cwd()

    result = subprocess.run(
        ["uv", "pip", "show", "djb"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None

    for line in result.stdout.splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return None


def uninstall_editable_djb(repo_root: Path | None = None, quiet: bool = False) -> bool:
    """Uninstall editable djb and reinstall from PyPI.

    Args:
        repo_root: Project root directory (default: cwd)
        quiet: If True, suppress output messages

    Returns:
        True on success, False on failure
    """
    if repo_root is None:
        repo_root = Path.cwd()

    # Save the version specifier BEFORE removing (uv remove will delete it)
    version_specifier = get_djb_version_specifier(repo_root)

    if not quiet:
        click.echo("Removing editable djb...")

    result = subprocess.run(
        ["uv", "remove", "djb"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if not quiet:
            click.secho(f"Failed to remove djb: {result.stderr}", fg="red")
        return False

    if not quiet:
        click.echo("Re-adding djb from PyPI...")

    # Re-add with the original version specifier to preserve it
    # Use --refresh to bypass uv's resolver cache and get the latest from PyPI
    djb_spec = f"djb{version_specifier}" if version_specifier else "djb"
    result = subprocess.run(
        ["uv", "add", "--refresh", djb_spec],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if not quiet:
            click.secho(f"Failed to add djb from PyPI: {result.stderr}", fg="red")
        return False

    if not quiet:
        version = get_installed_djb_version(repo_root)
        version_str = f" (v{version})" if version else ""
        click.secho(f"✓ Switched to PyPI version of djb{version_str}", fg="green")
    return True


def install_editable_djb(repo_root: Path | None = None, quiet: bool = False) -> bool:
    """Install djb in editable mode from local directory.

    Uses `uv add --editable` which modifies pyproject.toml to track the
    editable source, ensuring it persists across `uv sync` operations.

    Args:
        repo_root: Project root directory (default: cwd)
        quiet: If True, suppress output messages

    Returns:
        True on success, False on failure
    """
    if repo_root is None:
        repo_root = Path.cwd()

    djb_dir = find_djb_dir(repo_root)
    if not djb_dir:
        if not quiet:
            click.secho(
                "Could not find djb directory. Run from a project containing djb/ "
                "or from inside the djb directory.",
                fg="red",
            )
        return False

    if not quiet:
        click.echo(f"Installing djb in editable mode from {djb_dir}...")

    result = subprocess.run(
        ["uv", "add", "--editable", str(djb_dir)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if not quiet:
            click.secho(f"Failed to add editable djb: {result.stderr}", fg="red")
        return False

    if not quiet:
        version = get_installed_djb_version(repo_root)
        version_str = f" (v{version})" if version else ""
        click.secho(f"✓ djb installed in editable mode{version_str}", fg="green")
        click.echo(f"  Source: {djb_dir}")
        click.echo("")
        click.echo("Note: pyproject.toml now has [tool.uv.sources] for djb.")
        click.echo("This ensures editable mode persists across `uv sync`.")
    return True


def show_status(repo_root: Path | None = None) -> None:
    """Show the current djb installation status."""
    if repo_root is None:
        repo_root = Path.cwd()

    version = get_installed_djb_version(repo_root)
    is_editable = is_djb_editable(repo_root)
    source_path = get_djb_source_path(repo_root)

    click.echo("djb installation status:")
    click.echo("")

    if version:
        click.echo(f"  Version: {version}")
    else:
        click.secho("  Not installed", fg="yellow")
        return

    if is_editable:
        click.secho("  Mode: editable (local development)", fg="green")
        if source_path:
            click.echo(f"  Source: {source_path}")
    else:
        click.echo("  Mode: PyPI (production)")

    click.echo("")

    if is_editable:
        click.echo("To switch to PyPI version:")
        click.echo("  djb editable-djb --uninstall")
    else:
        djb_dir = find_djb_dir(repo_root)
        if djb_dir:
            click.echo("To switch to editable mode:")
            click.echo("  djb editable-djb")
        else:
            click.echo("No local djb directory found for editable installation.")


@click.command("editable-djb")
@click.option(
    "--uninstall",
    is_flag=True,
    help="Uninstall editable djb and use PyPI version instead.",
)
@click.option(
    "--status",
    is_flag=True,
    help="Show current djb installation status.",
)
def editable_djb(uninstall: bool, status: bool):
    """Install or uninstall djb in editable mode.

    Uses `uv add --editable` which modifies pyproject.toml to add a
    [tool.uv.sources] section. This ensures that `uv sync` and `uv run`
    respect the editable installation.

    IMPORTANT: Never use `uv pip install -e ./djb` directly - it will be
    overwritten by `uv sync`. Always use this command instead.

    \b
    Examples:
        djb editable-djb              # Install editable djb
        djb editable-djb --status     # Check current status
        djb editable-djb --uninstall  # Switch back to PyPI version
    """
    if status:
        show_status()
        return

    if uninstall:
        if not is_djb_editable():
            click.echo("djb is not currently in editable mode.")
            return
        if not uninstall_editable_djb():
            raise click.ClickException("Failed to uninstall editable djb")
    else:
        if is_djb_editable():
            source_path = get_djb_source_path()
            click.echo(f"djb is already installed in editable mode from {source_path}")
            click.echo("Use --uninstall to switch back to PyPI version.")
            return
        if not install_editable_djb():
            raise click.ClickException("Failed to install editable djb")
