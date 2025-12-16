"""
djb publish CLI - Version management and PyPI publishing.

Provides commands for bumping versions and publishing to PyPI.
"""

from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

import click
import requests

from djb.cli.editable_stash import (
    bust_uv_cache,
    capture_editable_state,
    regenerate_uv_lock,
    remove_editable_config,
    restore_editable_with_current_version,
)


def find_djb_root() -> Path:
    """Find the djb package root directory.

    Looks for pyproject.toml with name = "djb" in current directory
    or in a djb/ subdirectory.

    Uses resolve() to canonicalize paths, handling symlinks consistently.
    """
    cwd = Path.cwd().resolve()

    # Check if we're in the djb directory itself
    pyproject = cwd / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        if 'name = "djb"' in content:
            return cwd

    # Check if there's a djb subdirectory
    djb_dir = cwd / "djb"
    pyproject = djb_dir / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        if 'name = "djb"' in content:
            return djb_dir

    raise click.ClickException(
        "Could not find djb package. Run from djb directory or a parent containing djb/"
    )


def get_version(djb_root: Path) -> str:
    """Read current version from pyproject.toml."""
    pyproject = djb_root / "pyproject.toml"
    content = pyproject.read_text()

    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        raise click.ClickException("Could not find version in pyproject.toml")

    return match.group(1)


def set_version(djb_root: Path, version: str) -> None:
    """Write new version to pyproject.toml."""
    pyproject = djb_root / "pyproject.toml"
    content = pyproject.read_text()

    new_content = re.sub(
        r'^(version\s*=\s*)"[^"]+"',
        f'\\1"{version}"',
        content,
        flags=re.MULTILINE,
    )

    pyproject.write_text(new_content)


def bump_version(version: str, part: str) -> str:
    """Bump the specified part of a semver version string.

    Args:
        version: Current version (e.g., "0.2.0")
        part: Which part to bump ("major", "minor", or "patch")

    Returns:
        New version string
    """
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version)
    if not match:
        raise click.ClickException(f"Invalid version format: {version} (expected X.Y.Z)")

    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))

    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        raise click.ClickException(f"Unknown version part: {part}")

    return f"{major}.{minor}.{patch}"


def wait_for_pypi(version: str, timeout: int = 300, interval: int = 10) -> bool:
    """Wait for a specific djb version to be available on PyPI.

    Args:
        version: The version to wait for (e.g., "0.2.10")
        timeout: Maximum time to wait in seconds (default: 5 minutes)
        interval: Time between checks in seconds (default: 10 seconds)

    Returns:
        True if version is available, False if timeout reached
    """
    url = "https://pypi.org/pypi/djb/json"
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if version in data.get("releases", {}):
                    return True
        except requests.RequestException:
            pass  # Network error, will retry

        time.sleep(interval)

    return False


def find_parent_project(djb_root: Path) -> Path | None:
    """Find parent project that depends on djb.

    Looks for a pyproject.toml in the parent directory that has djb as a dependency.
    """
    parent = djb_root.parent
    pyproject = parent / "pyproject.toml"

    if pyproject.exists():
        content = pyproject.read_text()
        if '"djb>=' in content or "'djb>=" in content:
            return parent

    return None


def update_parent_dependency(parent_root: Path, new_version: str) -> bool:
    """Update the djb dependency version in a parent project.

    Returns True if updated, False if no change needed.
    """
    pyproject = parent_root / "pyproject.toml"
    content = pyproject.read_text()

    # Match patterns like "djb>=0.2.3" or 'djb>=0.2.3'
    new_content = re.sub(
        r'(["\'])djb>=[\d.]+(["\'])',
        f'\\1djb>={new_version}\\2',
        content,
    )

    if new_content != content:
        pyproject.write_text(new_content)
        return True
    return False


class PublishRunner:
    """Handles publish workflow with dry-run support.

    Keeps dry-run and real execution in sync by using a single control flow.
    """

    def __init__(self, dry_run: bool):
        self.dry_run = dry_run
        self.step = 0

    def _step(self, description: str | None) -> None:
        """Print step description for dry-run or progress message.

        If description is None, the step is silent (used for sub-operations
        that are part of a larger logical step).
        """
        if description is None:
            return
        self.step += 1
        if self.dry_run:
            click.echo(f"  {self.step}. {description}")
        else:
            click.echo(f"{description}...")

    def run_git(self, args: list[str], cwd: Path, description: str | None = None) -> None:
        """Run a git command, or print what would be done in dry-run mode.

        Pass description=None to run silently (as part of another step).
        """
        self._step(description)
        if not self.dry_run:
            subprocess.run(["git"] + args, cwd=cwd, check=True)

    def run_shell(self, args: list[str], cwd: Path, description: str | None = None) -> bool:
        """Run a shell command, or print what would be done in dry-run mode.

        Pass description=None to run silently (as part of another step).
        Returns True on success, False on failure.
        """
        self._step(description)
        if not self.dry_run:
            result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
            return result.returncode == 0
        return True

    def action(self, description: str | None, func: callable) -> None:
        """Execute an action, or print what would be done in dry-run mode.

        Pass description=None to run silently (as part of another step).
        """
        self._step(description)
        if not self.dry_run:
            func()


@click.command()
@click.option(
    "--major",
    "part",
    flag_value="major",
    help="Bump major version (X.0.0)",
)
@click.option(
    "--minor",
    "part",
    flag_value="minor",
    help="Bump minor version (0.X.0)",
)
@click.option(
    "--patch",
    "part",
    flag_value="patch",
    default=True,
    help="Bump patch version (0.0.X) [default]",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
def publish(part: str, dry_run: bool):
    """Bump version and publish djb to PyPI.

    Reads the current version from pyproject.toml, bumps it according
    to the specified part (--major, --minor, or --patch), commits the
    change, creates a git tag, and pushes to trigger the publish workflow.

    If run from a parent project that depends on djb (e.g., beachresort25),
    also updates the parent's dependency version and commits that change.

    If the parent project has djb in editable mode, this command will
    temporarily remove the editable configuration for the commit, then
    restore it afterward so local development can continue.

    Can be run from the djb directory or from a parent directory
    containing a djb/ subdirectory.

    \b
    Examples:
        djb publish              # Bump patch: 0.2.0 -> 0.2.1
        djb publish --minor      # Bump minor: 0.2.0 -> 0.3.0
        djb publish --major      # Bump major: 0.2.0 -> 1.0.0
        djb publish --dry-run    # Show what would happen
    """
    djb_root = find_djb_root()
    click.echo(f"Found djb at: {djb_root}")

    # Check for parent project
    parent_root = find_parent_project(djb_root)
    if parent_root:
        click.echo(f"Found parent project at: {parent_root}")

    # Capture editable state of parent (if exists)
    parent_state = capture_editable_state(parent_root) if parent_root else None
    parent_editable = parent_state and parent_state.was_editable
    if parent_editable:
        click.echo("Parent project has djb in editable mode (will be handled automatically)")

    current_version = get_version(djb_root)
    new_version = bump_version(current_version, part)
    tag_name = f"v{new_version}"

    click.echo(f"Current version: {current_version}")
    click.echo(f"New version: {new_version}")
    click.echo(f"Git tag: {tag_name}")

    if dry_run:
        click.secho("\n[dry-run] Would perform the following:", fg="yellow")

    runner = PublishRunner(dry_run)

    # Check for uncommitted changes in djb (only in non-dry-run mode)
    if not dry_run:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=djb_root,
            capture_output=True,
            text=True,
        )
        uncommitted = [
            line for line in result.stdout.strip().split("\n")
            if line and not line.endswith("pyproject.toml")
        ]
        if uncommitted:
            click.secho("Warning: You have uncommitted changes in djb:", fg="yellow")
            for line in uncommitted:
                click.echo(f"  {line}")
            if not click.confirm("Continue anyway?", default=False):
                raise click.ClickException("Aborted")
        click.echo("")  # Blank line before steps

    # Phase 1: Update and publish djb
    runner.action(
        f"Update djb version in pyproject.toml to {new_version}",
        lambda: set_version(djb_root, new_version),
    )

    # Stage + commit as one logical step
    runner.run_git(["add", "pyproject.toml"], cwd=djb_root)  # silent
    runner.run_git(
        ["commit", "-m", f"Bump djb version to {new_version}"],
        cwd=djb_root,
        description=f"Commit djb: 'Bump djb version to {new_version}'",
    )

    runner.run_git(
        ["tag", tag_name],
        cwd=djb_root,
        description=f"Create tag: {tag_name}",
    )

    # Push commit + tag as one logical step
    runner.run_git(["push", "origin", "main"], cwd=djb_root)  # silent
    runner.run_git(
        ["push", "origin", tag_name],
        cwd=djb_root,
        description="Push djb commit and tag to origin",
    )

    if not dry_run:
        click.secho(f"\n✓ Published djb {new_version}!", fg="green", bold=True)
        click.echo("The GitHub Actions workflow will build and upload to PyPI.")
        click.echo("Track progress at: https://github.com/kajicom/djb/actions")

    # Phase 2: Update parent project if it exists
    if parent_root:
        if not dry_run:
            click.echo(f"\nWaiting for PyPI to have djb {new_version}...")
            click.echo("(This may take a few minutes while GitHub Actions builds and uploads)")

            if not wait_for_pypi(new_version):
                click.secho(
                    f"Timeout waiting for djb {new_version} on PyPI. "
                    "You may need to manually update the parent project.",
                    fg="yellow",
                )
                return

            click.secho(f"✓ djb {new_version} is now available on PyPI", fg="green")
            click.echo("\nUpdating parent project dependency...")

        # Stash editable config if active
        if parent_editable:
            runner.action(
                "Stash editable djb configuration",
                lambda: remove_editable_config(parent_root, parent_state),
            )

        try:
            runner.action(
                f"Update parent project dependency to djb>={new_version}",
                lambda: update_parent_dependency(parent_root, new_version),
            )

            # Cache bust + lock regen as one step
            runner.action(None, bust_uv_cache)  # silent

            def regen_lock():
                if not regenerate_uv_lock(parent_root):
                    raise click.ClickException("Failed to regenerate uv.lock")

            runner.action("Regenerate uv.lock with new version", regen_lock)

            # Stage + commit as one step
            runner.run_git(["add", "pyproject.toml", "uv.lock"], cwd=parent_root)  # silent
            runner.run_git(
                ["commit", "-m", f"Update djb dependency to {new_version}"],
                cwd=parent_root,
                description=f"Commit parent: 'Update djb dependency to {new_version}'",
            )

            runner.run_git(
                ["push", "origin", "main"],
                cwd=parent_root,
                description="Push parent commit to origin",
            )

            if not dry_run:
                click.secho(f"✓ Updated parent project dependency to djb>={new_version}", fg="green")

        finally:
            # Re-enable editable mode if it was active (even on error)
            if parent_editable:
                runner.action(
                    "Re-enable editable djb with current version",
                    lambda: restore_editable_with_current_version(parent_root, parent_state),
                )
                if not dry_run:
                    click.secho("✓ Editable mode restored for local development", fg="green")
