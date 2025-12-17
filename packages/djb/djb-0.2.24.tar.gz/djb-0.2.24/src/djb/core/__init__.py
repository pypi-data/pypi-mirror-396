"""
djb core utilities.

This module provides foundational components used throughout djb:
- Exception hierarchy for consistent error handling
- Sentinel values for special meanings in function signatures
"""

from __future__ import annotations

from djb.core.exceptions import (
    DjbError,
    ImproperlyConfigured,
    SecretsError,
    SecretsKeyNotFound,
    SecretsDecryptionFailed,
    SecretsFileNotFound,
    DeploymentError,
    HerokuAuthError,
    HerokuPushError,
)

__all__ = [
    "DjbError",
    "ImproperlyConfigured",
    "SecretsError",
    "SecretsKeyNotFound",
    "SecretsDecryptionFailed",
    "SecretsFileNotFound",
    "DeploymentError",
    "HerokuAuthError",
    "HerokuPushError",
]
