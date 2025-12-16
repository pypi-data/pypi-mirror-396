"""Tests for djb sync-superuser CLI command."""

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
    with patch("djb.cli.superuser.subprocess.run") as mock:
        mock.return_value = Mock(returncode=0)
        yield mock


class TestSyncSuperuserCommand:
    """Tests for sync-superuser CLI command."""

    def test_help(self, runner):
        """Test that sync-superuser --help works."""
        result = runner.invoke(djb_cli, ["sync-superuser", "--help"])
        assert result.exit_code == 0
        assert "Sync superuser from encrypted secrets" in result.output
        assert "--environment" in result.output
        assert "--dry-run" in result.output
        assert "--app" in result.output

    def test_local_sync_default(self, runner, mock_subprocess_run):
        """Test local sync with default options."""
        result = runner.invoke(djb_cli, ["sync-superuser"])

        assert result.exit_code == 0
        assert "Syncing superuser locally" in result.output

        mock_subprocess_run.assert_called_once()
        call_args = mock_subprocess_run.call_args[0][0]
        assert call_args == ["python", "manage.py", "sync_superuser"]

    def test_local_sync_with_environment(self, runner, mock_subprocess_run):
        """Test local sync with specific environment."""
        result = runner.invoke(djb_cli, ["sync-superuser", "-e", "dev"])

        assert result.exit_code == 0
        call_args = mock_subprocess_run.call_args[0][0]
        assert call_args == ["python", "manage.py", "sync_superuser", "--environment", "dev"]

    def test_local_sync_with_dry_run(self, runner, mock_subprocess_run):
        """Test local sync with dry-run flag."""
        result = runner.invoke(djb_cli, ["sync-superuser", "--dry-run"])

        assert result.exit_code == 0
        call_args = mock_subprocess_run.call_args[0][0]
        assert call_args == ["python", "manage.py", "sync_superuser", "--dry-run"]

    def test_local_sync_with_all_options(self, runner, mock_subprocess_run):
        """Test local sync with all options combined."""
        result = runner.invoke(djb_cli, ["sync-superuser", "-e", "staging", "--dry-run"])

        assert result.exit_code == 0
        call_args = mock_subprocess_run.call_args[0][0]
        assert call_args == [
            "python",
            "manage.py",
            "sync_superuser",
            "--environment",
            "staging",
            "--dry-run",
        ]

    def test_heroku_sync(self, runner, mock_subprocess_run):
        """Test sync on Heroku."""
        result = runner.invoke(djb_cli, ["sync-superuser", "--app", "myapp"])

        assert result.exit_code == 0
        assert "Syncing superuser on Heroku (myapp)" in result.output

        call_args = mock_subprocess_run.call_args[0][0]
        assert call_args == [
            "heroku",
            "run",
            "-a",
            "myapp",
            "python",
            "manage.py",
            "sync_superuser",
        ]

    def test_heroku_sync_with_environment(self, runner, mock_subprocess_run):
        """Test Heroku sync with specific environment."""
        result = runner.invoke(djb_cli, ["sync-superuser", "--app", "myapp", "-e", "heroku_prod"])

        assert result.exit_code == 0
        call_args = mock_subprocess_run.call_args[0][0]
        assert call_args == [
            "heroku",
            "run",
            "-a",
            "myapp",
            "python",
            "manage.py",
            "sync_superuser",
            "--environment",
            "heroku_prod",
        ]

    def test_heroku_sync_with_dry_run(self, runner, mock_subprocess_run):
        """Test Heroku sync with dry-run."""
        result = runner.invoke(djb_cli, ["sync-superuser", "--app", "myapp", "--dry-run"])

        assert result.exit_code == 0
        call_args = mock_subprocess_run.call_args[0][0]
        assert "--dry-run" in call_args

    def test_heroku_sync_with_all_options(self, runner, mock_subprocess_run):
        """Test Heroku sync with all options."""
        result = runner.invoke(
            djb_cli, ["sync-superuser", "--app", "myapp", "-e", "heroku_prod", "--dry-run"]
        )

        assert result.exit_code == 0
        call_args = mock_subprocess_run.call_args[0][0]
        assert call_args == [
            "heroku",
            "run",
            "-a",
            "myapp",
            "python",
            "manage.py",
            "sync_superuser",
            "--environment",
            "heroku_prod",
            "--dry-run",
        ]

    def test_failure_returns_error(self, runner, mock_subprocess_run):
        """Test that command failure raises ClickException."""
        mock_subprocess_run.return_value = Mock(returncode=1)

        result = runner.invoke(djb_cli, ["sync-superuser"])

        assert result.exit_code == 1
        assert "Failed to sync superuser" in result.output

    def test_environment_choices(self, runner):
        """Test that only valid environment choices are accepted."""
        result = runner.invoke(djb_cli, ["sync-superuser", "-e", "invalid_env"])

        assert result.exit_code == 2
        assert "Invalid value" in result.output or "invalid_env" in result.output

    def test_valid_environment_dev(self, runner, mock_subprocess_run):
        """Test dev environment is accepted."""
        result = runner.invoke(djb_cli, ["sync-superuser", "-e", "dev"])
        assert result.exit_code == 0

    def test_valid_environment_staging(self, runner, mock_subprocess_run):
        """Test staging environment is accepted."""
        result = runner.invoke(djb_cli, ["sync-superuser", "-e", "staging"])
        assert result.exit_code == 0

    def test_valid_environment_heroku_prod(self, runner, mock_subprocess_run):
        """Test heroku_prod environment is accepted."""
        result = runner.invoke(djb_cli, ["sync-superuser", "-e", "heroku_prod"])
        assert result.exit_code == 0
