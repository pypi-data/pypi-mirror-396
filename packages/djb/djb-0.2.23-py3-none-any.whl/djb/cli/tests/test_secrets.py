"""Tests for djb secrets CLI commands and safeguards."""

from __future__ import annotations

from pathlib import Path
from typing import Callable
from unittest.mock import patch

import pytest

from djb.cli.secrets import rotate
from djb.secrets import SecretsManager
from djb.secrets.core import (
    find_placeholder_secrets,
    format_identity,
    is_placeholder_value,
    is_valid_age_public_key,
    parse_identity,
    parse_sops_config,
)
from djb.secrets.init import SECRETS_ENVIRONMENTS


class TestPlaceholderDetection:
    """Tests for placeholder secret detection."""

    def test_detects_change_me(self):
        """Test that CHANGE-ME is detected as placeholder."""
        assert is_placeholder_value("CHANGE-ME") is True
        assert is_placeholder_value("change-me") is True
        assert is_placeholder_value("CHANGEME") is True
        assert is_placeholder_value("changeme") is True
        assert is_placeholder_value("CHANGE_ME") is True

    def test_detects_todo_fixme(self):
        """Test that TODO and FIXME are detected."""
        assert is_placeholder_value("TODO: set this") is True
        assert is_placeholder_value("FIXME") is True

    def test_detects_placeholder_in_string(self):
        """Test that placeholders embedded in strings are detected."""
        assert is_placeholder_value("my-CHANGE-ME-value") is True
        assert is_placeholder_value("placeholder-secret") is True

    def test_real_secrets_not_flagged(self):
        """Test that real secrets are not flagged as placeholders."""
        assert is_placeholder_value("sk_live_abc123xyz") is False
        assert is_placeholder_value("django-insecure-abc123") is False
        assert is_placeholder_value("a1b2c3d4e5f6") is False
        assert is_placeholder_value("") is False

    def test_find_placeholder_secrets_flat(self):
        """Test finding placeholders in flat dict."""
        secrets = {
            "api_key": "CHANGE-ME",
            "secret_key": "real-secret-value",
            "token": "TODO",
        }
        placeholders = find_placeholder_secrets(secrets)
        assert "api_key" in placeholders
        assert "token" in placeholders
        assert "secret_key" not in placeholders

    def test_find_placeholder_secrets_nested(self):
        """Test finding placeholders in nested dict."""
        secrets = {
            "django_secret_key": "real-secret",
            "api_keys": {
                "stripe": "CHANGE-ME",
                "sendgrid": "real-key",
            },
            "database": {
                "credentials": {
                    "password": "changeme",
                }
            }
        }
        placeholders = find_placeholder_secrets(secrets)
        assert "api_keys.stripe" in placeholders
        assert "database.credentials.password" in placeholders
        assert "django_secret_key" not in placeholders
        assert "api_keys.sendgrid" not in placeholders

    def test_find_placeholder_secrets_empty(self):
        """Test that empty dict returns no placeholders."""
        assert find_placeholder_secrets({}) == []

    def test_find_placeholder_secrets_no_placeholders(self):
        """Test dict with no placeholders."""
        secrets = {
            "key1": "real-value-1",
            "key2": "real-value-2",
        }
        assert find_placeholder_secrets(secrets) == []


class TestIdentityFormatting:
    """Tests for git-style identity formatting."""

    def test_format_identity_with_name_and_email(self):
        """Test formatting identity with both name and email."""
        assert format_identity("Alice Smith", "alice@example.com") == "Alice Smith <alice@example.com>"

    def test_format_identity_email_only(self):
        """Test formatting identity with email only (no name)."""
        assert format_identity(None, "alice@example.com") == "alice@example.com"

    def test_parse_identity_git_style(self):
        """Test parsing git-style identity."""
        name, email = parse_identity("Alice Smith <alice@example.com>")
        assert name == "Alice Smith"
        assert email == "alice@example.com"

    def test_parse_identity_email_only(self):
        """Test parsing email-only identity (legacy format)."""
        name, email = parse_identity("alice@example.com")
        assert name is None
        assert email == "alice@example.com"

    def test_parse_identity_with_spaces(self):
        """Test parsing identity with extra spaces."""
        name, email = parse_identity("Alice Smith  <alice@example.com>")
        assert name == "Alice Smith"
        assert email == "alice@example.com"


class TestAgeKeyValidation:
    """Tests for age public key validation."""

    def test_valid_key_accepted(self):
        """Test that a valid age public key is accepted."""
        # Real key format (62 chars, starts with age1, bech32 charset)
        valid_key = "age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p"
        assert is_valid_age_public_key(valid_key) is True

    def test_key_must_start_with_age1(self):
        """Test that keys must start with 'age1'."""
        assert is_valid_age_public_key("xyz1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p") is False
        assert is_valid_age_public_key("age2ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p") is False

    def test_key_must_be_62_chars(self):
        """Test that keys must be exactly 62 characters."""
        # Too short
        assert is_valid_age_public_key("age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aq") is False
        # Too long
        assert is_valid_age_public_key("age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8pxxx") is False

    def test_key_must_use_bech32_charset(self):
        """Test that keys must use valid bech32 characters."""
        # Contains 'b' (not in bech32)
        assert is_valid_age_public_key("age1bl3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p") is False
        # Contains 'i' (not in bech32)
        assert is_valid_age_public_key("age1il3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p") is False
        # Contains 'o' (not in bech32)
        assert is_valid_age_public_key("age1ol3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p") is False
        # Contains uppercase
        assert is_valid_age_public_key("age1QL3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p") is False

    def test_garbage_rejected(self):
        """Test that obvious garbage is rejected."""
        assert is_valid_age_public_key("garbage") is False
        assert is_valid_age_public_key("") is False
        assert is_valid_age_public_key("age1") is False
        assert is_valid_age_public_key("not-a-key-at-all") is False


class TestRotateCommandSafeguards:
    """Tests for safeguards in the rotate command."""

    def test_invalid_key_rejected(
        self,
        runner,
        secrets_dir: Path,
        alice_key: tuple[Path, str],
        setup_sops_config: Callable[[dict[str, str]], Path],
    ):
        """Test that adding an invalid key is rejected."""
        alice_key_path, alice_public = alice_key
        setup_sops_config({alice_public: "alice@example.com"})

        with patch("djb.cli.secrets.get_default_key_path", return_value=alice_key_path):
            result = runner.invoke(
                rotate,
                [
                    "--add-key", "garbage-not-a-key",
                    "--add-email", "bob@example.com",
                    "--secrets-dir", str(secrets_dir),
                ],
            )

        assert result.exit_code != 0
        assert "Invalid age public key" in result.output

    def test_cannot_remove_last_recipient(
        self,
        runner,
        secrets_dir: Path,
        alice_key: tuple[Path, str],
        setup_sops_config: Callable[[dict[str, str]], Path],
    ):
        """Test that removing the last recipient is prevented."""
        alice_key_path, alice_public = alice_key
        setup_sops_config({alice_public: "alice@example.com"})

        with patch("djb.cli.secrets.get_default_key_path", return_value=alice_key_path):
            result = runner.invoke(
                rotate,
                [
                    "--remove-key", "alice@example.com",
                    "--secrets-dir", str(secrets_dir),
                ],
            )

        assert result.exit_code != 0
        assert "Cannot remove the last recipient" in result.output

    def test_can_remove_when_multiple_recipients(
        self,
        runner,
        secrets_dir: Path,
        alice_key: tuple[Path, str],
        bob_key: tuple[Path, str],
        setup_sops_config: Callable[[dict[str, str]], Path],
    ):
        """Test that removing a recipient works when others exist."""
        alice_key_path, alice_public = alice_key
        _, bob_public = bob_key

        setup_sops_config({
            alice_public: "alice@example.com",
            bob_public: "bob@example.com",
        })

        # Create encrypted secrets for both
        manager = SecretsManager(secrets_dir=secrets_dir, key_path=alice_key_path)
        for env in SECRETS_ENVIRONMENTS:
            manager.save_secrets(env, {"django_secret_key": "test"}, [alice_public, bob_public])

        with patch("djb.cli.secrets.get_default_key_path", return_value=alice_key_path):
            result = runner.invoke(
                rotate,
                [
                    "--remove-key", "bob@example.com",
                    "--secrets-dir", str(secrets_dir),
                ],
            )

        assert result.exit_code == 0
        assert "Removed key" in result.output

        # Verify Bob was removed from .sops.yaml
        recipients = parse_sops_config(secrets_dir)
        assert alice_public in recipients
        assert bob_public not in recipients

    def test_valid_key_accepted(
        self,
        runner,
        secrets_dir: Path,
        alice_key: tuple[Path, str],
        bob_key: tuple[Path, str],
        setup_sops_config: Callable[[dict[str, str]], Path],
    ):
        """Test that adding a valid key works."""
        alice_key_path, alice_public = alice_key
        _, bob_public = bob_key

        setup_sops_config({alice_public: "alice@example.com"})

        # Create encrypted secrets
        manager = SecretsManager(secrets_dir=secrets_dir, key_path=alice_key_path)
        for env in SECRETS_ENVIRONMENTS:
            manager.save_secrets(env, {"django_secret_key": "test"}, [alice_public])

        with patch("djb.cli.secrets.get_default_key_path", return_value=alice_key_path):
            result = runner.invoke(
                rotate,
                [
                    "--add-key", bob_public,
                    "--add-email", "bob@example.com",
                    "--secrets-dir", str(secrets_dir),
                ],
            )

        assert result.exit_code == 0
        assert "Added key for bob@example.com" in result.output

        # Verify Bob was added to .sops.yaml
        recipients = parse_sops_config(secrets_dir)
        assert alice_public in recipients
        assert bob_public in recipients
