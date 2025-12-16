"""
djb init CLI - Initialize djb development environment.

Provides commands for setting up system dependencies, Python packages, and frontend tooling.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

import click

from djb.cli.logging import get_logger

logger = get_logger(__name__)

# Environments to manage secrets for
SECRETS_ENVIRONMENTS = ["dev", "staging", "heroku_prod"]


class SecretsStatus(NamedTuple):
    """Status of secrets initialization for an environment."""

    initialized: list[str]  # Newly created
    upgraded: list[str]  # Existing but upgraded with new keys
    up_to_date: list[str]  # Already up to date


def _init_or_upgrade_secrets(project_root: Path) -> SecretsStatus:
    """Initialize or upgrade secrets for all environments.

    For each environment:
    - If secrets file doesn't exist: create it from template
    - If secrets file exists: upgrade it with any new template keys

    Returns a SecretsStatus indicating what was done.
    """
    from djb.cli.secrets import _deep_merge_missing, _get_template
    from djb.secrets import AgeKey, SecretsManager, get_default_key_path

    key_path = get_default_key_path()
    secrets_dir = project_root / "secrets"

    # Ensure age key exists
    if not key_path.exists():
        age_key = AgeKey.generate()
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_text(age_key.to_private_string())
        key_path.chmod(0o600)
        logger.done(f"Generated age key at {key_path}")
    else:
        age_key = AgeKey.from_private_string(key_path.read_text().strip())

    public_key = age_key.to_public_string()

    # Ensure secrets directory exists
    secrets_dir.mkdir(parents=True, exist_ok=True)

    # Create .gitignore for secrets directory if needed
    gitignore_path = secrets_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(
            "# Decrypted secrets (never commit these)\n"
            "*.decrypted.yaml\n"
            "*.plaintext.yaml\n"
            "*.secret\n"
        )

    manager = SecretsManager(secrets_dir=secrets_dir, age_key=age_key)

    initialized: list[str] = []
    upgraded: list[str] = []
    up_to_date: list[str] = []

    for env in SECRETS_ENVIRONMENTS:
        secrets_file = secrets_dir / f"{env}.yaml"
        template = _get_template(env)

        if not secrets_file.exists():
            # Create new secrets file from template
            manager.save_secrets(env, template, [public_key], encrypt=True)
            initialized.append(env)
        else:
            # Upgrade existing secrets with any new template keys
            try:
                existing = manager.load_secrets(env, decrypt=True)
                merged, added = _deep_merge_missing(existing, template)

                if added:
                    manager.save_secrets(env, merged, [public_key], encrypt=True)
                    upgraded.append(env)
                else:
                    up_to_date.append(env)
            except Exception as e:
                logger.warning(f"Failed to upgrade {env} secrets: {e}")
                up_to_date.append(env)

    return SecretsStatus(initialized=initialized, upgraded=upgraded, up_to_date=up_to_date)


def _run(
    cmd: list[str],
    cwd: Path | None = None,
    label: str | None = None,
    done_msg: str | None = None,
    halt_on_fail: bool = True,
) -> int:
    """Run a shell command with optional error handling."""
    if label:
        logger.next(label)
    logger.debug(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True)
    if result.returncode != 0 and halt_on_fail:
        logger.error(f"{label or 'Command'} failed with exit code {result.returncode}")
        if result.stderr:
            logger.debug(result.stderr.decode())
        raise click.ClickException(f"{label or 'Command'} failed")
    if done_msg:
        logger.done(done_msg)
    return result.returncode


def _install_git_hooks(project_root: Path) -> None:
    """Install git hooks for the project.

    Installs:
    - pre-commit hook to prevent committing pyproject.toml with editable djb
    """
    logger.next("Installing git hooks")

    git_dir = project_root / ".git"
    if not git_dir.exists():
        logger.skip("Not a git repository, skipping hooks")
        return

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    # Source hook script location
    hook_source = project_root / "scripts" / "pre-commit-editable-check"

    if not hook_source.exists():
        logger.warning(f"Hook script not found at {hook_source}")
        logger.info("  Create scripts/pre-commit-editable-check to enable hook installation")
        return

    # Destination hook path
    pre_commit_hook = hooks_dir / "pre-commit"

    # Check if pre-commit hook already exists
    if pre_commit_hook.exists():
        # Check if it's our hook or something else
        content = pre_commit_hook.read_text()
        if "pre-commit-editable-check" in content or "editable djb" in content:
            logger.done("Git hooks already installed")
            return
        else:
            # There's an existing pre-commit hook, don't overwrite it
            logger.warning("Existing pre-commit hook found, not overwriting")
            logger.info(f"  To install manually, add a call to: {hook_source}")
            return

    # Install the hook by copying the script
    import shutil

    shutil.copy(hook_source, pre_commit_hook)
    pre_commit_hook.chmod(0o755)
    logger.done("Git hooks installed (pre-commit: editable djb check)")


@click.command("init")
@click.option(
    "--skip-brew",
    is_flag=True,
    help="Skip installing system dependencies via Homebrew",
)
@click.option(
    "--skip-python",
    is_flag=True,
    help="Skip installing Python dependencies",
)
@click.option(
    "--skip-frontend",
    is_flag=True,
    help="Skip installing frontend dependencies",
)
@click.option(
    "--skip-secrets",
    is_flag=True,
    help="Skip secrets initialization",
)
@click.option(
    "--skip-hooks",
    is_flag=True,
    help="Skip installing git hooks",
)
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Project root directory (default: current directory)",
)
def init(
    skip_brew: bool,
    skip_python: bool,
    skip_frontend: bool,
    skip_secrets: bool,
    skip_hooks: bool,
    project_root: Path | None,
):
    """Initialize djb development environment.

    Sets up everything needed for local development:

    \b
    • System dependencies (Homebrew): age, PostgreSQL, GDAL, Bun
    • Python dependencies: uv sync
    • Frontend dependencies: bun install in frontend/
    • Git hooks: pre-commit hook to prevent committing editable djb
    • Secrets management: Age-encrypted configuration

    This command is idempotent - safe to run multiple times.
    Already-installed dependencies are skipped automatically.

    \b
    Examples:
      djb init                    # Full setup
      djb init --skip-brew        # Skip Homebrew (already installed)
      djb init --skip-secrets     # Skip secrets (configure later)
    """
    if project_root is None:
        project_root = Path.cwd()

    logger.info("Initializing djb development environment")

    # Check if we're on macOS
    is_macos = sys.platform == "darwin"

    # Install system dependencies via Homebrew
    if not skip_brew and is_macos:
        logger.next("Installing system dependencies via Homebrew")

        # Check if brew is installed
        brew_check = subprocess.run(["which", "brew"], capture_output=True)
        if brew_check.returncode != 0:
            logger.error("Homebrew not found. Please install from https://brew.sh/")
            raise click.ClickException(
                "Homebrew is required for automatic dependency installation"
            )

        # Install age (for secrets encryption)
        result = subprocess.run(["brew", "list", "age"], capture_output=True)
        if result.returncode != 0:
            _run(["brew", "install", "age"], label="Installing age", done_msg="age installed")
        else:
            logger.done("age already installed")

        # Install PostgreSQL (for database)
        result = subprocess.run(["brew", "list", "postgresql@17"], capture_output=True)
        if result.returncode != 0:
            _run(
                ["brew", "install", "postgresql@17"],
                label="Installing PostgreSQL",
                done_msg="postgresql@17 installed",
            )
        else:
            logger.done("postgresql@17 already installed")

        # Install GDAL (for GeoDjango)
        result = subprocess.run(["brew", "list", "gdal"], capture_output=True)
        if result.returncode != 0:
            _run(["brew", "install", "gdal"], label="Installing GDAL", done_msg="gdal installed")
        else:
            logger.done("gdal already installed")

        # Install Bun (JavaScript runtime)
        result = subprocess.run(["which", "bun"], capture_output=True)
        if result.returncode != 0:
            _run(
                ["brew", "install", "oven-sh/bun/bun"],
                label="Installing Bun",
                done_msg="bun installed",
            )
        else:
            logger.done("bun already installed")

        logger.done("System dependencies ready")
    elif not skip_brew and not is_macos:
        logger.skip("Homebrew installation (not on macOS)")
        logger.info("Please install dependencies manually:")
        logger.info("  - age: https://age-encryption.org/")
        logger.info("  - PostgreSQL 17: https://www.postgresql.org/")
        logger.info("  - GDAL: https://gdal.org/")
        logger.info("  - Bun: https://bun.sh/")
    else:
        logger.skip("System dependency installation")

    # Install Python dependencies
    if not skip_python:
        _run(
            ["uv", "sync"],
            cwd=project_root,
            label="Installing Python dependencies",
            done_msg="Python dependencies installed",
        )
    else:
        logger.skip("Python dependency installation")

    # Install frontend dependencies
    if not skip_frontend:
        frontend_dir = project_root / "frontend"
        if frontend_dir.exists():
            _run(
                ["bun", "install"],
                cwd=frontend_dir,
                label="Installing frontend dependencies",
                done_msg="Frontend dependencies installed",
            )
        else:
            logger.skip(f"Frontend directory not found at {frontend_dir}")
    else:
        logger.skip("Frontend dependency installation")

    # Install git hooks
    if not skip_hooks:
        _install_git_hooks(project_root)
    else:
        logger.skip("Git hooks installation")

    # Initialize secrets
    if not skip_secrets:
        logger.next("Initializing secrets management")
        status = _init_or_upgrade_secrets(project_root)

        # Report what happened
        if status.initialized:
            logger.done(f"Created secrets: {', '.join(status.initialized)}")
        if status.upgraded:
            logger.done(f"Upgraded secrets: {', '.join(status.upgraded)}")
        if status.up_to_date and not status.initialized and not status.upgraded:
            logger.done("Secrets already up to date")

        # Show next steps if any secrets were created
        if status.initialized:
            logger.info("Remember to edit your secrets:")
            logger.info("  djb secrets edit dev")
            logger.info("  djb secrets edit heroku_prod")
    else:
        logger.skip("Secrets initialization")

    # Final success message
    logger.done("djb initialization complete!")
    logger.info("Next steps:")
    logger.info("  1. Configure your Django project to use djb")
    logger.info("  2. Edit secrets: djb secrets edit dev")
    logger.info("  3. Set up your database and run migrations")
    logger.info("  4. Deploy: djb deploy heroku --app your-app")
