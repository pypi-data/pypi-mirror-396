"""Tests for djb init command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from djb.cli.djb import djb_cli


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run to avoid actual command execution."""
    with patch("djb.cli.init.subprocess.run") as mock:
        # Default: commands succeed
        mock.return_value = Mock(returncode=0, stdout=b"", stderr=b"")
        yield mock


class TestDjbInit:
    """Tests for djb init command."""

    def test_init_help(self, runner):
        """Test that init --help works."""
        result = runner.invoke(djb_cli, ["init", "--help"])
        assert result.exit_code == 0
        assert "Initialize djb development environment" in result.output
        assert "--skip-brew" in result.output
        assert "--skip-python" in result.output
        assert "--skip-frontend" in result.output
        assert "--skip-secrets" in result.output

    def test_init_skip_all(self, runner, mock_subprocess_run):
        """Test init with all skips - should complete without errors."""
        result = runner.invoke(
            djb_cli,
            ["init", "--skip-brew", "--skip-python", "--skip-frontend", "--skip-secrets"],
        )
        assert result.exit_code == 0
        # With all skips, no subprocess calls should be made
        assert mock_subprocess_run.call_count == 0

    def test_init_homebrew_check_on_macos(self, runner, mock_subprocess_run):
        """Test that init checks for Homebrew on macOS."""
        with patch("djb.cli.init.sys.platform", "darwin"):
            # Mock brew not found
            def run_side_effect(cmd, *args, **kwargs):
                if cmd == ["which", "brew"]:
                    return Mock(returncode=1)
                return Mock(returncode=0, stdout=b"", stderr=b"")

            mock_subprocess_run.side_effect = run_side_effect

            result = runner.invoke(
                djb_cli,
                ["init", "--skip-python", "--skip-frontend", "--skip-secrets"],
            )

            assert result.exit_code == 1

    def test_init_skips_homebrew_on_non_macos(self, runner, mock_subprocess_run):
        """Test that init skips Homebrew on non-macOS platforms."""
        with patch("djb.cli.init.sys.platform", "linux"):
            result = runner.invoke(
                djb_cli,
                ["init", "--skip-python", "--skip-frontend", "--skip-secrets"],
            )

            assert result.exit_code == 0
            # On non-macOS, no brew commands should be called
            brew_calls = [c for c in mock_subprocess_run.call_args_list if "brew" in str(c)]
            assert len(brew_calls) == 0

    def test_init_installs_age_when_missing(self, runner, mock_subprocess_run):
        """Test that init installs age when not present."""
        with patch("djb.cli.init.sys.platform", "darwin"):

            def run_side_effect(cmd, *args, **kwargs):
                # brew exists, age doesn't
                if cmd == ["which", "brew"]:
                    return Mock(returncode=0)
                if cmd == ["brew", "list", "age"]:
                    return Mock(returncode=1)  # Not installed
                return Mock(returncode=0, stdout=b"", stderr=b"")

            mock_subprocess_run.side_effect = run_side_effect

            result = runner.invoke(
                djb_cli,
                ["init", "--skip-python", "--skip-frontend", "--skip-secrets"],
            )

            assert result.exit_code == 0
            # Check that brew install age was called
            install_calls = [
                c
                for c in mock_subprocess_run.call_args_list
                if "brew" in str(c) and "install" in str(c) and "age" in str(c)
            ]
            assert len(install_calls) > 0

    def test_init_skips_age_when_present(self, runner, mock_subprocess_run):
        """Test that init skips installing age when already present."""
        with patch("djb.cli.init.sys.platform", "darwin"):

            def run_side_effect(cmd, *args, **kwargs):
                # brew and age both exist
                if cmd == ["which", "brew"]:
                    return Mock(returncode=0)
                if cmd == ["brew", "list", "age"]:
                    return Mock(returncode=0)  # Already installed
                return Mock(returncode=0, stdout=b"", stderr=b"")

            mock_subprocess_run.side_effect = run_side_effect

            result = runner.invoke(
                djb_cli,
                ["init", "--skip-python", "--skip-frontend", "--skip-secrets"],
            )

            assert result.exit_code == 0
            # Verify that brew install age was NOT called (since it's already installed)
            install_age_calls = [
                c
                for c in mock_subprocess_run.call_args_list
                if "brew" in str(c) and "install" in str(c) and "age" in str(c)
            ]
            assert len(install_age_calls) == 0

    def test_init_python_dependencies(self, runner, mock_subprocess_run, tmp_path):
        """Test that init runs uv sync for Python dependencies."""
        result = runner.invoke(
            djb_cli,
            [
                "init",
                "--skip-brew",
                "--skip-frontend",
                "--skip-secrets",
                "--project-root",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        # Check that uv sync was called
        uv_calls = [
            c for c in mock_subprocess_run.call_args_list if "uv" in str(c) and "sync" in str(c)
        ]
        assert len(uv_calls) > 0

    def test_init_frontend_dependencies(self, runner, mock_subprocess_run, tmp_path):
        """Test that init runs bun install for frontend dependencies."""
        # Create frontend directory
        frontend_dir = tmp_path / "frontend"
        frontend_dir.mkdir()

        result = runner.invoke(
            djb_cli,
            [
                "init",
                "--skip-brew",
                "--skip-python",
                "--skip-secrets",
                "--project-root",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        # Check that bun install was called
        bun_calls = [
            c for c in mock_subprocess_run.call_args_list if "bun" in str(c) and "install" in str(c)
        ]
        assert len(bun_calls) > 0

    def test_init_skips_frontend_when_directory_missing(
        self, runner, mock_subprocess_run, tmp_path
    ):
        """Test that init skips frontend when directory doesn't exist."""
        result = runner.invoke(
            djb_cli,
            [
                "init",
                "--skip-brew",
                "--skip-python",
                "--skip-secrets",
                "--project-root",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        # Verify that bun install was NOT called (since frontend dir doesn't exist)
        bun_calls = [
            c for c in mock_subprocess_run.call_args_list if "bun" in str(c) and "install" in str(c)
        ]
        assert len(bun_calls) == 0

    def test_init_secrets_creates_missing_environments(self, runner, mock_subprocess_run, tmp_path):
        """Test that init creates secrets files for missing environments."""
        from djb.cli.init import _init_or_upgrade_secrets

        # Mock secrets to avoid actual encryption
        with patch("djb.cli.init._init_or_upgrade_secrets") as mock_secrets:
            mock_secrets.return_value = type(
                "SecretsStatus", (), {"initialized": ["dev", "staging"], "upgraded": [], "up_to_date": []}
            )()

            result = runner.invoke(
                djb_cli,
                [
                    "init",
                    "--skip-brew",
                    "--skip-python",
                    "--skip-frontend",
                    "--skip-hooks",
                    "--project-root",
                    str(tmp_path),
                ],
            )

            assert result.exit_code == 0
            assert "Created secrets" in result.output
            mock_secrets.assert_called_once()

    def test_init_secrets_upgrades_existing(self, runner, mock_subprocess_run, tmp_path):
        """Test that init upgrades existing secrets with new template keys."""
        with patch("djb.cli.init._init_or_upgrade_secrets") as mock_secrets:
            mock_secrets.return_value = type(
                "SecretsStatus", (), {"initialized": [], "upgraded": ["dev"], "up_to_date": ["staging"]}
            )()

            result = runner.invoke(
                djb_cli,
                [
                    "init",
                    "--skip-brew",
                    "--skip-python",
                    "--skip-frontend",
                    "--skip-hooks",
                    "--project-root",
                    str(tmp_path),
                ],
            )

            assert result.exit_code == 0
            assert "Upgraded secrets" in result.output
            mock_secrets.assert_called_once()

    def test_init_secrets_already_up_to_date(self, runner, mock_subprocess_run, tmp_path):
        """Test that init reports when all secrets are up to date."""
        with patch("djb.cli.init._init_or_upgrade_secrets") as mock_secrets:
            mock_secrets.return_value = type(
                "SecretsStatus",
                (),
                {"initialized": [], "upgraded": [], "up_to_date": ["dev", "staging", "heroku_prod"]},
            )()

            result = runner.invoke(
                djb_cli,
                [
                    "init",
                    "--skip-brew",
                    "--skip-python",
                    "--skip-frontend",
                    "--skip-hooks",
                    "--project-root",
                    str(tmp_path),
                ],
            )

            assert result.exit_code == 0
            assert "already up to date" in result.output
            mock_secrets.assert_called_once()

    def test_init_with_project_root(self, runner, mock_subprocess_run, tmp_path):
        """Test that init respects --project-root option."""
        result = runner.invoke(
            djb_cli,
            [
                "init",
                "--skip-brew",
                "--skip-frontend",
                "--skip-secrets",
                "--project-root",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        # Verify uv sync was called with correct cwd
        uv_calls = [
            c
            for c in mock_subprocess_run.call_args_list
            if len(c.args) > 0 and "uv" in str(c.args[0])
        ]
        assert any(c.kwargs.get("cwd") == tmp_path for c in uv_calls)

    def test_init_idempotent(self, runner, mock_subprocess_run):
        """Test that running init multiple times is safe (idempotent)."""
        with patch("djb.cli.init.sys.platform", "darwin"):

            def run_side_effect(cmd, *args, **kwargs):
                # Everything already installed
                return Mock(returncode=0, stdout=b"", stderr=b"")

            mock_subprocess_run.side_effect = run_side_effect

            # Run init twice
            result1 = runner.invoke(
                djb_cli,
                ["init", "--skip-python", "--skip-frontend", "--skip-secrets"],
            )

            result2 = runner.invoke(
                djb_cli,
                ["init", "--skip-python", "--skip-frontend", "--skip-secrets"],
            )

            # Both runs should succeed (idempotent)
            assert result1.exit_code == 0
            assert result2.exit_code == 0

    def test_init_produces_no_empty_lines(self, runner, mock_subprocess_run):
        """Test that init output contains actual content, not just blank lines.

        Regression test: Previously, when the default log level was 'note' (25) and
        actual messages used logger.info() (level 20), no messages were displayed.
        Only empty logger.note() spacer calls were output as blank lines.
        """
        result = runner.invoke(
            djb_cli,
            [
                "init",
                "--skip-brew",
                "--skip-python",
                "--skip-frontend",
                "--skip-secrets",
                "--skip-hooks",
            ],
        )
        assert result.exit_code == 0

        # Split output into lines and check for meaningful content
        lines = result.output.strip().split("\n")

        # Should have multiple lines of actual content
        assert len(lines) >= 5, f"Expected at least 5 lines of output, got {len(lines)}"

        # No lines should be empty (except possibly trailing whitespace)
        empty_lines = [i for i, line in enumerate(lines) if not line.strip()]
        assert len(empty_lines) == 0, f"Found empty lines at positions: {empty_lines}"

        # Should contain recognizable messages
        output_text = result.output
        assert "Initializing" in output_text or "initialization" in output_text.lower()
        assert "complete" in output_text.lower() or "skip" in output_text.lower()


class TestInitOrUpgradeSecrets:
    """Tests for _init_or_upgrade_secrets function."""

    def test_creates_all_environments_when_none_exist(self, runner, mock_subprocess_run, tmp_path):
        """Test that all environments are created when none exist."""
        from djb.cli.init import SECRETS_ENVIRONMENTS

        with patch("djb.secrets.get_default_key_path", return_value=tmp_path / ".age" / "keys.txt"):
            result = runner.invoke(
                djb_cli,
                [
                    "init",
                    "--skip-brew",
                    "--skip-python",
                    "--skip-frontend",
                    "--skip-hooks",
                    "--project-root",
                    str(tmp_path),
                ],
            )

        assert result.exit_code == 0
        assert "Created secrets" in result.output

        # Verify files were created
        secrets_dir = tmp_path / "secrets"
        for env in SECRETS_ENVIRONMENTS:
            assert (secrets_dir / f"{env}.yaml").exists()

    def test_upgrades_existing_secrets_with_missing_keys(self, runner, mock_subprocess_run, tmp_path):
        """Test that existing secrets get upgraded with new template keys."""
        from djb.secrets import AgeKey, SecretsManager

        # Set up age key
        key_path = tmp_path / ".age" / "keys.txt"
        key_path.parent.mkdir(parents=True)
        age_key = AgeKey.generate()
        key_path.write_text(age_key.to_private_string())

        # Create secrets dir with partial secrets (missing superuser key)
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir()
        manager = SecretsManager(secrets_dir=secrets_dir, age_key=age_key)
        public_key = age_key.to_public_string()

        # Create dev secrets without superuser key
        manager.save_secrets(
            "dev", {"django_secret_key": "test-key", "db_credentials": {"host": "localhost"}}, [public_key]
        )

        with patch("djb.secrets.get_default_key_path", return_value=key_path):
            result = runner.invoke(
                djb_cli,
                [
                    "init",
                    "--skip-brew",
                    "--skip-python",
                    "--skip-frontend",
                    "--skip-hooks",
                    "--project-root",
                    str(tmp_path),
                ],
            )

        assert result.exit_code == 0
        # dev should be upgraded (missing superuser), others should be initialized
        assert "Upgraded secrets" in result.output or "Created secrets" in result.output

        # Verify dev now has superuser key
        dev_secrets = manager.load_secrets("dev", decrypt=True)
        assert "superuser" in dev_secrets

    def test_reports_up_to_date_when_no_changes_needed(self, runner, mock_subprocess_run, tmp_path):
        """Test that secrets are reported as up to date when complete."""
        from djb.cli.init import SECRETS_ENVIRONMENTS
        from djb.cli.secrets import _get_template
        from djb.secrets import AgeKey, SecretsManager

        # Set up age key
        key_path = tmp_path / ".age" / "keys.txt"
        key_path.parent.mkdir(parents=True)
        age_key = AgeKey.generate()
        key_path.write_text(age_key.to_private_string())

        # Create secrets dir with complete secrets
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir()
        manager = SecretsManager(secrets_dir=secrets_dir, age_key=age_key)
        public_key = age_key.to_public_string()

        # Create complete secrets for all environments
        for env in SECRETS_ENVIRONMENTS:
            template = _get_template(env)
            manager.save_secrets(env, template, [public_key])

        with patch("djb.secrets.get_default_key_path", return_value=key_path):
            result = runner.invoke(
                djb_cli,
                [
                    "init",
                    "--skip-brew",
                    "--skip-python",
                    "--skip-frontend",
                    "--skip-hooks",
                    "--project-root",
                    str(tmp_path),
                ],
            )

        assert result.exit_code == 0
        # All should be up to date
        assert "already up to date" in result.output
