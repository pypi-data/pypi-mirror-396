"""Tests for djb deploy CLI commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch, call

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
    with patch("djb.cli.deploy.subprocess.run") as mock:
        mock.return_value = Mock(returncode=0, stdout="main", stderr="")
        yield mock


class TestDeployHerokuCommand:
    """Tests for deploy heroku CLI command."""

    def test_help(self, runner):
        """Test that deploy heroku --help works."""
        result = runner.invoke(djb_cli, ["deploy", "heroku", "--help"])
        assert result.exit_code == 0
        assert "Deploy the application to Heroku" in result.output
        assert "--app" in result.output
        assert "--local-build" in result.output
        assert "--skip-migrate" in result.output
        assert "--skip-secrets" in result.output

    def test_requires_app_option_or_setting(self, runner):
        """Test that --app or DJB_APP_NAME setting is required."""
        with patch("djb.cli.deploy.get_app_name", return_value=None):
            result = runner.invoke(djb_cli, ["deploy", "heroku"])
        assert result.exit_code == 1
        assert "No app name provided" in result.output

    def test_editable_djb_handling(self, runner, tmp_path):
        """Test that editable djb is temporarily stashed for deploy."""
        # Create project structure
        (tmp_path / ".git").mkdir()
        djb_dir = tmp_path / "djb"
        djb_dir.mkdir()
        (djb_dir / "pyproject.toml").write_text('name = "djb"')

        # Create pyproject.toml with editable djb
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "myproject"

[tool.uv.sources]
djb = { path = "./djb", editable = true }
"""
        )

        # Create uv.lock to be stashed
        uv_lock = tmp_path / "uv.lock"
        uv_lock.write_text('[[package]]\nname = "djb"\nsource = { editable = "djb" }\n')

        with (
            patch("djb.cli.deploy.subprocess.run") as deploy_mock,
            patch("djb.cli.editable_stash.subprocess.run") as stash_mock,
            patch("djb.cli.deploy.Path.cwd", return_value=tmp_path),
        ):
            # Set up mocks
            deploy_mock.return_value = Mock(returncode=0, stdout="main\n", stderr="")
            stash_mock.return_value = Mock(returncode=0, stdout="", stderr="")

            result = runner.invoke(djb_cli, ["deploy", "heroku", "--app", "testapp", "-y"])

        # Should have stashed and restored editable djb configuration
        assert "Stashed editable djb configuration for deploy" in result.output
        assert "Restoring editable djb configuration" in result.output

    def test_local_build_option(self, runner, tmp_path):
        """Test --local-build runs frontend build locally."""
        (tmp_path / ".git").mkdir()
        frontend_dir = tmp_path / "frontend"
        frontend_dir.mkdir()

        with (
            patch("djb.cli.deploy.subprocess.run") as mock,
            patch("djb.cli.deploy.Path.cwd", return_value=tmp_path),
        ):
            mock.return_value = Mock(returncode=0, stdout="main\n", stderr="")

            result = runner.invoke(
                djb_cli, ["deploy", "heroku", "--app", "testapp", "--local-build", "-y"]
            )

        assert "Building frontend assets locally" in result.output

    def test_skip_migrate_option(self, runner, tmp_path):
        """Test --skip-migrate skips database migrations."""
        (tmp_path / ".git").mkdir()

        with (
            patch("djb.cli.deploy.subprocess.run") as mock,
            patch("djb.cli.deploy.Path.cwd", return_value=tmp_path),
        ):
            mock.return_value = Mock(returncode=0, stdout="main\n", stderr="")

            result = runner.invoke(
                djb_cli, ["deploy", "heroku", "--app", "testapp", "--skip-migrate", "-y"]
            )

        assert "Skipping database migrations" in result.output

    def test_skip_secrets_option(self, runner, tmp_path):
        """Test --skip-secrets skips secrets sync."""
        (tmp_path / ".git").mkdir()

        with (
            patch("djb.cli.deploy.subprocess.run") as mock,
            patch("djb.cli.deploy.Path.cwd", return_value=tmp_path),
        ):
            mock.return_value = Mock(returncode=0, stdout="main\n", stderr="")

            result = runner.invoke(
                djb_cli, ["deploy", "heroku", "--app", "testapp", "--skip-secrets", "-y"]
            )

        assert "Skipping secrets sync" in result.output

    def test_requires_git_repository(self, runner, tmp_path):
        """Test that deploy requires a git repository."""
        # No .git directory
        with patch("djb.cli.deploy.Path.cwd", return_value=tmp_path):
            with patch("djb.cli.deploy.subprocess.run") as mock:
                mock.return_value = Mock(returncode=0, stdout="", stderr="")

                result = runner.invoke(djb_cli, ["deploy", "heroku", "--app", "testapp", "-y"])

        assert result.exit_code == 1
        assert "Not in a git repository" in result.output


class TestDeployRevertCommand:
    """Tests for deploy revert CLI command."""

    def test_help(self, runner):
        """Test that deploy revert --help works."""
        result = runner.invoke(djb_cli, ["deploy", "revert", "--help"])
        assert result.exit_code == 0
        assert "Revert to a previous deployment" in result.output
        assert "--app" in result.output
        assert "--skip-migrate" in result.output

    def test_requires_app_option_or_setting(self, runner):
        """Test that --app or DJB_APP_NAME setting is required."""
        with patch("djb.cli.deploy.get_app_name", return_value=None):
            result = runner.invoke(djb_cli, ["deploy", "revert"])
        assert result.exit_code == 1
        assert "No app name provided" in result.output

    def test_revert_to_previous_commit(self, runner, tmp_path):
        """Test reverting to previous commit (HEAD~1)."""
        (tmp_path / ".git").mkdir()

        with (
            patch("djb.cli.deploy.subprocess.run") as mock,
            patch("djb.cli.deploy.Path.cwd", return_value=tmp_path),
        ):

            def side_effect(cmd, *args, **kwargs):
                if cmd == ["heroku", "auth:whoami"]:
                    return Mock(returncode=0)
                if "rev-parse" in cmd and "HEAD~1" in cmd:
                    return Mock(returncode=0, stdout="abc1234567890\n")
                if "cat-file" in cmd:
                    return Mock(returncode=0, stdout="commit\n")
                if "log" in cmd:
                    return Mock(returncode=0, stdout="abc1234 Previous commit\n")
                return Mock(returncode=0, stdout="", stderr="")

            mock.side_effect = side_effect

            result = runner.invoke(
                djb_cli, ["deploy", "revert", "--app", "testapp"], input="y\n"
            )

        assert "No git hash provided, using previous commit" in result.output

    def test_revert_to_specific_commit(self, runner, tmp_path):
        """Test reverting to a specific commit hash."""
        (tmp_path / ".git").mkdir()

        with (
            patch("djb.cli.deploy.subprocess.run") as mock,
            patch("djb.cli.deploy.Path.cwd", return_value=tmp_path),
        ):

            def side_effect(cmd, *args, **kwargs):
                if cmd == ["heroku", "auth:whoami"]:
                    return Mock(returncode=0)
                if "cat-file" in cmd:
                    return Mock(returncode=0, stdout="commit\n")
                if "log" in cmd:
                    return Mock(returncode=0, stdout="def5678 Specific commit\n")
                return Mock(returncode=0, stdout="", stderr="")

            mock.side_effect = side_effect

            result = runner.invoke(
                djb_cli, ["deploy", "revert", "--app", "testapp", "def5678"], input="y\n"
            )

        assert "Reverting to: def5678" in result.output

    def test_revert_invalid_hash(self, runner, tmp_path):
        """Test revert with invalid git hash."""
        (tmp_path / ".git").mkdir()

        with (
            patch("djb.cli.deploy.subprocess.run") as mock,
            patch("djb.cli.deploy.Path.cwd", return_value=tmp_path),
        ):

            def side_effect(cmd, *args, **kwargs):
                if cmd == ["heroku", "auth:whoami"]:
                    return Mock(returncode=0)
                if "cat-file" in cmd:
                    return Mock(returncode=1, stdout="", stderr="Not a valid object")
                return Mock(returncode=0, stdout="", stderr="")

            mock.side_effect = side_effect

            result = runner.invoke(
                djb_cli, ["deploy", "revert", "--app", "testapp", "invalid"]
            )

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_revert_cancelled(self, runner, tmp_path):
        """Test revert can be cancelled at confirmation."""
        (tmp_path / ".git").mkdir()

        with (
            patch("djb.cli.deploy.subprocess.run") as mock,
            patch("djb.cli.deploy.Path.cwd", return_value=tmp_path),
        ):

            def side_effect(cmd, *args, **kwargs):
                if cmd == ["heroku", "auth:whoami"]:
                    return Mock(returncode=0)
                if "rev-parse" in cmd:
                    return Mock(returncode=0, stdout="abc1234567890\n")
                if "cat-file" in cmd:
                    return Mock(returncode=0, stdout="commit\n")
                if "log" in cmd:
                    return Mock(returncode=0, stdout="abc1234 Some commit\n")
                return Mock(returncode=0, stdout="", stderr="")

            mock.side_effect = side_effect

            result = runner.invoke(
                djb_cli, ["deploy", "revert", "--app", "testapp"], input="n\n"
            )

        assert result.exit_code == 1
        assert "Revert cancelled" in result.output

    def test_revert_skip_migrate(self, runner, tmp_path):
        """Test revert with --skip-migrate skips migrations."""
        (tmp_path / ".git").mkdir()

        with (
            patch("djb.cli.deploy.subprocess.run") as mock,
            patch("djb.cli.deploy.Path.cwd", return_value=tmp_path),
        ):

            def side_effect(cmd, *args, **kwargs):
                if cmd == ["heroku", "auth:whoami"]:
                    return Mock(returncode=0)
                if "rev-parse" in cmd:
                    return Mock(returncode=0, stdout="abc1234567890\n")
                if "cat-file" in cmd:
                    return Mock(returncode=0, stdout="commit\n")
                if "log" in cmd:
                    return Mock(returncode=0, stdout="abc1234 Some commit\n")
                return Mock(returncode=0, stdout="", stderr="")

            mock.side_effect = side_effect

            result = runner.invoke(
                djb_cli,
                ["deploy", "revert", "--app", "testapp", "--skip-migrate"],
                input="y\n",
            )

        assert "Skipping database migrations" in result.output


class TestDeployGroup:
    """Tests for deploy command group."""

    def test_deploy_help(self, runner):
        """Test that deploy --help shows subcommands."""
        result = runner.invoke(djb_cli, ["deploy", "--help"])
        assert result.exit_code == 0
        assert "heroku" in result.output
        assert "revert" in result.output
