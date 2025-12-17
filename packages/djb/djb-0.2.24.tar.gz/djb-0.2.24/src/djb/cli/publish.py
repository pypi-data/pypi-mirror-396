"""
djb publish CLI - Version management and PyPI publishing.

Provides commands for bumping versions and publishing to PyPI.
"""

from __future__ import annotations

import re
import time
from collections.abc import Callable
from pathlib import Path

import click

from djb.cli.logging import get_logger
from djb.cli.utils import run_cmd
from djb.cli.editable import (
    find_djb_dir,
    is_djb_editable,
    uninstall_editable_djb,
)
from djb.core.exceptions import ProjectNotFound
from djb.project import find_project_root
from djb.cli.editable_stash import (
    bust_uv_cache,
    regenerate_uv_lock,
    restore_editable,
)

logger = get_logger(__name__)


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


def wait_for_uv_resolvable(
    repo_root: Path, version: str, timeout: int = 300, interval: int = 5
) -> bool:
    """Wait until uv can resolve the new djb version from PyPI.

    After pushing a new version to PyPI, there's a delay before the package
    index is updated and uv can resolve it. This function retries `uv lock`
    until it succeeds, which is the definitive test that the version is available.

    Args:
        repo_root: Path to the project root (where pyproject.toml is)
        version: The version waiting for (used for logging)
        timeout: Maximum time to wait in seconds (default: 5 minutes)
        interval: Time between retries in seconds (default: 5 seconds)

    Returns:
        True if uv lock succeeds within the timeout, False otherwise
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        bust_uv_cache()
        if regenerate_uv_lock(repo_root, quiet=True):
            return True
        time.sleep(interval)

    return False


def update_parent_dependency(parent_root: Path, new_version: str) -> bool:
    """Update the djb dependency version in a parent project.

    Returns True if updated, False if no change needed.
    """
    pyproject = parent_root / "pyproject.toml"
    content = pyproject.read_text()

    # Match patterns like "djb>=0.2.3" or 'djb>=0.2.3'
    new_content = re.sub(
        r'(["\'])djb>=[\d.]+(["\'])',
        f"\\1djb>={new_version}\\2",
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
            logger.info(f"  {self.step}. {description}")
        else:
            logger.next(description)

    def run_git(self, args: list[str], cwd: Path, description: str | None = None) -> None:
        """Run a git command, or print what would be done in dry-run mode.

        Pass description=None to run silently (as part of another step).
        """
        self._step(description)
        if not self.dry_run:
            run_cmd(["git"] + args, cwd=cwd, halt_on_fail=True)

    def run_shell(self, args: list[str], cwd: Path, description: str | None = None) -> bool:
        """Run a shell command, or print what would be done in dry-run mode.

        Pass description=None to run silently (as part of another step).
        Returns True on success, False on failure.
        """
        self._step(description)
        if not self.dry_run:
            result = run_cmd(args, cwd=cwd, halt_on_fail=False)
            return result.returncode == 0
        return True

    def action(self, description: str | None, func: Callable[[], object]) -> None:
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

    If run from a parent project that depends on djb,
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
    djb_dir = find_djb_dir(raise_on_missing=True)
    assert djb_dir is not None  # raise_on_missing=True guarantees this
    djb_root = djb_dir.resolve()
    logger.info(f"Found djb at: {djb_root}")

    # Check for parent project that depends on djb
    try:
        parent_root = find_project_root(djb_root.parent)
    except ProjectNotFound:
        parent_root = None
    if parent_root:
        logger.info(f"Found parent project at: {parent_root}")

    # Check if parent has djb in editable mode
    parent_editable = parent_root and is_djb_editable(parent_root)
    if parent_editable:
        logger.info("Parent project has djb in editable mode (will be handled automatically)")

    current_version = get_version(djb_root)
    new_version = bump_version(current_version, part)
    tag_name = f"v{new_version}"

    logger.info(f"Current version: {current_version}")
    logger.info(f"New version: {new_version}")
    logger.info(f"Git tag: {tag_name}")

    if dry_run:
        logger.warning("[dry-run] Would perform the following:")

    runner = PublishRunner(dry_run)

    # Check for uncommitted changes in djb (only in non-dry-run mode)
    if not dry_run:
        result = run_cmd(["git", "status", "--porcelain"], cwd=djb_root, halt_on_fail=False)
        uncommitted = [
            line
            for line in result.stdout.strip().split("\n")
            if line and not line.endswith("pyproject.toml")
        ]
        if uncommitted:
            logger.warning("You have uncommitted changes in djb:")
            for line in uncommitted:
                logger.info(f"  {line}")
            if not click.confirm("Continue anyway?", default=False):
                raise click.ClickException("Aborted")
        logger.note()  # Blank line before steps

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
        logger.done(f"Published djb {new_version}!")
        logger.info("The GitHub Actions workflow will build and upload to PyPI.")
        logger.tip("Track progress at: https://github.com/kajicom/djb/actions")

    # Phase 2: Update parent project if it exists
    if parent_root:
        if not dry_run:
            logger.next("Updating parent project dependency")

        # Stash editable config if active
        if parent_editable:
            runner.action(
                "Stash editable djb configuration",
                lambda: uninstall_editable_djb(parent_root, quiet=True),
            )

        try:
            runner.action(
                f"Update parent project dependency to djb>={new_version}",
                lambda: update_parent_dependency(parent_root, new_version),
            )

            # Wait for uv to be able to resolve the new version
            # This retries uv lock until it succeeds (the actual source of truth)
            def wait_and_lock():
                logger.info("  Waiting for PyPI to have djb available...")
                logger.info(
                    "  (This may take a few minutes while GitHub Actions builds and uploads)"
                )
                if not wait_for_uv_resolvable(parent_root, new_version):
                    # One final attempt with error output
                    if not regenerate_uv_lock(parent_root):
                        raise click.ClickException(
                            f"Timeout waiting for djb {new_version} to be resolvable. "
                            "Try running: uv lock --refresh"
                        )

            runner.action("Regenerate uv.lock with new version", wait_and_lock)

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
                logger.done(f"Updated parent project dependency to djb>={new_version}")

        finally:
            # Re-enable editable mode if it was active (even on error)
            if parent_editable:
                runner.action(
                    "Re-enable editable djb with current version",
                    lambda: restore_editable(parent_root, quiet=True),
                )
                if not dry_run:
                    logger.done("Editable mode restored for local development")
