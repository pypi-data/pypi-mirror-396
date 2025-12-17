"""Conftest for management command tests - configures Django.

This must configure Django before any tests run, using pytest_configure
which runs before test collection begins.
"""

from __future__ import annotations

import os

import django
from django.conf import settings


def pytest_configure(config):
    """Configure Django settings for testing management commands.

    This runs before test collection, which is necessary because the
    sync_superuser module imports from django at module level.
    """
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[
                "django.contrib.auth",
                "django.contrib.contenttypes",
            ],
            AUTH_USER_MODEL="auth.User",
            BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        )
        django.setup()
