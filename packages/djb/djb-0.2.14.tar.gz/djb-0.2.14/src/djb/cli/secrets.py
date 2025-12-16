"""
djb secrets CLI - Manage encrypted secrets.

Provides commands for initializing, editing, and managing encrypted secrets.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import click
import yaml

from djb.secrets import AgeKey, SecretsManager, get_default_key_path


def _get_template(env: str) -> dict:
    """Get the secrets template for an environment."""
    if env == "heroku_prod":
        return {
            "django_secret_key": f"CHANGE-ME-{env.upper()}-KEY",
            "superuser": {
                "username": "admin",
                "email": "admin@example.com",
                "password": f"CHANGE-ME-{env.upper()}-PASSWORD",
            },
        }
    else:
        return {
            "django_secret_key": f"CHANGE-ME-{env.upper()}-KEY",
            "db_credentials": {
                "username": "beachresort25",
                "password": f"CHANGE-ME-{env.upper()}-PASSWORD",
                "database": "beachresort25",
                "host": "localhost",
                "port": 5432,
            },
            "superuser": {
                "username": "admin",
                "email": "admin@example.com",
                "password": f"CHANGE-ME-{env.upper()}-PASSWORD",
            },
        }


def _deep_merge_missing(existing: dict, template: dict) -> tuple[dict, list[str]]:
    """Merge template keys into existing dict, only adding missing keys.

    Returns the merged dict and a list of keys that were added.
    """
    result = dict(existing)
    added = []

    for key, value in template.items():
        if key not in result:
            result[key] = value
            added.append(key)
        elif isinstance(value, dict) and isinstance(result.get(key), dict):
            # Recursively merge nested dicts
            nested_result, nested_added = _deep_merge_missing(result[key], value)
            result[key] = nested_result
            added.extend(f"{key}.{k}" for k in nested_added)

    return result, added


@click.group()
def secrets():
    """Manage encrypted secrets for different environments."""
    pass


@secrets.command("init")
@click.option(
    "--key-path",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to store age key (default: ~/.age/keys.txt)",
)
@click.option(
    "--secrets-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for secrets files (default: ./secrets)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing key file if it exists",
)
def init(key_path: Path | None, secrets_dir: Path | None, force: bool):
    """Initialize secrets management for this project.

    Sets up Age-encrypted secrets management:

    \b
    • Generates an age encryption key (~/.age/keys.txt)
    • Creates encrypted secrets files for dev/staging/production
    • Sets up .gitignore to protect decrypted files
    • Displays your public key for sharing with team members

    Safe to run if key already exists - you'll be prompted to reuse it.

    \b
    Examples:
      djb secrets init                  # Standard setup
      djb secrets init --force          # Regenerate key
      djb secrets init --key-path ./my.key  # Custom key location
    """
    if key_path is None:
        key_path = get_default_key_path()

    if secrets_dir is None:
        secrets_dir = Path.cwd() / "secrets"

    # Check if key already exists
    if key_path.exists() and not force:
        click.secho(f"Age key already exists at {key_path}", fg="yellow")
        if not click.confirm("Do you want to use the existing key?"):
            click.echo("Aborted.")
            return
        age_key = AgeKey.from_private_string(key_path.read_text().strip())
    else:
        # Generate new age key
        age_key = AgeKey.generate()

        # Save private key
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_text(age_key.to_private_string())
        key_path.chmod(0o600)  # Secure permissions

        click.secho(f"✓ Generated age key at {key_path}", fg="green")

    # Display public key
    public_key = age_key.to_public_string()
    click.echo(f"\nYour public key (share with team members):")
    click.secho(f"  {public_key}", fg="cyan", bold=True)

    # Create secrets directory
    secrets_dir.mkdir(parents=True, exist_ok=True)

    # Create .gitignore for secrets directory
    gitignore_path = secrets_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(
            "# Decrypted secrets (never commit these)\n"
            "*.decrypted.yaml\n"
            "*.plaintext.yaml\n"
            "*.secret\n"
        )

    # Create template secrets files for each environment
    manager = SecretsManager(secrets_dir=secrets_dir, age_key=age_key)

    for env in ["dev", "staging", "heroku_prod"]:
        secrets_file = secrets_dir / f"{env}.yaml"
        if not secrets_file.exists():
            template = _get_template(env)
            manager.save_secrets(env, template, [public_key], encrypt=True)
            click.secho(f"✓ Created {env}.yaml", fg="green")

    click.echo(f"\n✓ Secrets management initialized in {secrets_dir}")
    click.echo(f"\nNext steps:")
    click.echo(f"  1. Edit your secrets: djb secrets edit dev")
    click.echo(f"  2. Add secrets to git: git add {secrets_dir}/*.yaml")
    click.echo(f"  3. Keep your key safe: backup {key_path}")


@secrets.command("edit")
@click.argument("environment", type=click.Choice(["dev", "staging", "heroku_prod"]))
@click.option(
    "--key-path",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to age key file",
)
@click.option(
    "--secrets-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory containing secrets files",
)
@click.option(
    "--editor",
    default=None,
    help="Editor to use (default: $EDITOR or vim)",
)
def edit(
    environment: str,
    key_path: Path | None,
    secrets_dir: Path | None,
    editor: str | None,
):
    """Edit secrets for an environment.

    Decrypts the secrets file, opens it in your editor ($EDITOR or vim),
    then automatically re-encrypts when you save and close.

    Creates a new secrets file if the environment doesn't exist yet.

    \b
    Examples:
      djb secrets edit dev              # Edit dev secrets
      djb secrets edit heroku_prod      # Edit Heroku production secrets
      djb secrets edit dev --editor nano  # Use specific editor
    """
    if key_path is None:
        key_path = get_default_key_path()

    if secrets_dir is None:
        secrets_dir = Path.cwd() / "secrets"

    if not key_path.exists():
        click.secho(f"Age key not found at {key_path}", fg="red")
        click.echo("Run 'djb secrets init' first.")
        sys.exit(1)

    # Load manager
    age_key = AgeKey.from_private_string(key_path.read_text().strip())
    manager = SecretsManager(secrets_dir=secrets_dir, age_key=age_key)

    # Get public key for re-encryption
    public_key = age_key.to_public_string()

    # Load and decrypt secrets
    try:
        secrets_data = manager.load_secrets(environment, decrypt=True)
    except FileNotFoundError:
        click.secho(f"Secrets file for '{environment}' not found.", fg="yellow")
        if click.confirm("Create new secrets file?"):
            secrets_data = _get_template(environment)
        else:
            sys.exit(1)

    # Create temporary file for editing
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=f".{environment}.yaml", delete=False
    ) as tf:
        temp_path = Path(tf.name)
        yaml.dump(secrets_data, tf, default_flow_style=False, sort_keys=False)

    try:
        # Get editor
        if editor is None:
            editor = os.environ.get("EDITOR", "vim")

        # Open in editor
        subprocess.run([editor, str(temp_path)], check=True)

        # Read edited secrets
        with open(temp_path, "r") as f:
            edited_secrets = yaml.safe_load(f)

        # Check if changed
        if edited_secrets != secrets_data:
            # Re-encrypt and save
            manager.save_secrets(environment, edited_secrets, [public_key], encrypt=True)
            click.secho(f"✓ Encrypted and saved secrets for {environment}", fg="green")
        else:
            click.echo("No changes made.")

    finally:
        # Clean up temp file
        temp_path.unlink()


@secrets.command("view")
@click.argument("environment", type=click.Choice(["dev", "staging", "heroku_prod"]))
@click.option(
    "--key-path",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to age key file",
)
@click.option(
    "--secrets-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory containing secrets files",
)
@click.option(
    "--key",
    "secret_key",
    default=None,
    help="Show only this specific key",
)
def view(
    environment: str,
    key_path: Path | None,
    secrets_dir: Path | None,
    secret_key: str | None,
):
    """View decrypted secrets without editing.

    Displays secrets in plaintext - use carefully in secure environments only.

    \b
    Examples:
      djb secrets view dev              # View all dev secrets
      djb secrets view prod --key django_secret_key  # View one key
    """
    if key_path is None:
        key_path = get_default_key_path()

    if secrets_dir is None:
        secrets_dir = Path.cwd() / "secrets"

    if not key_path.exists():
        click.secho(f"Age key not found at {key_path}", fg="red")
        sys.exit(1)

    # Load and decrypt
    age_key = AgeKey.from_private_string(key_path.read_text().strip())
    manager = SecretsManager(secrets_dir=secrets_dir, age_key=age_key)
    secrets_data = manager.load_secrets(environment, decrypt=True)

    if secret_key:
        # Show specific key
        if secret_key in secrets_data:
            click.echo(f"{secret_key}: {secrets_data[secret_key]}")
        else:
            click.secho(f"Key '{secret_key}' not found", fg="red")
            sys.exit(1)
    else:
        # Show all secrets
        click.echo(f"Secrets for {environment}:")
        click.echo(yaml.dump(secrets_data, default_flow_style=False, sort_keys=False))


@secrets.command("list")
@click.option(
    "--secrets-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory containing secrets files",
)
def list_environments(secrets_dir: Path | None):
    """List available secret environments.

    Shows all encrypted secrets files in the secrets directory.

    \b
    Example:
      djb secrets list
    """
    if secrets_dir is None:
        secrets_dir = Path.cwd() / "secrets"

    if not secrets_dir.exists():
        click.secho("No secrets directory found.", fg="yellow")
        click.echo("Run 'djb secrets init' to get started.")
        return

    # Find all .yaml files
    secret_files = sorted(secrets_dir.glob("*.yaml"))

    if not secret_files:
        click.secho("No secret files found.", fg="yellow")
        return

    click.echo("Available environments:")
    for file in secret_files:
        env_name = file.stem
        click.echo(f"  • {env_name}")


@secrets.command("generate-key")
def generate_key():
    """Generate a new random Django secret key.

    Creates a cryptographically secure 50-character secret key
    suitable for Django's SECRET_KEY setting.

    \b
    Example:
      djb secrets generate-key
    """
    import secrets as py_secrets
    import string

    chars = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    secret_key = "".join(py_secrets.choice(chars) for _ in range(50))

    click.echo("Generated Django secret key:")
    click.secho(secret_key, fg="green", bold=True)
    click.echo("\nAdd this to your secrets file with:")
    click.echo("  djb secrets edit <environment>")


@secrets.command("upgrade")
@click.argument(
    "environment",
    type=click.Choice(["dev", "staging", "heroku_prod"]),
    required=False,
)
@click.option(
    "--key-path",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to age key file",
)
@click.option(
    "--secrets-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory containing secrets files",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be added without making changes",
)
@click.option(
    "--all",
    "all_envs",
    is_flag=True,
    help="Upgrade all environments",
)
def upgrade(
    environment: str | None,
    key_path: Path | None,
    secrets_dir: Path | None,
    dry_run: bool,
    all_envs: bool,
):
    """Add missing secrets from template to existing secrets files.

    Upgrades secrets files by adding any new keys from the template while
    preserving existing values. Useful when djb adds new secret fields.

    \b
    Examples:
      djb secrets upgrade dev             # Upgrade dev secrets
      djb secrets upgrade --all           # Upgrade all environments
      djb secrets upgrade dev --dry-run   # Preview changes
    """
    if key_path is None:
        key_path = get_default_key_path()

    if secrets_dir is None:
        secrets_dir = Path.cwd() / "secrets"

    if not key_path.exists():
        click.secho(f"Age key not found at {key_path}", fg="red")
        click.echo("Run 'djb secrets init' first.")
        sys.exit(1)

    if not environment and not all_envs:
        click.secho("Specify an environment or use --all", fg="red")
        sys.exit(1)

    # Load manager
    age_key = AgeKey.from_private_string(key_path.read_text().strip())
    manager = SecretsManager(secrets_dir=secrets_dir, age_key=age_key)
    public_key = age_key.to_public_string()

    # Determine which environments to upgrade
    if all_envs:
        environments = ["dev", "staging", "heroku_prod"]
    else:
        environments = [environment]

    for env in environments:
        secrets_file = secrets_dir / f"{env}.yaml"
        if not secrets_file.exists():
            click.secho(f"Skipping {env}: secrets file not found", fg="yellow")
            continue

        # Load existing secrets
        try:
            existing = manager.load_secrets(env, decrypt=True)
        except Exception as e:
            click.secho(f"Skipping {env}: failed to load ({e})", fg="red")
            continue

        # Get template and merge
        template = _get_template(env)
        merged, added = _deep_merge_missing(existing, template)

        if not added:
            click.echo(f"{env}: already up to date")
            continue

        if dry_run:
            click.secho(f"{env}: would add {len(added)} key(s):", fg="yellow")
            for key in added:
                click.echo(f"  + {key}")
        else:
            manager.save_secrets(env, merged, [public_key], encrypt=True)
            click.secho(f"{env}: added {len(added)} key(s):", fg="green")
            for key in added:
                click.echo(f"  + {key}")
