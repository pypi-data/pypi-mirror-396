"""
djb deploy CLI - Heroku deployment commands.

Provides commands for deploying and reverting Django applications to Heroku.

Deployment Workflow
-------------------
The `djb deploy heroku` command orchestrates a complete deployment:

1. **Secrets Sync**: Decrypts secrets (based on current mode) and sets them as Heroku config vars
2. **Editable Stash**: Temporarily removes editable djb config (restored after)
3. **Git Push**: Force-pushes the current branch to Heroku's main
4. **Migrations**: Runs Django migrations on the Heroku dyno
5. **Tagging**: Tags the commit for deployment tracking (deploy-<hash>)

Why Streaming Output (_run_streaming)
-------------------------------------
Git push to Heroku produces build logs that are nice to see in real time.
A naive subprocess.run() would buffer output until completion.

The _run_streaming function uses select.poll() for non-blocking I/O:
- Streams stdout/stderr to the terminal in real-time as bytes arrive
- Captures the output for post-processing

Why Force Push
--------------
Heroku requires pushing to its `main` branch. Using --force ensures the
deployment succeeds even if the branch histories have diverged (common
after reverts or rebases). The deployment is tagged, so rollback is easy.

Editable Mode Handling
----------------------
If djb is installed in editable mode during development, the pyproject.toml
contains a local path reference that won't work on Heroku. The stashed_editable
context manager temporarily removes this configuration during git push,
then restores it after deployment completes.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import click

from djb.cli.editable_stash import stashed_editable
from djb.cli.logging import get_logger
from djb.cli.utils import check_cmd, flatten_dict, run_cmd, run_streaming
from djb.secrets import (
    SopsError,
    find_placeholder_secrets,
    get_default_key_path,
    get_default_secrets_dir,
    load_secrets_for_mode,
)
from djb.types import Mode

logger = get_logger(__name__)


def _get_app_or_fail(app: str | None, config=None) -> str:
    """Get Heroku app name from --app flag or project_name from config.

    The project_name (from --project-name, DJB_PROJECT_NAME env var, or
    pyproject.toml) is used as the default Heroku app name. Use --app
    to override when the Heroku app name differs from the project name.

    Args:
        app: App name from --app CLI option (may be None)
        config: DjbConfig from context (may be None)

    Returns:
        App name to use

    Raises:
        click.ClickException: If no app name can be determined
    """
    if app:
        return app

    if config and config.project_name:
        logger.info(f"Using project name as Heroku app: {config.project_name}")
        return config.project_name

    raise click.ClickException(
        "No app name provided. Either use --app or ensure project name is set "
        "(via --project-name, DJB_PROJECT_NAME env var, or pyproject.toml)."
    )


@click.group()
def deploy():
    """Deploy applications to Heroku."""
    pass


@deploy.group("heroku", invoke_without_command=True)
@click.option(
    "--app",
    default=None,
    help="Heroku app name (default: project_name). Use when app name differs from project.",
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
@click.pass_context
def heroku(
    ctx,
    app: str | None,
    local_build: bool,
    skip_migrate: bool,
    skip_secrets: bool,
    yes: bool,
    frontend_dir: Path | None,
    secrets_dir: Path | None,
    key_path: Path | None,
):
    """Deploy to Heroku or manage Heroku configuration.

    When invoked without a subcommand, deploys the application to Heroku.

    \b
    Deployment workflow:
    • Checks mode (warns and prompts if not production)
    • Syncs secrets to Heroku config vars (loads secrets matching current mode)
    • Pushes code to Heroku (buildpacks handle frontend and collectstatic)
    • Runs database migrations
    • Tags the deployment for tracking

    If djb is in editable mode, the config is temporarily stashed during deploy.

    \b
    Examples:
      djb deploy heroku                    # Deploy to Heroku
      djb --mode production deploy heroku  # Deploy in production mode
      djb deploy heroku --app myapp        # Explicit app name
      djb deploy heroku -y                 # Skip confirmation prompts
      djb deploy heroku setup              # Configure Heroku app
      djb deploy heroku revert             # Revert to previous deployment
    """
    # Get config from parent context (set by djb_cli)
    config = ctx.obj.config if ctx.obj and hasattr(ctx.obj, "config") else None

    # Store options in context for subcommands to access
    ctx.ensure_object(dict)
    ctx.obj["app"] = app
    ctx.obj["yes"] = yes
    ctx.obj["config"] = config  # Preserve config for subcommands

    # Only run deployment if no subcommand was invoked
    if ctx.invoked_subcommand is not None:
        return

    repo_root = Path.cwd()
    app = _get_app_or_fail(app, config)

    # Deployment guard: warn if not in production mode
    current_mode = config.mode if config else Mode.DEVELOPMENT
    if current_mode != Mode.PRODUCTION:
        logger.warning(f"Deploying to Heroku with mode={current_mode}")
        logger.info("Heroku deployments typically use mode=production.")
        logger.tip("Set production mode: djb --mode production deploy heroku")
        if not yes and not click.confirm("Continue with deployment?", default=False):
            raise click.ClickException("Deployment cancelled")

    if frontend_dir is None:
        frontend_dir = repo_root / "frontend"
    if secrets_dir is None:
        secrets_dir = get_default_secrets_dir(repo_root)
    if key_path is None:
        key_path = get_default_key_path()

    # Temporarily remove editable djb config if present (restores automatically on exit)
    # Use quiet=True since we print our own messages here
    with stashed_editable(repo_root, quiet=True) as was_editable:
        if was_editable:
            logger.info("Stashed editable djb configuration for deploy...")

        _deploy_heroku_impl(
            app=app,
            mode=current_mode,
            local_build=local_build,
            skip_migrate=skip_migrate,
            skip_secrets=skip_secrets,
            yes=yes,
            repo_root=repo_root,
            frontend_dir=frontend_dir,
            secrets_dir=secrets_dir,
            key_path=key_path,
        )

        if was_editable:
            logger.info("Restoring editable djb configuration...")


def _deploy_heroku_impl(
    app: str,
    mode: Mode,
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
        run_cmd(["heroku", "auth:whoami"], label="Checking Heroku auth", halt_on_fail=True)
    except click.ClickException:
        raise click.ClickException("Not logged into Heroku. Run 'heroku login' first.")

    # Verify we're in a git repository
    if not (repo_root / ".git").exists():
        raise click.ClickException("Not in a git repository")

    # Sync secrets to Heroku config vars
    # Use the current mode to determine which secrets to load
    if not skip_secrets:
        logger.next(f"Syncing {mode.secrets_env} secrets to Heroku")
        try:
            if not key_path.exists():
                logger.warning("Age key not found, skipping secrets sync")
            else:
                secrets = load_secrets_for_mode(
                    mode=mode,
                    secrets_dir=secrets_dir,
                    key_path=key_path,
                )

                # Check for placeholder secrets that need to be changed
                placeholders = find_placeholder_secrets(secrets)
                if placeholders:
                    logger.warning(f"Found {len(placeholders)} secret(s) with placeholder values:")
                    for key in placeholders:
                        logger.info(f"   • {key}")
                    logger.note()
                    logger.warning(
                        "These secrets contain values like 'CHANGE-ME' that must be updated."
                    )
                    logger.info(f"Run 'djb secrets edit {mode.secrets_env}' to set real values.")
                    logger.note()
                    if not yes and not click.confirm(
                        "Continue deployment with placeholder secrets?", default=False
                    ):
                        raise click.ClickException("Deployment cancelled - update secrets first")

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

                # Collect config vars to set, filtering out managed/large values
                config_vars: list[str] = []
                for key_name, value in flat_secrets.items():
                    # Skip Heroku-managed database config vars
                    if key_name in heroku_managed_keys:
                        logger.skip(f"{key_name} (managed by Heroku)")
                        continue

                    # Skip if it's a complex value
                    if len(value) > 500:
                        logger.skip(f"{key_name} (value too large)")
                        continue

                    config_vars.append(f"{key_name}={value}")

                # Set all config vars in a single Heroku call
                if config_vars:
                    subprocess.run(
                        ["heroku", "config:set", *config_vars, "--app", app],
                        capture_output=True,
                        check=True,
                    )

                logger.done(f"Synced {len(config_vars)} secrets to Heroku config")
        except (FileNotFoundError, SopsError, subprocess.CalledProcessError) as e:
            logger.warning(f"Failed to sync secrets: {e}")
            if not yes and not click.confirm("Continue deployment without secrets?", default=False):
                raise click.ClickException("Deployment cancelled")
    else:
        logger.skip("Secrets sync")

    # Check for uncommitted changes
    result = run_cmd(["git", "status", "--porcelain"], cwd=repo_root, halt_on_fail=False)
    if result.stdout.strip():
        logger.warning("You have uncommitted changes:")
        logger.info(result.stdout)
        if not yes and not click.confirm("Continue with deployment?", default=False):
            raise click.ClickException("Deployment cancelled")

    # Optionally build frontend locally (default: let Heroku bun buildpack handle it)
    if local_build:
        if frontend_dir.exists():
            run_cmd(
                ["bun", "run", "build"],
                cwd=frontend_dir,
                label="Building frontend assets locally",
                done_msg="Frontend build complete",
            )

            # Also run collectstatic locally if doing local build
            run_cmd(
                ["python", "manage.py", "collectstatic", "--noinput", "--clear"],
                cwd=repo_root,
                label="Collecting Django static files",
                done_msg="Static files collected",
            )
        else:
            logger.warning(f"Frontend directory not found at {frontend_dir}, skipping build")

    # Get current git commit hash for tracking
    result = run_cmd(["git", "rev-parse", "HEAD"], cwd=repo_root, halt_on_fail=False)
    commit_hash = result.stdout.strip()[:7]

    # Check current branch
    result = run_cmd(["git", "branch", "--show-current"], cwd=repo_root, halt_on_fail=False)
    current_branch = result.stdout.strip()

    logger.info(f"Deploying from branch '{current_branch}' (commit {commit_hash})...")

    # Push to Heroku - stream output in real-time while capturing for analysis
    logger.next(f"Pushing to Heroku ({app})")
    returncode, captured_output = run_streaming(
        ["git", "push", "heroku", f"{current_branch}:main", "--force"],
        cwd=repo_root,
        combine_output=True,
    )

    # Check if anything was actually pushed
    # Git outputs "Everything up-to-date" to stderr when nothing to push
    already_deployed = "Everything up-to-date" in captured_output

    if returncode != 0 and not already_deployed:
        logger.fail("Git push failed")
        raise click.ClickException("Failed to push to Heroku")

    if already_deployed:
        logger.warning(f"Nothing to deploy - commit {commit_hash} is already deployed on Heroku")
        return  # Exit early, no need to run migrations or tag

    logger.done("Code pushed to Heroku")

    # Run migrations
    if not skip_migrate:
        run_cmd(
            ["heroku", "run", "python", "manage.py", "migrate", "--app", app],
            label="Running database migrations on Heroku",
            done_msg="Migrations complete",
        )
    else:
        logger.skip("Database migrations")

    # Tag the deployment
    tag_name = f"deploy-{commit_hash}"
    run_cmd(["git", "tag", "-f", tag_name], cwd=repo_root, halt_on_fail=False)
    run_cmd(["git", "push", "--tags", "--force"], cwd=repo_root, halt_on_fail=False)

    logger.done(f"Deployment successful! (commit: {commit_hash})")
    logger.info(f"App URL: https://{app}.herokuapp.com/")
    logger.tip(f"Logs: heroku logs --tail --app {app}")


@heroku.command("revert")
@click.option(
    "--app",
    default=None,
    help="Heroku app name (default: project_name or parent command).",
)
@click.argument("git_hash", required=False)
@click.option(
    "--skip-migrate",
    is_flag=True,
    help="Skip running database migrations on Heroku.",
)
@click.pass_context
def revert(ctx, app: str | None, git_hash: str | None, skip_migrate: bool):
    """Revert to a previous deployment.

    Pushes a previous git commit to Heroku, effectively rolling back
    your deployment. By default reverts to the previous commit (HEAD~1).

    Confirms before executing the revert. Tags the revert for tracking.

    If --app is not provided, uses project_name from djb config or DJB_PROJECT_NAME
    from Django settings.

    \b
    Examples:
      djb deploy heroku revert               # Revert to previous commit
      djb deploy heroku revert --app myapp   # Explicit app name
      djb deploy heroku revert abc123        # Revert to specific commit
      djb deploy heroku revert --skip-migrate  # Revert without migrations
    """
    # Inherit app from parent command if not explicitly provided
    if app is None and ctx.obj:
        app = ctx.obj.get("app")
    repo_root = Path.cwd()
    config = ctx.obj.get("config") if ctx.obj else None
    app = _get_app_or_fail(app, config)

    # Check if logged into Heroku
    try:
        run_cmd(["heroku", "auth:whoami"], label="Checking Heroku auth", halt_on_fail=True)
    except click.ClickException:
        raise click.ClickException("Not logged into Heroku. Run 'heroku login' first.")

    # Verify we're in a git repository
    if not (repo_root / ".git").exists():
        raise click.ClickException("Not in a git repository")

    # If no git hash provided, use the previous commit
    if git_hash is None:
        result = run_cmd(["git", "rev-parse", "HEAD~1"], cwd=repo_root, halt_on_fail=False)
        if result.returncode != 0:
            raise click.ClickException("Could not determine previous commit")
        assert result.stdout is not None  # For type checker: run_cmd always captures output
        git_hash = result.stdout.strip()
        logger.info(f"No git hash provided, using previous commit: {git_hash[:7]}")

    # Verify the git hash exists
    if not check_cmd(["git", "cat-file", "-t", git_hash], cwd=repo_root):
        raise click.ClickException(f"Git hash '{git_hash}' not found in repository")

    # Get full commit info
    result = run_cmd(["git", "log", "-1", "--oneline", git_hash], cwd=repo_root, halt_on_fail=False)
    commit_info = result.stdout.strip()

    logger.info(f"Reverting to: {commit_info}")
    if not click.confirm("Continue with revert?", default=False):
        raise click.ClickException("Revert cancelled")

    # Push the specified commit to Heroku
    run_cmd(
        ["git", "push", "heroku", f"{git_hash}:main", "--force"],
        label=f"Pushing commit {git_hash[:7]} to Heroku ({app})",
        done_msg="Code pushed to Heroku",
    )

    # Run migrations
    if not skip_migrate:
        run_cmd(
            ["heroku", "run", "python", "manage.py", "migrate", "--app", app],
            label="Running database migrations on Heroku",
            done_msg="Migrations complete",
        )
    else:
        logger.skip("Database migrations")

    # Tag the revert
    short_hash = git_hash[:7]
    tag_name = f"revert-to-{short_hash}"
    run_cmd(["git", "tag", "-f", tag_name], cwd=repo_root, halt_on_fail=False)
    run_cmd(["git", "push", "--tags", "--force"], cwd=repo_root, halt_on_fail=False)

    logger.done(f"Revert successful! (commit: {short_hash})")
    logger.info(f"App URL: https://{app}.herokuapp.com/")
    logger.tip(f"Logs: heroku logs --tail --app {app}")


# Buildpacks required for djb projects (order matters!)
DJB_BUILDPACKS = [
    "https://github.com/heroku/heroku-geo-buildpack.git",  # GDAL for GeoDjango
    "https://github.com/jakeg/heroku-buildpack-bun",  # Bun for frontend
    "heroku/python",  # Python/Django
]


@heroku.command("setup")
@click.option(
    "--app",
    default=None,
    help="Heroku app name (default: project_name or parent command).",
)
@click.option(
    "--skip-buildpacks",
    is_flag=True,
    help="Skip configuring buildpacks.",
)
@click.option(
    "--skip-postgres",
    is_flag=True,
    help="Skip adding Heroku Postgres addon.",
)
@click.option(
    "--skip-remote",
    is_flag=True,
    help="Skip adding heroku git remote.",
)
@click.option(
    "--postgres-plan",
    default="essential-0",
    help="Heroku Postgres plan (default: essential-0, ~$5/month).",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Auto-confirm prompts.",
)
@click.pass_context
def setup(
    ctx,
    app: str | None,
    skip_buildpacks: bool,
    skip_postgres: bool,
    skip_remote: bool,
    postgres_plan: str,
    yes: bool,
):
    """Configure Heroku app for djb deployment.

    Sets up an existing Heroku app with the required buildpacks,
    config vars, and addons for a Django + Bun + GeoDjango project.

    This command is idempotent - safe to run multiple times.
    It will skip configuration that's already in place.

    \b
    Configuration applied:
    • Buildpacks (in order):
      1. heroku-geo-buildpack (GDAL for GeoDjango)
      2. heroku-buildpack-bun (Bun for frontend)
      3. heroku/python (Python/Django)
    • Config vars: DEBUG=False
    • Git remote: heroku -> https://git.heroku.com/<app>.git
    • Addon: heroku-postgresql (optional)

    \b
    Examples:
      djb deploy heroku setup --app myapp   # Setup new app
      djb deploy heroku setup               # Use project_name from djb config
      djb deploy heroku setup --skip-postgres  # Skip database addon
      djb deploy heroku setup -y            # Auto-confirm all prompts
    """
    repo_root = Path.cwd()

    # Inherit app and yes from parent command if not explicitly provided
    if app is None and ctx.obj:
        app = ctx.obj.get("app")
    if not yes and ctx.obj:
        yes = ctx.obj.get("yes", False)

    config = ctx.obj.get("config") if ctx.obj else None
    app = _get_app_or_fail(app, config)

    logger.info(f"Setting up Heroku app: {app}")

    # Check if logged into Heroku
    try:
        run_cmd(["heroku", "auth:whoami"], label="Checking Heroku auth", halt_on_fail=True)
    except click.ClickException:
        raise click.ClickException("Not logged into Heroku. Run 'heroku login' first.")

    # Verify the app exists
    result = run_cmd(
        ["heroku", "apps:info", "--app", app],
        halt_on_fail=False,
        label=f"Verifying app '{app}' exists",
    )
    if result.returncode != 0:
        raise click.ClickException(
            f"App '{app}' not found. Create it first with: heroku create {app}"
        )
    logger.done(f"App '{app}' found")

    # Configure buildpacks
    if not skip_buildpacks:
        logger.next("Configuring buildpacks")

        # Get current buildpacks
        result = run_cmd(
            ["heroku", "buildpacks", "--app", app],
            halt_on_fail=False,
        )
        current_buildpacks = result.stdout.strip()

        # Check if buildpacks are already configured correctly
        all_present = all(bp in current_buildpacks for bp in DJB_BUILDPACKS)
        if all_present:
            logger.done("Buildpacks already configured correctly")
        else:
            # Clear and set buildpacks in order
            logger.info("Setting buildpacks (order matters for Heroku):")
            for i, buildpack in enumerate(DJB_BUILDPACKS, 1):
                logger.info(f"  {i}. {buildpack}")

            if not yes and not click.confirm("Apply this buildpack configuration?", default=True):
                logger.skip("Buildpack configuration")
            else:
                # Clear existing buildpacks
                run_cmd(
                    ["heroku", "buildpacks:clear", "--app", app],
                    halt_on_fail=False,
                )

                # Add buildpacks in order
                for buildpack in DJB_BUILDPACKS:
                    run_cmd(
                        ["heroku", "buildpacks:add", buildpack, "--app", app],
                        halt_on_fail=False,
                    )

                logger.done("Buildpacks configured")
    else:
        logger.skip("Buildpack configuration")

    # Set DEBUG=False
    logger.next("Setting config vars")
    result = run_cmd(
        ["heroku", "config:get", "DEBUG", "--app", app],
        halt_on_fail=False,
    )
    current_debug = result.stdout.strip()

    if current_debug == "False":
        logger.done("DEBUG=False already set")
    else:
        run_cmd(
            ["heroku", "config:set", "DEBUG=False", "--app", app],
            halt_on_fail=False,
        )
        logger.done("DEBUG=False set")

    # Add Heroku Postgres addon
    if not skip_postgres:
        logger.next("Checking Heroku Postgres addon")

        result = run_cmd(
            ["heroku", "addons", "--app", app],
            halt_on_fail=False,
        )
        has_postgres = "heroku-postgresql" in result.stdout

        if has_postgres:
            logger.done("Heroku Postgres already attached")
        else:
            logger.info(f"Heroku Postgres not found. Plan: {postgres_plan}")
            if not yes and not click.confirm(
                f"Add heroku-postgresql:{postgres_plan} addon?", default=True
            ):
                logger.skip("Postgres addon")
            else:
                run_cmd(
                    ["heroku", "addons:create", f"heroku-postgresql:{postgres_plan}", "--app", app],
                    label="Adding Heroku Postgres",
                    done_msg=f"Heroku Postgres ({postgres_plan}) added",
                )
    else:
        logger.skip("Postgres addon")

    # Set up git remote
    if not skip_remote:
        logger.next("Configuring git remote")

        # Check if heroku remote exists
        result = run_cmd(
            ["git", "remote", "get-url", "heroku"],
            cwd=repo_root,
            halt_on_fail=False,
        )

        expected_url = f"https://git.heroku.com/{app}.git"

        if result.returncode == 0:
            current_url = result.stdout.strip()
            if current_url == expected_url:
                logger.done(f"Git remote 'heroku' already configured")
            else:
                # Update existing remote
                run_cmd(
                    ["git", "remote", "set-url", "heroku", expected_url],
                    cwd=repo_root,
                    halt_on_fail=False,
                )
                logger.done(f"Updated git remote 'heroku' -> {expected_url}")
        else:
            # Add new remote
            run_cmd(
                ["git", "remote", "add", "heroku", expected_url],
                cwd=repo_root,
                halt_on_fail=False,
            )
            logger.done(f"Added git remote 'heroku' -> {expected_url}")
    else:
        logger.skip("Git remote configuration")

    logger.note()
    logger.done("Heroku setup complete!")
    logger.note()
    logger.info("Next steps:")
    logger.info("  1. Configure secrets: djb secrets edit production")
    logger.info(f"  2. Deploy: djb deploy heroku")
    logger.tip(f"View app config: heroku config --app {app}")
