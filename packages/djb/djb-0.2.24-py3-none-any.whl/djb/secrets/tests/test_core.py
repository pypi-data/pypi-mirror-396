"""Tests for djb.secrets.core module."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from djb.secrets.core import (
    SopsError,
    check_age_installed,
    check_sops_installed,
    create_sops_config,
    find_placeholder_secrets,
    format_identity,
    get_all_recipients,
    get_default_key_path,
    get_default_secrets_dir,
    get_public_key_from_private,
    is_placeholder_value,
    is_valid_age_public_key,
    parse_identity,
    parse_sops_config,
)


class TestCheckInstalled:
    """Tests for check_sops_installed and check_age_installed."""

    def test_check_sops_installed_found(self):
        """Test check_sops_installed when sops is available."""
        with patch("shutil.which", return_value="/usr/bin/sops"):
            assert check_sops_installed() is True

    def test_check_sops_installed_not_found(self):
        """Test check_sops_installed when sops is not available."""
        with patch("shutil.which", return_value=None):
            assert check_sops_installed() is False

    def test_check_age_installed_found(self):
        """Test check_age_installed when age-keygen is available."""
        with patch("shutil.which", return_value="/usr/bin/age-keygen"):
            assert check_age_installed() is True

    def test_check_age_installed_not_found(self):
        """Test check_age_installed when age-keygen is not available."""
        with patch("shutil.which", return_value=None):
            assert check_age_installed() is False


class TestGetDefaultKeyPath:
    """Tests for get_default_key_path."""

    def test_returns_age_keys_path(self, tmp_path):
        """Test default key path is .age/keys.txt in project root."""
        with patch("djb.secrets.core.find_project_root", return_value=tmp_path):
            result = get_default_key_path()
            assert result == tmp_path / ".age" / "keys.txt"

    def test_uses_provided_project_root(self, tmp_path):
        """Test using explicit project root."""
        result = get_default_key_path(tmp_path)
        assert result == tmp_path / ".age" / "keys.txt"


class TestGetDefaultSecretsDir:
    """Tests for get_default_secrets_dir."""

    def test_returns_secrets_in_cwd(self, tmp_path, monkeypatch):
        """Test default secrets dir is secrets/ in cwd."""
        monkeypatch.chdir(tmp_path)
        result = get_default_secrets_dir()
        assert result == tmp_path / "secrets"

    def test_uses_provided_project_root(self, tmp_path):
        """Test using explicit project root."""
        result = get_default_secrets_dir(tmp_path)
        assert result == tmp_path / "secrets"


class TestIsValidAgePublicKey:
    """Tests for is_valid_age_public_key."""

    def test_valid_key(self):
        """Test valid age public key."""
        # This is a properly formatted age public key (62 chars, starts with age1)
        key = "age1qyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqs3290gq"
        assert is_valid_age_public_key(key) is True

    def test_wrong_prefix(self):
        """Test rejection of wrong prefix."""
        key = "age2qyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqs3290gq"
        assert is_valid_age_public_key(key) is False

    def test_wrong_length(self):
        """Test rejection of wrong length."""
        key = "age1short"
        assert is_valid_age_public_key(key) is False

    def test_invalid_characters(self):
        """Test rejection of invalid bech32 characters."""
        # 'b' and '1' (except in prefix) are not valid bech32
        key = "age1qyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqsb290gq"
        assert is_valid_age_public_key(key) is False


class TestFormatAndParseIdentity:
    """Tests for format_identity and parse_identity."""

    def test_format_with_name_and_email(self):
        """Test formatting with both name and email."""
        result = format_identity("John Doe", "john@example.com")
        assert result == "John Doe <john@example.com>"

    def test_format_with_email_only(self):
        """Test formatting with email only."""
        result = format_identity(None, "john@example.com")
        assert result == "john@example.com"

    def test_parse_full_identity(self):
        """Test parsing full git-style identity."""
        name, email = parse_identity("John Doe <john@example.com>")
        assert name == "John Doe"
        assert email == "john@example.com"

    def test_parse_email_only(self):
        """Test parsing email-only identity."""
        name, email = parse_identity("john@example.com")
        assert name is None
        assert email == "john@example.com"

    def test_roundtrip(self):
        """Test format then parse returns original values."""
        formatted = format_identity("Jane Smith", "jane@example.com")
        name, email = parse_identity(formatted)
        assert name == "Jane Smith"
        assert email == "jane@example.com"

    def test_parse_identity_with_spaces(self):
        """Test parsing identity with extra spaces."""
        name, email = parse_identity("Alice Smith  <alice@example.com>")
        assert name == "Alice Smith"
        assert email == "alice@example.com"


class TestPlaceholderDetection:
    """Tests for placeholder detection functions."""

    def test_is_placeholder_change_me(self):
        """Test detection of CHANGE-ME placeholder (used in secrets templates)."""
        assert is_placeholder_value("CHANGE-ME") is True
        assert is_placeholder_value("change-me") is True
        assert is_placeholder_value("CHANGE-ME-DEV-KEY") is True
        assert is_placeholder_value("CHANGE-ME-PRODUCTION-PASSWORD") is True

    def test_is_placeholder_real_values(self):
        """Test that real values are not detected as placeholders."""
        real_values = [
            "sk_live_abc123xyz",
            "my-secret-key-12345",
            "production-database-password",
            "https://api.example.com",
            "user@example.com",
        ]

        for value in real_values:
            assert is_placeholder_value(value) is False, f"Should not detect: {value}"

    def test_is_placeholder_non_string(self):
        """Test that non-strings return False."""
        assert is_placeholder_value(123) is False  # type: ignore[arg-type]
        assert is_placeholder_value(None) is False  # type: ignore[arg-type]
        assert is_placeholder_value(["CHANGE-ME"]) is False  # type: ignore[arg-type]

    def test_find_placeholder_secrets_flat(self):
        """Test finding placeholders in flat dict."""
        secrets = {
            "api_key": "sk_live_real_key",
            "db_password": "CHANGE-ME",
            "secret_key": "real-secret",
        }

        result = find_placeholder_secrets(secrets)
        assert result == ["db_password"]

    def test_find_placeholder_secrets_nested(self):
        """Test finding placeholders in nested dict."""
        secrets = {
            "api_keys": {
                "stripe": "sk_live_real",
                "sendgrid": "CHANGE-ME",
            },
            "database": {
                "password": "CHANGE-ME-DEV-PASSWORD",
            },
        }

        result = find_placeholder_secrets(secrets)
        assert "api_keys.sendgrid" in result
        assert "database.password" in result
        assert len(result) == 2

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


class TestSopsConfig:
    """Tests for SOPS config functions."""

    def test_create_sops_config_dict(self, tmp_path):
        """Test creating .sops.yaml with dict recipients."""
        recipients = {
            "age1abc123": "John <john@example.com>",
            "age1def456": "Jane <jane@example.com>",
        }

        result = create_sops_config(tmp_path, recipients)

        assert result == tmp_path / ".sops.yaml"
        assert result.exists()

        content = result.read_text()
        assert "age1abc123" in content
        assert "age1def456" in content
        assert "john@example.com" in content
        assert "jane@example.com" in content

    def test_create_sops_config_list(self, tmp_path):
        """Test creating .sops.yaml with list of keys."""
        recipients = ["age1abc123", "age1def456"]

        result = create_sops_config(tmp_path, recipients)

        content = result.read_text()
        assert "age1abc123" in content
        assert "age1def456" in content

    def test_parse_sops_config(self, tmp_path):
        """Test parsing .sops.yaml."""
        sops_config = tmp_path / ".sops.yaml"
        sops_config.write_text(
            """creation_rules:
  - path_regex: '.*\\.yaml$'
    key_groups:
      - age:
          # John <john@example.com>
          - age1abc123
          # jane@example.com
          - age1def456
"""
        )

        result = parse_sops_config(tmp_path)

        assert result["age1abc123"] == "John <john@example.com>"
        assert result["age1def456"] == "jane@example.com"

    def test_parse_sops_config_missing(self, tmp_path):
        """Test parsing when .sops.yaml doesn't exist."""
        result = parse_sops_config(tmp_path)
        assert result == {}

    def test_get_all_recipients(self, tmp_path):
        """Test getting all recipients from .sops.yaml."""
        sops_config = tmp_path / ".sops.yaml"
        sops_config.write_text(
            """creation_rules:
  - path_regex: '.*\\.yaml$'
    key_groups:
      - age:
          - age1abc123
          - age1def456
"""
        )

        result = get_all_recipients(tmp_path)
        assert set(result) == {"age1abc123", "age1def456"}


class TestGetPublicKeyFromPrivate:
    """Tests for get_public_key_from_private."""

    def test_reads_from_comment(self, tmp_path):
        """Test reading public key from comment in key file."""
        key_file = tmp_path / "keys.txt"
        key_file.write_text(
            "# created: 2024-01-01T00:00:00Z\n"
            "# public key: age1qyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqs3290gq\n"
            "AGE-SECRET-KEY-1QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ\n"
        )

        result = get_public_key_from_private(key_file)
        assert result == "age1qyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqs3290gq"

    def test_missing_file_raises(self, tmp_path):
        """Test FileNotFoundError when key file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            get_public_key_from_private(tmp_path / "missing.txt")

    def test_derives_from_private_key(self, tmp_path):
        """Test deriving public key using age-keygen -y."""
        key_file = tmp_path / "keys.txt"
        # Key file without public key comment
        key_file.write_text(
            "AGE-SECRET-KEY-1QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ\n"
        )

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "age1derived123"

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = get_public_key_from_private(key_file)
            assert result == "age1derived123"
            mock_run.assert_called_once()

    def test_invalid_file_raises(self, tmp_path):
        """Test SopsError when file has no valid key."""
        key_file = tmp_path / "keys.txt"
        key_file.write_text("# just a comment\n")

        with pytest.raises(SopsError):
            get_public_key_from_private(key_file)
