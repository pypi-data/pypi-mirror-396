"""
djb init CLI - Initialize djb development environment.

Provides commands for setting up system dependencies, Python packages, and frontend tooling.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import click

from djb.cli.logging import get_logger
from djb.cli.secrets import _ensure_prerequisites as ensure_secrets_prerequisites
from djb.cli.utils import check_cmd, run_cmd
from djb.config import (
    get_config_path,
    get_email,
    get_name,
    get_project_name,
    get_project_name_from_pyproject,
    set_email,
    set_name,
    set_project_name,
)
from djb.secrets import SECRETS_ENVIRONMENTS, SecretsStatus, init_or_upgrade_secrets

logger = get_logger(__name__)

EMAIL_REGEX = re.compile(r"^.+@.+\..+$")


def _get_git_config(key: str) -> str | None:
    """Get a value from git config."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", key],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, OSError):
        pass
    return None


def _set_git_config(key: str, value: str) -> bool:
    """Set a value in git config (global)."""
    try:
        result = subprocess.run(
            ["git", "config", "--global", key, value],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except (FileNotFoundError, OSError):
        return False


def _configure_user_identity() -> tuple[str | None, str | None]:
    """Configure user identity (name and email).

    Checks git config first; if values exist, copies them to djb config.
    If not configured, prompts the user and sets both git and djb config.

    Returns:
        Tuple of (name, email), either or both may be None if skipped.
    """
    config_path = get_config_path()
    name = get_name()
    email = get_email()
    git_name = _get_git_config("user.name")
    git_email = _get_git_config("user.email")

    # Track what was copied from git
    copied_from_git = []

    # Handle name
    if name:
        # Already configured in djb
        logger.info(f"Name: {name}")
    elif git_name:
        # Copy from git config
        set_name(git_name)
        name = git_name
        copied_from_git.append("name")
    else:
        # Prompt user
        for _ in range(3):
            entered_name = click.prompt("Enter your name", default="", show_default=False)
            if entered_name:
                set_name(entered_name)
                _set_git_config("user.name", entered_name)
                name = entered_name
                logger.done(f"Name saved: {name}")
                break
            else:
                logger.warning("Name is required for git commits.")
        else:
            logger.warning("Name skipped.")

    # Handle email
    if email:
        # Already configured in djb
        logger.info(f"Email: {email}")
    elif git_email:
        # Copy from git config
        set_email(git_email)
        email = git_email
        copied_from_git.append("email")
    else:
        # Prompt user
        for _ in range(3):
            entered_email = click.prompt("Enter your email", default="", show_default=False)
            if not entered_email:
                logger.warning("Email is required for git commits.")
                continue
            if EMAIL_REGEX.match(entered_email):
                set_email(entered_email)
                _set_git_config("user.email", entered_email)
                email = entered_email
                logger.done(f"Email saved: {email}")
                break
            else:
                logger.warning("Invalid email format. Please try again.")
        else:
            logger.warning("Email skipped.")

    # Report what was copied from git
    if copied_from_git:
        logger.info(f"Copied {' and '.join(copied_from_git)} from git config")

    # Show where config is stored
    if name or email:
        logger.info(f"Config saved to: {config_path}")

    return name, email


def _configure_project_name(project_root: Path) -> str | None:
    """Configure project name.

    Checks existing config first, then pyproject.toml, then prompts if needed.

    Args:
        project_root: Project root directory.

    Returns:
        Project name, or None if skipped.
    """
    # Check if already configured
    existing = get_project_name(project_root)
    if existing:
        logger.info(f"Project name: {existing}")
        return existing

    # Try to get default from pyproject.toml or directory name
    default = get_project_name_from_pyproject(project_root) or project_root.name

    # Prompt user with default
    project_name = click.prompt(
        "Enter project name",
        default=default,
        show_default=True,
    )

    if project_name:
        set_project_name(project_name, project_root)
        logger.done(f"Project name saved: {project_name}")
        return project_name

    return None


def _find_settings_file(project_root: Path) -> Path | None:
    """Find the Django settings.py file in the project.

    Searches for settings.py in subdirectories of project_root that look like
    Django project directories (contain __init__.py).

    Returns:
        Path to settings.py if found, None otherwise.
    """
    # Look for directories containing settings.py
    for item in project_root.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            settings_path = item / "settings.py"
            init_path = item / "__init__.py"
            # Must have both settings.py and __init__.py to be a Django project
            if settings_path.exists() and init_path.exists():
                return settings_path
    return None


def _add_djb_to_installed_apps(project_root: Path) -> bool:
    """Add 'djb' to Django's INSTALLED_APPS if not already present.

    Finds the settings.py file and modifies INSTALLED_APPS to include 'djb'.
    Inserts djb after the last django.* app for proper ordering.

    Returns:
        True if djb was added, False if already present or settings not found.
    """
    settings_path = _find_settings_file(project_root)
    if not settings_path:
        logger.skip("No Django settings.py found")
        return False

    content = settings_path.read_text()

    # Check if djb is already in INSTALLED_APPS
    # Match various formats: "djb", 'djb', with or without trailing comma
    if re.search(r'["\']djb["\']', content):
        logger.done("djb already in INSTALLED_APPS")
        return False

    # Find INSTALLED_APPS list and insert djb
    # Match the pattern: INSTALLED_APPS = [
    pattern = r"(INSTALLED_APPS\s*=\s*\[)"

    match = re.search(pattern, content)
    if not match:
        logger.warning("Could not find INSTALLED_APPS in settings.py")
        return False

    # Find a good insertion point - after the last django.* entry
    # or at the end of the list if no django entries
    lines = content.split("\n")
    installed_apps_start = None
    last_django_line = None
    bracket_depth = 0
    in_installed_apps = False

    for i, line in enumerate(lines):
        if "INSTALLED_APPS" in line and "=" in line:
            installed_apps_start = i
            in_installed_apps = True

        if in_installed_apps:
            bracket_depth += line.count("[") - line.count("]")
            # Match django.* apps (django.contrib.*, django_components, etc.)
            if re.search(r'["\']django[._]', line):
                last_django_line = i
            if bracket_depth == 0 and installed_apps_start is not None and i > installed_apps_start:
                break

    if last_django_line is not None:
        # Insert after the last django.* line
        insert_line = last_django_line
        # Detect indentation from the previous line
        indent_match = re.match(r"^(\s*)", lines[insert_line])
        indent = indent_match.group(1) if indent_match else "    "
        lines.insert(insert_line + 1, f'{indent}"djb",')
    elif installed_apps_start is not None:
        # No django entries, insert after the opening bracket
        indent = "    "
        lines.insert(installed_apps_start + 1, f'{indent}"djb",')
    else:
        logger.warning("Could not determine where to insert djb in INSTALLED_APPS")
        return False

    # Write the modified content
    settings_path.write_text("\n".join(lines))
    logger.done(f"Added djb to INSTALLED_APPS in {settings_path.name}")
    return True


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
    • System dependencies (Homebrew): SOPS, age, PostgreSQL, GDAL, Bun
    • Python dependencies: uv sync
    • Django settings: adds djb to INSTALLED_APPS
    • Frontend dependencies: bun install in frontend/
    • Git hooks: pre-commit hook to prevent committing editable djb
    • Secrets management: SOPS-encrypted configuration

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

    # Validate we're in a Python project
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        raise click.ClickException(
            f"No pyproject.toml found in {project_root}. "
            "Run 'djb init' from your project root directory."
        )

    logger.info("Initializing djb development environment")

    # Configure user identity (name and email)
    logger.next("Configuring user identity")
    user_name, user_email = _configure_user_identity()

    # Configure project name
    logger.next("Configuring project name")
    project_name = _configure_project_name(project_root)

    # Check if we're on a platform that supports Homebrew (macOS or Linux)
    is_brew_supported = sys.platform in ("darwin", "linux")

    # Install system dependencies via Homebrew
    if not skip_brew and is_brew_supported:
        logger.next("Installing system dependencies via Homebrew")

        # Check if brew is installed
        if not check_cmd(["which", "brew"]):
            logger.error("Homebrew not found. Please install from https://brew.sh/")
            raise click.ClickException("Homebrew is required for automatic dependency installation")

        # Install SOPS (for secrets encryption)
        if not check_cmd(["brew", "list", "sops"]):
            run_cmd(["brew", "install", "sops"], label="Installing sops", done_msg="sops installed")
        else:
            logger.done("sops already installed")

        # Install age (for secrets encryption)
        if not check_cmd(["brew", "list", "age"]):
            run_cmd(["brew", "install", "age"], label="Installing age", done_msg="age installed")
        else:
            logger.done("age already installed")

        # Install PostgreSQL (for database)
        if not check_cmd(["brew", "list", "postgresql@17"]):
            run_cmd(
                ["brew", "install", "postgresql@17"],
                label="Installing PostgreSQL",
                done_msg="postgresql@17 installed",
            )
        else:
            logger.done("postgresql@17 already installed")

        # Install GDAL (for GeoDjango)
        if not check_cmd(["brew", "list", "gdal"]):
            run_cmd(["brew", "install", "gdal"], label="Installing GDAL", done_msg="gdal installed")
        else:
            logger.done("gdal already installed")

        # Install Bun (JavaScript runtime)
        if not check_cmd(["which", "bun"]):
            run_cmd(
                ["brew", "install", "oven-sh/bun/bun"],
                label="Installing Bun",
                done_msg="bun installed",
            )
        else:
            logger.done("bun already installed")

        logger.done("System dependencies ready")
    elif not skip_brew and not is_brew_supported:
        logger.skip("Homebrew installation (not supported on this platform)")
        logger.info("Please install dependencies manually:")
        logger.info("  - SOPS: https://github.com/getsops/sops")
        logger.info("  - age: https://age-encryption.org/")
        logger.info("  - PostgreSQL 17: https://www.postgresql.org/")
        logger.info("  - GDAL: https://gdal.org/")
        logger.info("  - Bun: https://bun.sh/")
    else:
        logger.skip("System dependency installation")

    # Install Python dependencies
    if not skip_python:
        run_cmd(
            ["uv", "sync"],
            cwd=project_root,
            label="Installing Python dependencies",
            done_msg="Python dependencies installed",
        )
    else:
        logger.skip("Python dependency installation")

    # Add djb to INSTALLED_APPS
    logger.next("Configuring Django settings")
    _add_djb_to_installed_apps(project_root)

    # Install frontend dependencies
    if not skip_frontend:
        frontend_dir = project_root / "frontend"
        if frontend_dir.exists():
            run_cmd(
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
        # Ensure SOPS and age are installed (quiet=True since Homebrew section already reported)
        if not ensure_secrets_prerequisites(quiet=True):
            logger.fail("Cannot initialize secrets without SOPS and age")
            sys.exit(1)
        status = init_or_upgrade_secrets(project_root, email=user_email, name=user_name)

        # Report what happened
        if status.initialized:
            logger.done(f"Created secrets: {', '.join(status.initialized)}")
        if status.upgraded:
            logger.done(f"Upgraded secrets: {', '.join(status.upgraded)}")
        if status.up_to_date and not status.initialized and not status.upgraded:
            logger.done("Secrets already up to date")

        # Auto-commit .sops.yaml if this is a git repo and the file was modified
        secrets_dir = project_root / "secrets"
        git_dir = project_root / ".git"
        if git_dir.exists() and user_email:
            sops_config = secrets_dir / ".sops.yaml"

            files_to_commit = []
            if sops_config.exists():
                # Check if file is untracked or modified
                result = run_cmd(
                    ["git", "status", "--porcelain", str(sops_config)],
                    cwd=project_root,
                    halt_on_fail=False,
                )
                if result.stdout.strip():
                    files_to_commit.append(str(sops_config.relative_to(project_root)))

            if files_to_commit:
                logger.next("Committing public key to git")
                logger.info(f"Files: {', '.join(files_to_commit)}")

                # Stage the files
                for file in files_to_commit:
                    run_cmd(["git", "add", file], cwd=project_root, halt_on_fail=False)

                # Commit with output visible
                commit_msg = f"Add public key for {user_email}"
                result = run_cmd(
                    ["git", "commit", "-m", commit_msg],
                    cwd=project_root,
                    halt_on_fail=False,
                    fail_msg="Could not commit public key",
                )
                if result.returncode == 0:
                    # Show the commit output
                    if result.stdout.strip():
                        for line in result.stdout.strip().split("\n"):
                            logger.info(f"  {line}")
                    logger.done("Public key committed")

        # Show next steps if any secrets were created
        if status.initialized:
            logger.info("Remember to edit your secrets:")
            logger.info("  djb secrets edit dev")
            logger.info("  djb secrets edit production")
    else:
        logger.skip("Secrets initialization")

    # Final success message
    logger.done("djb initialization complete!")
    logger.note()
    logger.info("Next steps:")
    logger.info("  1. Edit secrets: djb secrets edit dev")
    logger.info("  2. Back up your key: djb secrets export-key | pbcopy")
    if project_name:
        logger.info(f"  3. Deploy: djb deploy heroku")
    else:
        logger.info("  3. Deploy: djb deploy heroku --app your-app")
    logger.note()
    if not project_name:
        logger.tip("Set project_name in .djb/config.yaml to skip --app flag")
    logger.tip("Run 'djb secrets --help' for all secrets commands")
