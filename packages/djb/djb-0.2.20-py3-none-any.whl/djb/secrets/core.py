"""
Core secrets management using age-style encryption.

This module provides encrypted secrets storage compatible with Kubernetes
and cloud deployments, using modern cryptography (X25519, ChaCha20-Poly1305).
"""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


@dataclass
class AgeKey:
    """Represents an age encryption key pair."""

    private_key: X25519PrivateKey
    public_key: X25519PublicKey

    @classmethod
    def generate(cls) -> AgeKey:
        """Generate a new age key pair."""
        private_key = X25519PrivateKey.generate()
        public_key = private_key.public_key()
        return cls(private_key=private_key, public_key=public_key)

    @classmethod
    def from_private_string(cls, key_string: str) -> AgeKey:
        """Load from age private key string format."""
        # Remove age prefix if present
        if key_string.startswith("AGE-SECRET-KEY-"):
            key_string = key_string[15:]

        # Decode base64
        key_bytes = base64.b64decode(key_string)
        private_key = X25519PrivateKey.from_private_bytes(key_bytes)
        public_key = private_key.public_key()
        return cls(private_key=private_key, public_key=public_key)

    def to_private_string(self) -> str:
        """Export as age private key string format."""
        key_bytes = self.private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        encoded = base64.b64encode(key_bytes).decode("ascii")
        return f"AGE-SECRET-KEY-{encoded}"

    def to_public_string(self) -> str:
        """Export as age public key string format."""
        key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
        )
        encoded = base64.b64encode(key_bytes).decode("ascii")
        return f"age{encoded}"


class SecretsManager:
    """Manages encrypted secrets for different environments."""

    def __init__(self, secrets_dir: Path, age_key: AgeKey | None = None):
        """
        Initialize secrets manager.

        Args:
            secrets_dir: Directory containing encrypted secret files
            age_key: Age key for encryption/decryption (optional for reading only)
        """
        self.secrets_dir = Path(secrets_dir)
        self.age_key = age_key

    @classmethod
    def from_key_file(cls, secrets_dir: Path, key_file: Path) -> SecretsManager:
        """
        Create manager from an age key file.

        Args:
            secrets_dir: Directory containing encrypted secret files
            key_file: Path to file containing age private key
        """
        key_string = key_file.read_text().strip()
        age_key = AgeKey.from_private_string(key_string)
        return cls(secrets_dir=secrets_dir, age_key=age_key)

    def encrypt_value(self, value: str, recipient_public_key: str) -> str:
        """
        Encrypt a single value.

        Args:
            value: Plaintext value to encrypt
            recipient_public_key: Age public key of recipient

        Returns:
            Base64-encoded encrypted value
        """
        # Remove age prefix if present
        if recipient_public_key.startswith("age"):
            recipient_public_key = recipient_public_key[3:]

        # Decode recipient public key
        recipient_bytes = base64.b64decode(recipient_public_key)
        recipient_key = X25519PublicKey.from_public_bytes(recipient_bytes)

        # Generate ephemeral key for this encryption
        ephemeral_key = X25519PrivateKey.generate()

        # Perform X25519 key exchange
        shared_secret = ephemeral_key.exchange(recipient_key)

        # Derive encryption key using HKDF
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"age-encryption.org/v1/X25519",
        ).derive(shared_secret)

        # Encrypt value
        cipher = ChaCha20Poly1305(derived_key)
        nonce = os.urandom(12)
        ciphertext = cipher.encrypt(nonce, value.encode("utf-8"), None)

        # Get ephemeral public key bytes
        ephemeral_public_bytes = ephemeral_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
        )

        # Combine: ephemeral_public_key || nonce || ciphertext
        combined = ephemeral_public_bytes + nonce + ciphertext

        # Return base64-encoded result
        return base64.b64encode(combined).decode("ascii")

    def decrypt_value(self, encrypted_value: str) -> str:
        """
        Decrypt a single value.

        Args:
            encrypted_value: Base64-encoded encrypted value

        Returns:
            Decrypted plaintext value
        """
        if not self.age_key:
            raise ValueError("Cannot decrypt without an age key")

        # Decode base64
        combined = base64.b64decode(encrypted_value)

        # Split: ephemeral_public_key (32) || nonce (12) || ciphertext
        ephemeral_public_bytes = combined[:32]
        nonce = combined[32:44]
        ciphertext = combined[44:]

        # Reconstruct ephemeral public key
        ephemeral_public_key = X25519PublicKey.from_public_bytes(ephemeral_public_bytes)

        # Perform X25519 key exchange
        shared_secret = self.age_key.private_key.exchange(ephemeral_public_key)

        # Derive decryption key
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"age-encryption.org/v1/X25519",
        ).derive(shared_secret)

        # Decrypt
        cipher = ChaCha20Poly1305(derived_key)
        plaintext = cipher.decrypt(nonce, ciphertext, None)

        return plaintext.decode("utf-8")

    def encrypt_dict(
        self, data: dict[str, Any], recipient_public_keys: list[str]
    ) -> dict[str, Any]:
        """
        Encrypt all string values in a dictionary (recursively).

        Args:
            data: Dictionary with plaintext values
            recipient_public_keys: List of age public keys to encrypt for

        Returns:
            Dictionary with encrypted values
        """
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self.encrypt_dict(value, recipient_public_keys)
            elif isinstance(value, str):
                # For multiple recipients, we encrypt for the first one
                # (in a full implementation, we'd store separate encrypted copies)
                result[key] = self.encrypt_value(value, recipient_public_keys[0])
            else:
                result[key] = value
        return result

    def decrypt_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Decrypt all encrypted values in a dictionary (recursively).

        Args:
            data: Dictionary with encrypted values

        Returns:
            Dictionary with decrypted plaintext values
        """
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self.decrypt_dict(value)
            elif isinstance(value, str) and len(value) > 50:  # Likely encrypted
                try:
                    result[key] = self.decrypt_value(value)
                except Exception:
                    # Not encrypted, keep as is
                    result[key] = value
            else:
                result[key] = value
        return result

    def load_secrets(self, environment: str, decrypt: bool = True) -> dict[str, Any]:
        """
        Load secrets for a given environment.

        Args:
            environment: Environment name (dev, staging, production)
            decrypt: Whether to decrypt the secrets (requires age_key)

        Returns:
            Dictionary of secrets (encrypted or decrypted)
        """
        secrets_file = self.secrets_dir / f"{environment}.yaml"
        if not secrets_file.exists():
            raise FileNotFoundError(f"Secrets file not found: {secrets_file}")

        with open(secrets_file, "r") as f:
            data = yaml.safe_load(f)

        if decrypt:
            if not self.age_key:
                raise ValueError("Cannot decrypt without an age key")
            return self.decrypt_dict(data)
        return data

    def save_secrets(
        self,
        environment: str,
        secrets: dict[str, Any],
        recipient_public_keys: list[str],
        encrypt: bool = True,
    ):
        """
        Save secrets for a given environment.

        Args:
            environment: Environment name (dev, staging, production)
            secrets: Dictionary of secrets to save
            recipient_public_keys: List of age public keys to encrypt for
            encrypt: Whether to encrypt the secrets before saving
        """
        self.secrets_dir.mkdir(parents=True, exist_ok=True)

        if encrypt:
            data = self.encrypt_dict(secrets, recipient_public_keys)
        else:
            data = secrets

        secrets_file = self.secrets_dir / f"{environment}.yaml"
        with open(secrets_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def get_default_key_path() -> Path:
    """Get default path for age key file."""
    return Path.home() / ".age" / "keys.txt"


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
        secrets_dir = Path.cwd() / "secrets"

    if key_path is None:
        key_path = get_default_key_path()

    if not key_path.exists():
        raise FileNotFoundError(
            f"Age key file not found: {key_path}. "
            f"Generate one with: djb-secrets init"
        )

    manager = SecretsManager.from_key_file(secrets_dir, key_path)
    return manager.load_secrets(environment)
