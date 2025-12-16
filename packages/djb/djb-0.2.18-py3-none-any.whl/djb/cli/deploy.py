"""
djb deploy CLI - Heroku deployment commands.

Provides commands for deploying and reverting Django applications to Heroku.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import click

from djb.cli.app_name import get_app_name
from djb.cli.editable_stash import stashed_editable
from djb.cli.utils import flatten_dict, run_command
from djb.secrets import AgeKey, SecretsManager, get_default_key_path


def _get_app_or_fail(app: str | None) -> str:
    """Get app name from argument or auto-detect from settings.

    Args:
        app: App name from CLI option (may be None)

    Returns:
        App name to use

    Raises:
        click.ClickException: If no app name provided and auto-detection fails
    """
    if app:
        return app

    detected = get_app_name()
    if detected:
        click.echo(f"Using app name from DJB_APP_NAME setting: {detected}")
        return detected

    raise click.ClickException(
        "No app name provided. Either use --app or set DJB_APP_NAME in Django settings."
    )


@click.group()
def deploy():
    """Deploy applications to Heroku."""
    pass


@deploy.command("heroku")
@click.option(
    "--app",
    default=None,
    help="Heroku app name (default: from DJB_APP_NAME setting)",
)
@click.option(
    "--local-build",
    is_flag=True,
    help="Build frontend locally before push (default: let Heroku buildpack build).",
)
@click.option(
    "--skip-migrate",
    is_flag=True,
    help="Skip running database migrations on Heroku.",
)
@click.option(
    "--skip-secrets",
    is_flag=True,
    help="Skip syncing secrets to Heroku config vars.",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Auto-confirm prompts (e.g., uncommitted changes warning).",
)
@click.option(
    "--frontend-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Frontend directory containing package.json (default: ./frontend)",
)
@click.option(
    "--secrets-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Secrets directory (default: ./secrets)",
)
@click.option(
    "--key-path",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to age key file (default: ~/.age/keys.txt)",
)
def heroku(
    app: str | None,
    local_build: bool,
    skip_migrate: bool,
    skip_secrets: bool,
    yes: bool,
    frontend_dir: Path | None,
    secrets_dir: Path | None,
    key_path: Path | None,
):
    """Deploy the application to Heroku.

    Complete deployment workflow:

    \b
    • Syncs production secrets to Heroku config vars
    • Pushes code to Heroku (bun buildpack builds frontend, Python buildpack runs collectstatic)
    • Runs database migrations
    • Tags the deployment for tracking

    If djb is installed in editable mode (local development), the editable
    configuration is temporarily stashed and restored after deployment.

    Checks for uncommitted changes and confirms before proceeding.

    If --app is not provided, uses DJB_APP_NAME from Django settings.

    \b
    Examples:
      djb deploy heroku                          # Use DJB_APP_NAME from settings
      djb deploy heroku --app myapp              # Explicit app name
      djb deploy heroku --local-build            # Build frontend locally first
      djb deploy heroku --skip-migrate           # Skip migrations
    """
    repo_root = Path.cwd()
    app = _get_app_or_fail(app)

    if frontend_dir is None:
        frontend_dir = repo_root / "frontend"
    if secrets_dir is None:
        secrets_dir = repo_root / "secrets"
    if key_path is None:
        key_path = get_default_key_path()

    # Temporarily remove editable djb config if present (restores automatically on exit)
    with stashed_editable(repo_root) as state:
        if state.was_editable:
            click.echo("Stashed editable djb configuration for deploy...")

        _deploy_heroku_impl(
            app=app,
            local_build=local_build,
            skip_migrate=skip_migrate,
            skip_secrets=skip_secrets,
            yes=yes,
            repo_root=repo_root,
            frontend_dir=frontend_dir,
            secrets_dir=secrets_dir,
            key_path=key_path,
        )

        if state.was_editable:
            click.echo("Restoring editable djb configuration...")


def _deploy_heroku_impl(
    app: str,
    local_build: bool,
    skip_migrate: bool,
    skip_secrets: bool,
    yes: bool,
    repo_root: Path,
    frontend_dir: Path,
    secrets_dir: Path,
    key_path: Path,
):
    """Internal implementation of Heroku deployment."""
    # Check if logged into Heroku
    try:
        run_command(["heroku", "auth:whoami"], label="Checking Heroku auth", halt_on_fail=True)
    except click.ClickException:
        raise click.ClickException(
            "Not logged into Heroku. Run 'heroku login' first."
        )

    # Verify we're in a git repository
    if not (repo_root / ".git").exists():
        raise click.ClickException("Not in a git repository")

    # Sync secrets to Heroku config vars
    if not skip_secrets:
        click.echo("Syncing production secrets to Heroku...")
        try:
            if not key_path.exists():
                click.secho("Warning: Age key not found, skipping secrets sync", fg="yellow")
            else:
                key = AgeKey.from_private_string(key_path.read_text().strip())
                manager = SecretsManager(secrets_dir=secrets_dir, age_key=key)
                secrets = manager.load_secrets("heroku_prod", decrypt=True)
                flat_secrets = flatten_dict(secrets)

                # Heroku-managed config vars that should not be overwritten
                heroku_managed_keys = {
                    "DATABASE_URL",  # Managed by Heroku Postgres addon
                    "DB_CREDENTIALS_USERNAME",
                    "DB_CREDENTIALS_PASSWORD",
                    "DB_CREDENTIALS_DATABASE",
                    "DB_CREDENTIALS_HOST",
                    "DB_CREDENTIALS_PORT",
                }

                # Set config vars on Heroku
                for key_name, value in flat_secrets.items():
                    # Skip Heroku-managed database config vars
                    if key_name in heroku_managed_keys:
                        click.secho(
                            f"Skipping {key_name} (managed by Heroku)", fg="yellow"
                        )
                        continue

                    # Skip if it's a complex value
                    if len(value) > 500:
                        click.secho(f"Skipping {key_name} (value too large)", fg="yellow")
                        continue

                    subprocess.run(
                        ["heroku", "config:set", f"{key_name}={value}", "--app", app],
                        capture_output=True,
                        check=True,
                    )

                click.secho(
                    f"✓ Synced {len(flat_secrets)} secrets to Heroku config", fg="green"
                )
        except Exception as e:
            click.secho(f"Warning: Failed to sync secrets: {e}", fg="yellow")
            if not yes and not click.confirm("Continue deployment without secrets?", default=False):
                raise click.ClickException("Deployment cancelled")
    else:
        click.secho("Skipping secrets sync.", fg="yellow")

    # Check for uncommitted changes
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        click.secho("Warning: You have uncommitted changes:", fg="yellow")
        click.echo(result.stdout)
        if not yes and not click.confirm("Continue with deployment?", default=False):
            raise click.ClickException("Deployment cancelled")

    # Optionally build frontend locally (default: let Heroku bun buildpack handle it)
    if local_build:
        if frontend_dir.exists():
            click.echo("Building frontend assets locally...")
            run_command(
                ["bun", "run", "build"],
                cwd=frontend_dir,
                label="Frontend build",
            )
            click.secho("Frontend build complete.", fg="green")

            # Also run collectstatic locally if doing local build
            click.echo("Collecting Django static files...")
            run_command(
                ["python", "manage.py", "collectstatic", "--noinput", "--clear"],
                cwd=repo_root,
                label="collectstatic",
            )
            click.secho("Static files collected.", fg="green")
        else:
            click.secho(f"Frontend directory not found at {frontend_dir}, skipping build.", fg="yellow")

    # Get current git commit hash for tracking
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    commit_hash = result.stdout.strip()[:7]

    # Check current branch
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    current_branch = result.stdout.strip()

    click.echo(f"Deploying from branch '{current_branch}' (commit {commit_hash})...")

    # Push to Heroku
    click.echo(f"Pushing to Heroku ({app})...")
    run_command(
        ["git", "push", "heroku", f"{current_branch}:main", "--force"],
        label="git push heroku",
    )
    click.secho("Code pushed to Heroku.", fg="green")

    # Run migrations
    if not skip_migrate:
        click.echo("Running database migrations on Heroku...")
        run_command(
            ["heroku", "run", "python manage.py migrate", "--app", app],
            label="heroku migrate",
        )
        click.secho("Migrations complete.", fg="green")
    else:
        click.secho("Skipping database migrations.", fg="yellow")

    # Tag the deployment
    tag_name = f"deploy-{commit_hash}"
    subprocess.run(
        ["git", "tag", "-f", tag_name],
        cwd=repo_root,
        capture_output=True,
    )
    subprocess.run(
        ["git", "push", "--tags", "--force"],
        cwd=repo_root,
        capture_output=True,
    )

    click.secho(f"\n✓ Deployment successful! (commit: {commit_hash})", fg="green", bold=True)
    click.echo(f"App URL: https://{app}.herokuapp.com/")
    click.echo(f"Logs: heroku logs --tail --app {app}")


@deploy.command("revert")
@click.option(
    "--app",
    default=None,
    help="Heroku app name (default: from DJB_APP_NAME setting)",
)
@click.argument("git_hash", required=False)
@click.option(
    "--skip-migrate",
    is_flag=True,
    help="Skip running database migrations on Heroku.",
)
def revert(app: str | None, git_hash: str | None, skip_migrate: bool):
    """Revert to a previous deployment.

    Pushes a previous git commit to Heroku, effectively rolling back
    your deployment. By default reverts to the previous commit (HEAD~1).

    Confirms before executing the revert. Tags the revert for tracking.

    If --app is not provided, uses DJB_APP_NAME from Django settings.

    \b
    Examples:
      djb deploy revert                      # Revert using DJB_APP_NAME
      djb deploy revert --app myapp          # Revert to previous commit
      djb deploy revert abc123               # Revert to specific commit
      djb deploy revert --skip-migrate       # Revert without migrations
    """
    repo_root = Path.cwd()
    app = _get_app_or_fail(app)

    # Check if logged into Heroku
    try:
        run_command(["heroku", "auth:whoami"], label="Checking Heroku auth", halt_on_fail=True)
    except click.ClickException:
        raise click.ClickException(
            "Not logged into Heroku. Run 'heroku login' first."
        )

    # Verify we're in a git repository
    if not (repo_root / ".git").exists():
        raise click.ClickException("Not in a git repository")

    # If no git hash provided, use the previous commit
    if git_hash is None:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD~1"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise click.ClickException("Could not determine previous commit")
        git_hash = result.stdout.strip()
        click.echo(f"No git hash provided, using previous commit: {git_hash[:7]}")

    # Verify the git hash exists
    result = subprocess.run(
        ["git", "cat-file", "-t", git_hash],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise click.ClickException(f"Git hash '{git_hash}' not found in repository")

    # Get full commit info
    result = subprocess.run(
        ["git", "log", "-1", "--oneline", git_hash],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    commit_info = result.stdout.strip()

    click.echo(f"Reverting to: {commit_info}")
    if not click.confirm("Continue with revert?", default=False):
        raise click.ClickException("Revert cancelled")

    # Push the specified commit to Heroku
    click.echo(f"Pushing commit {git_hash[:7]} to Heroku ({app})...")
    run_command(
        ["git", "push", "heroku", f"{git_hash}:main", "--force"],
        label="git push heroku (revert)",
    )
    click.secho("Code pushed to Heroku.", fg="green")

    # Run migrations
    if not skip_migrate:
        click.echo("Running database migrations on Heroku...")
        run_command(
            ["heroku", "run", "python manage.py migrate", "--app", app],
            label="heroku migrate",
        )
        click.secho("Migrations complete.", fg="green")
    else:
        click.secho("Skipping database migrations.", fg="yellow")

    # Tag the revert
    short_hash = git_hash[:7]
    tag_name = f"revert-to-{short_hash}"
    subprocess.run(
        ["git", "tag", "-f", tag_name],
        cwd=repo_root,
        capture_output=True,
    )
    subprocess.run(
        ["git", "push", "--tags", "--force"],
        cwd=repo_root,
        capture_output=True,
    )

    click.secho(f"\n✓ Revert successful! (commit: {short_hash})", fg="green", bold=True)
    click.echo(f"App URL: https://{app}.herokuapp.com/")
    click.echo(f"Logs: heroku logs --tail --app {app}")
