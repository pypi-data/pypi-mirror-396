"""
djb.secrets - Encrypted secrets management

Provides encrypted secrets storage using age-style encryption (X25519 + ChaCha20-Poly1305).
Compatible with Kubernetes secrets and cloud deployments.
"""

from djb.secrets.core import (
    AgeKey,
    SecretsManager,
    get_default_key_path,
    load_secrets,
)

__all__ = [
    "AgeKey",
    "SecretsManager",
    "get_default_key_path",
    "load_secrets",
]
