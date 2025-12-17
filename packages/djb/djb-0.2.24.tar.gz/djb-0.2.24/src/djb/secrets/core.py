"""
Core secrets management using SOPS.

This module provides encrypted secrets storage compatible with Kubernetes
and cloud deployments, using SOPS with age encryption.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from djb.project import find_project_root

if TYPE_CHECKING:
    from djb.types import Mode


# Bech32 character set for age public key validation (excludes 1, b, i, o)
BECH32_CHARS = frozenset("023456789acdefghjklmnpqrstuvwxyz")


class SopsError(Exception):
    """Error from SOPS command."""


def check_sops_installed() -> bool:
    """Check if SOPS is installed and available."""
    return shutil.which("sops") is not None


def check_age_installed() -> bool:
    """Check if age is installed and available."""
    return shutil.which("age-keygen") is not None


def get_default_key_path(project_root: Path | None = None) -> Path:
    """Get default path for age key file.

    The key is stored in the project root (.age/keys.txt) rather than the
    home directory, so each project has its own key.

    Args:
        project_root: Project root directory. Defaults to detected project root
                     (searches for pyproject.toml with djb dependency).

    Returns:
        Path to the age key file (.age/keys.txt in project root).
    """
    if project_root is None:
        project_root = find_project_root(fallback_to_cwd=True)
    return project_root / ".age" / "keys.txt"


def get_default_secrets_dir(project_root: Path | None = None) -> Path:
    """Get default path for secrets directory.

    Args:
        project_root: Project root directory. Defaults to current working directory.

    Returns:
        Path to the secrets directory (secrets/ in project root).
    """
    if project_root is None:
        project_root = Path.cwd()
    return project_root / "secrets"


def generate_age_key(key_path: Path | None = None) -> tuple[str, str]:
    """Generate a new age key pair using age-keygen.

    Args:
        key_path: Path to save the private key (defaults to .age/keys.txt in project root)

    Returns:
        Tuple of (public_key, private_key)
    """
    if key_path is None:
        key_path = get_default_key_path()

    # Generate key using age-keygen
    result = subprocess.run(
        ["age-keygen"],
        capture_output=True,
        text=True,
        check=True,
    )

    # Parse output - age-keygen outputs:
    # # created: 2024-01-01T00:00:00Z
    # # public key: age1...
    # AGE-SECRET-KEY-...
    lines = result.stdout.strip().split("\n")
    public_key = None
    private_key = None

    for line in lines:
        if line.startswith("# public key: "):
            public_key = line.replace("# public key: ", "").strip()
        elif line.startswith("AGE-SECRET-KEY-"):
            private_key = line.strip()

    if not public_key or not private_key:
        raise SopsError(f"Failed to parse age-keygen output: {result.stdout}")

    # Save private key to file
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text(result.stdout)
    key_path.chmod(0o600)

    return public_key, private_key


def is_valid_age_public_key(key: str) -> bool:
    """Check if a string is a valid age public key.

    Age public keys:
    - Start with "age1"
    - Are 62 characters long (Bech32 encoding)
    - Contain only lowercase letters and digits (no 1, b, i, o to avoid confusion)

    Args:
        key: String to validate

    Returns:
        True if the key appears to be a valid age public key
    """
    if not key.startswith("age1"):
        return False

    if len(key) != 62:
        return False

    # Check characters after "age1" prefix
    for char in key[4:]:
        if char not in BECH32_CHARS:
            return False

    return True


def get_public_key_from_private(key_path: Path | None = None) -> str:
    """Extract public key from a private key file.

    Args:
        key_path: Path to the private key file

    Returns:
        The public key string
    """
    if key_path is None:
        key_path = get_default_key_path()

    if not key_path.exists():
        raise FileNotFoundError(f"Key file not found: {key_path}")

    content = key_path.read_text()

    # Look for public key in comments
    for line in content.split("\n"):
        if line.startswith("# public key: "):
            return line.replace("# public key: ", "").strip()

    # If no comment, derive from private key using age-keygen -y
    # Find the private key line
    for line in content.split("\n"):
        if line.startswith("AGE-SECRET-KEY-"):
            result = subprocess.run(
                ["age-keygen", "-y"],
                input=line,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            raise SopsError(f"Failed to derive public key: {result.stderr}")

    raise SopsError("No valid age key found in file")


def format_identity(name: str | None, email: str) -> str:
    """Format name and email into git-style identity string.

    Args:
        name: User's name (optional)
        email: User's email

    Returns:
        Identity string in format "Name <email>" or just "email" if no name.
    """
    if name:
        return f"{name} <{email}>"
    return email


def parse_identity(identity: str) -> tuple[str | None, str]:
    """Parse git-style identity string into name and email.

    Args:
        identity: Identity string like "Name <email>" or just "email"

    Returns:
        Tuple of (name, email). Name may be None for legacy format.
    """
    # Try git-style format: "Name <email>"
    match = re.match(r"^(.+?)\s*<([^>]+)>$", identity)
    if match:
        return match.group(1).strip(), match.group(2).strip()

    # Legacy format: just email
    return None, identity


# Placeholder pattern used in secrets templates (case-insensitive substring match)
PLACEHOLDER_PATTERN = "CHANGE-ME"


def is_placeholder_value(value: str) -> bool:
    """Check if a secret value is a placeholder that needs to be changed.

    Args:
        value: The secret value to check.

    Returns:
        True if the value contains CHANGE-ME (case-insensitive).
    """
    if not isinstance(value, str):
        return False

    return PLACEHOLDER_PATTERN.upper() in value.upper()


def find_placeholder_secrets(secrets: dict[str, Any], prefix: str = "") -> list[str]:
    """Find all secrets that have placeholder values.

    Args:
        secrets: Dictionary of secrets (can be nested).
        prefix: Key prefix for nested keys (used internally).

    Returns:
        List of key paths that have placeholder values (e.g., "api_keys.stripe").
    """
    placeholders = []

    for key, value in secrets.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            # Recurse into nested dicts
            placeholders.extend(find_placeholder_secrets(value, full_key))
        elif isinstance(value, str) and is_placeholder_value(value):
            placeholders.append(full_key)

    return placeholders


def create_sops_config(
    secrets_dir: Path,
    recipients: dict[str, str] | list[str],
) -> Path:
    """Create or update .sops.yaml configuration with identity comments.

    Args:
        secrets_dir: Directory containing secrets files
        recipients: Either a dict mapping public_key -> identity, or a list of keys.
                   Identity should be git-style: "Name <email>" or just "email".

    Returns:
        Path to the .sops.yaml file
    """
    sops_config_path = secrets_dir / ".sops.yaml"

    # Normalize to dict
    if isinstance(recipients, list):
        recipients = {key: "" for key in recipients}

    # Write manually to include comments
    lines = [
        "creation_rules:",
        "  - path_regex: '.*\\.yaml$'",
        "    key_groups:",
        "      - age:",
    ]

    for key, identity in recipients.items():
        if identity:
            lines.append(f"          # {identity}")
        lines.append(f"          - {key}")

    with open(sops_config_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return sops_config_path


def parse_sops_config(secrets_dir: Path) -> dict[str, str]:
    """Parse .sops.yaml and extract public keys with their identity comments.

    Returns:
        Dict mapping public_key -> identity (identity may be empty string).
        Identity format is "Name <email>" or just "email" for legacy configs.
    """
    sops_config_path = secrets_dir / ".sops.yaml"

    if not sops_config_path.exists():
        return {}

    content = sops_config_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    recipients: dict[str, str] = {}
    current_identity = ""

    for line in lines:
        stripped = line.strip()
        # Look for identity comments (# Name <email> or # email@example.com)
        if stripped.startswith("# ") and "@" in stripped:
            current_identity = stripped[2:].strip()
        # Look for age public keys (- age1...)
        elif stripped.startswith("- age1"):
            key = stripped[2:].strip()
            recipients[key] = current_identity
            current_identity = ""
        # Reset identity if we hit something else
        elif stripped and not stripped.startswith("#"):
            current_identity = ""

    return recipients


def get_all_recipients(secrets_dir: Path) -> list[str]:
    """Get all public keys from .sops.yaml.

    Returns:
        List of public key strings
    """
    return list(parse_sops_config(secrets_dir).keys())


def encrypt_file(
    input_path: Path,
    output_path: Path | None = None,
    public_keys: list[str] | None = None,
    sops_config: Path | None = None,
) -> None:
    """Encrypt a YAML file using SOPS.

    Args:
        input_path: Path to plaintext YAML file
        output_path: Path for encrypted output (defaults to input_path)
        public_keys: Age public keys to encrypt for (overrides sops config)
        sops_config: Path to .sops.yaml config file
    """
    if output_path is None:
        output_path = input_path

    cmd = ["sops", "--encrypt"]

    if public_keys:
        cmd.extend(["--age", ",".join(public_keys)])

    if sops_config:
        cmd.extend(["--config", str(sops_config)])

    cmd.extend(["--output", str(output_path), str(input_path)])

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise SopsError(f"SOPS encryption failed: {result.stderr}")


def decrypt_file(
    input_path: Path,
    output_path: Path | None = None,
    key_path: Path | None = None,
) -> str:
    """Decrypt a SOPS-encrypted YAML file.

    Args:
        input_path: Path to encrypted YAML file
        output_path: Path for decrypted output (if None, returns content)
        key_path: Path to age private key file

    Returns:
        Decrypted content as string (if output_path is None)
    """
    env = os.environ.copy()
    if key_path:
        env["SOPS_AGE_KEY_FILE"] = str(key_path)

    cmd = ["sops", "--decrypt"]

    if output_path:
        cmd.extend(["--output", str(output_path)])

    cmd.append(str(input_path))

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)

    if result.returncode != 0:
        raise SopsError(f"SOPS decryption failed: {result.stderr}")

    return result.stdout


def rotate_keys(
    input_path: Path,
    public_keys: list[str],
    key_path: Path | None = None,
) -> None:
    """Re-encrypt a file with new recipients.

    This decrypts the file and re-encrypts it with the new set of public keys.

    Args:
        input_path: Path to encrypted YAML file
        public_keys: New list of age public keys to encrypt for
        key_path: Path to age private key file for decryption
    """
    env = os.environ.copy()
    if key_path:
        env["SOPS_AGE_KEY_FILE"] = str(key_path)

    # Use sops updatekeys to rotate recipients
    cmd = [
        "sops",
        "updatekeys",
        "--age",
        ",".join(public_keys),
        "--yes",
        str(input_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)

    if result.returncode != 0:
        raise SopsError(f"SOPS key rotation failed: {result.stderr}")


class SecretsManager:
    """Manages encrypted secrets for different environments using SOPS."""

    def __init__(
        self,
        secrets_dir: Path,
        key_path: Path | None = None,
    ):
        """
        Initialize secrets manager.

        Args:
            secrets_dir: Directory containing encrypted secret files
            key_path: Path to age private key file for decryption
        """
        self.secrets_dir = Path(secrets_dir)
        self.key_path = key_path or get_default_key_path()

    def load_secrets(self, environment: str) -> dict[str, Any]:
        """
        Load and decrypt secrets for a given environment.

        Args:
            environment: Environment name (dev, staging, production)

        Returns:
            Dictionary of decrypted secrets
        """
        secrets_file = self.secrets_dir / f"{environment}.yaml"
        if not secrets_file.exists():
            raise FileNotFoundError(f"Secrets file not found: {secrets_file}")

        decrypted = decrypt_file(secrets_file, key_path=self.key_path)
        return yaml.safe_load(decrypted)

    def save_secrets(
        self,
        environment: str,
        secrets: dict[str, Any],
        public_keys: list[str],
    ) -> None:
        """
        Save and encrypt secrets for a given environment.

        Args:
            environment: Environment name (dev, staging, production)
            secrets: Dictionary of secrets to save
            public_keys: List of age public keys to encrypt for
        """
        self.secrets_dir.mkdir(parents=True, exist_ok=True)

        secrets_file = self.secrets_dir / f"{environment}.yaml"
        temp_file = self.secrets_dir / f".{environment}.tmp.yaml"

        try:
            # Write plaintext to temp file
            with open(temp_file, "w", encoding="utf-8") as f:
                yaml.dump(secrets, f, default_flow_style=False, sort_keys=False)

            # Encrypt to final location
            encrypt_file(temp_file, secrets_file, public_keys=public_keys)
        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()

    def rotate_keys(
        self,
        environment: str,
        public_keys: list[str],
    ) -> None:
        """
        Re-encrypt secrets with new set of public keys.

        Args:
            environment: Environment name
            public_keys: New list of age public keys to encrypt for
        """
        secrets_file = self.secrets_dir / f"{environment}.yaml"
        if not secrets_file.exists():
            raise FileNotFoundError(f"Secrets file not found: {secrets_file}")

        rotate_keys(secrets_file, public_keys, self.key_path)


def load_secrets(
    environment: str = "dev",
    secrets_dir: Path | None = None,
    key_path: Path | None = None,
) -> dict[str, Any]:
    """
    Convenience function to load and decrypt secrets.

    Args:
        environment: Environment name (dev, staging, production)
        secrets_dir: Directory containing secrets (defaults to ./secrets)
        key_path: Path to age key file (defaults to ~/.age/keys.txt)

    Returns:
        Dictionary of decrypted secrets
    """
    if secrets_dir is None:
        secrets_dir = get_default_secrets_dir()

    if key_path is None:
        key_path = get_default_key_path()

    if not key_path.exists():
        raise FileNotFoundError(
            f"Age key file not found: {key_path}. " f"Generate one with: djb secrets init"
        )

    manager = SecretsManager(secrets_dir=secrets_dir, key_path=key_path)
    return manager.load_secrets(environment)


def load_secrets_for_mode(
    mode: "Mode",
    secrets_dir: Path | None = None,
    key_path: Path | None = None,
) -> dict[str, Any]:
    """
    Load secrets for a deployment mode.

    This is a convenience wrapper around load_secrets() that maps
    Mode to the corresponding secrets environment:
    - Mode.DEVELOPMENT → dev.yaml
    - Mode.STAGING → staging.yaml
    - Mode.PRODUCTION → production.yaml

    Args:
        mode: Deployment mode (from djb.types.Mode)
        secrets_dir: Directory containing secrets (defaults to ./secrets)
        key_path: Path to age key file (defaults to ~/.age/keys.txt)

    Returns:
        Dictionary of decrypted secrets

    Example:
        >>> from djb.types import Mode
        >>> secrets = load_secrets_for_mode(Mode.PRODUCTION)
    """
    return load_secrets(
        environment=mode.secrets_env,
        secrets_dir=secrets_dir,
        key_path=key_path,
    )
