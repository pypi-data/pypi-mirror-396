"""
djb.secrets - Encrypted secrets management with SOPS

Provides encrypted secrets storage using SOPS with age encryption.
Compatible with Kubernetes secrets and cloud deployments.

Multi-recipient encryption is configured via .sops.yaml with email comments.
"""

from djb.secrets.core import (
    SecretsManager,
    SopsError,
    check_age_installed,
    check_sops_installed,
    create_sops_config,
    decrypt_file,
    encrypt_file,
    find_placeholder_secrets,
    format_identity,
    generate_age_key,
    get_all_recipients,
    get_default_key_path,
    get_default_secrets_dir,
    get_public_key_from_private,
    is_placeholder_value,
    is_valid_age_public_key,
    load_secrets,
    load_secrets_for_mode,
    parse_identity,
    parse_sops_config,
    rotate_keys,
)
from djb.secrets.init import (
    SECRETS_ENVIRONMENTS,
    SecretsStatus,
    init_or_upgrade_secrets,
)

__all__ = [
    # Core SOPS functions
    "SecretsManager",
    "SopsError",
    "check_age_installed",
    "check_sops_installed",
    "create_sops_config",
    "decrypt_file",
    "encrypt_file",
    "find_placeholder_secrets",
    "format_identity",
    "generate_age_key",
    "get_all_recipients",
    "get_default_key_path",
    "get_default_secrets_dir",
    "get_public_key_from_private",
    "is_placeholder_value",
    "is_valid_age_public_key",
    "load_secrets",
    "load_secrets_for_mode",
    "parse_identity",
    "parse_sops_config",
    "rotate_keys",
    # Initialization
    "SECRETS_ENVIRONMENTS",
    "SecretsStatus",
    "init_or_upgrade_secrets",
]
