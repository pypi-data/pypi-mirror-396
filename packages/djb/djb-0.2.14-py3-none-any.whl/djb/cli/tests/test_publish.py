"""Tests for djb publish module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from djb.cli.djb import djb_cli
from djb.cli.publish import (
    bump_version,
    find_djb_root,
    find_parent_project,
    get_version,
    set_version,
    update_parent_dependency,
)


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run to avoid actual command execution."""
    with patch("djb.cli.publish.subprocess.run") as mock:
        mock.return_value = Mock(returncode=0, stdout="", stderr="")
        yield mock


class TestFindDjbRoot:
    """Tests for find_djb_root function."""

    def test_finds_djb_in_cwd(self, tmp_path):
        """Test finding djb when in djb directory."""
        (tmp_path / "pyproject.toml").write_text('name = "djb"\nversion = "0.1.0"')

        with patch("djb.cli.publish.Path.cwd", return_value=tmp_path):
            result = find_djb_root()
            assert result == tmp_path

    def test_finds_djb_in_subdirectory(self, tmp_path):
        """Test finding djb/ subdirectory."""
        djb_dir = tmp_path / "djb"
        djb_dir.mkdir()
        (djb_dir / "pyproject.toml").write_text('name = "djb"\nversion = "0.1.0"')

        with patch("djb.cli.publish.Path.cwd", return_value=tmp_path):
            result = find_djb_root()
            assert result == djb_dir

    def test_raises_when_not_found(self, tmp_path):
        """Test raises ClickException when djb not found."""
        import click

        with patch("djb.cli.publish.Path.cwd", return_value=tmp_path):
            with pytest.raises(click.ClickException):
                find_djb_root()


class TestGetVersion:
    """Tests for get_version function."""

    def test_gets_version(self, tmp_path):
        """Test getting version from pyproject.toml."""
        (tmp_path / "pyproject.toml").write_text('name = "djb"\nversion = "0.2.5"')

        result = get_version(tmp_path)
        assert result == "0.2.5"

    def test_raises_when_version_not_found(self, tmp_path):
        """Test raises when version not in pyproject.toml."""
        import click

        (tmp_path / "pyproject.toml").write_text('name = "djb"')

        with pytest.raises(click.ClickException):
            get_version(tmp_path)


class TestSetVersion:
    """Tests for set_version function."""

    def test_sets_version(self, tmp_path):
        """Test setting version in pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('name = "djb"\nversion = "0.2.5"')

        set_version(tmp_path, "0.3.0")

        content = pyproject.read_text()
        assert 'version = "0.3.0"' in content
        assert 'version = "0.2.5"' not in content


class TestBumpVersion:
    """Tests for bump_version function."""

    def test_bump_patch(self):
        """Test bumping patch version."""
        assert bump_version("0.2.5", "patch") == "0.2.6"

    def test_bump_minor(self):
        """Test bumping minor version resets patch."""
        assert bump_version("0.2.5", "minor") == "0.3.0"

    def test_bump_major(self):
        """Test bumping major version resets minor and patch."""
        assert bump_version("0.2.5", "major") == "1.0.0"

    def test_invalid_version_format(self):
        """Test raises for invalid version format."""
        import click

        with pytest.raises(click.ClickException):
            bump_version("invalid", "patch")

    def test_unknown_part(self):
        """Test raises for unknown version part."""
        import click

        with pytest.raises(click.ClickException):
            bump_version("0.2.5", "unknown")


class TestFindParentProject:
    """Tests for find_parent_project function."""

    def test_finds_parent_with_djb_dependency(self, tmp_path):
        """Test finding parent project with djb dependency."""
        djb_dir = tmp_path / "djb"
        djb_dir.mkdir()

        parent_pyproject = tmp_path / "pyproject.toml"
        parent_pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = ["djb>=0.2.5"]
"""
        )

        result = find_parent_project(djb_dir)
        assert result == tmp_path

    def test_returns_none_when_no_parent(self, tmp_path):
        """Test returns None when no parent project."""
        djb_dir = tmp_path / "djb"
        djb_dir.mkdir()

        result = find_parent_project(djb_dir)
        assert result is None

    def test_returns_none_when_parent_without_djb(self, tmp_path):
        """Test returns None when parent doesn't depend on djb."""
        djb_dir = tmp_path / "djb"
        djb_dir.mkdir()

        parent_pyproject = tmp_path / "pyproject.toml"
        parent_pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = ["other-package>=1.0"]
"""
        )

        result = find_parent_project(djb_dir)
        assert result is None


class TestUpdateParentDependency:
    """Tests for update_parent_dependency function."""

    def test_updates_version(self, tmp_path):
        """Test updates djb version in dependencies."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = [
    "djb>=0.2.4",
]
"""
        )

        result = update_parent_dependency(tmp_path, "0.2.5")

        assert result is True
        content = pyproject.read_text()
        assert '"djb>=0.2.5"' in content
        assert '"djb>=0.2.4"' not in content

    def test_returns_false_when_no_change(self, tmp_path):
        """Test returns False when version already correct."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = [
    "djb>=0.2.5",
]
"""
        )

        result = update_parent_dependency(tmp_path, "0.2.5")
        assert result is False


class TestPublishCommand:
    """Tests for publish CLI command."""

    def test_help(self, runner):
        """Test that publish --help works."""
        result = runner.invoke(djb_cli, ["publish", "--help"])
        assert result.exit_code == 0
        assert "Bump version and publish djb to PyPI" in result.output
        assert "--major" in result.output
        assert "--minor" in result.output
        assert "--patch" in result.output
        assert "--dry-run" in result.output

    def test_dry_run_basic(self, runner, tmp_path):
        """Test dry-run shows planned actions."""
        djb_dir = tmp_path / "djb"
        djb_dir.mkdir()
        (djb_dir / "pyproject.toml").write_text('name = "djb"\nversion = "0.2.4"')

        with patch("djb.cli.publish.Path.cwd", return_value=tmp_path):
            result = runner.invoke(djb_cli, ["publish", "--dry-run"])

        assert result.exit_code == 0
        assert "[dry-run]" in result.output
        assert "0.2.5" in result.output
        assert "v0.2.5" in result.output

    def test_dry_run_with_editable_parent(self, runner, tmp_path):
        """Test dry-run shows editable handling steps."""
        djb_dir = tmp_path / "djb"
        djb_dir.mkdir()
        (djb_dir / "pyproject.toml").write_text('name = "djb"\nversion = "0.2.4"')

        parent_pyproject = tmp_path / "pyproject.toml"
        parent_pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = ["djb>=0.2.4"]

[tool.uv.sources]
djb = { path = "djb", editable = true }
"""
        )

        with patch("djb.cli.publish.Path.cwd", return_value=tmp_path):
            result = runner.invoke(djb_cli, ["publish", "--dry-run"])

        assert result.exit_code == 0
        assert "editable" in result.output.lower()
        assert "Stash editable djb configuration" in result.output
        assert "Restore editable djb configuration" in result.output

    def test_dry_run_minor_bump(self, runner, tmp_path):
        """Test dry-run with --minor flag."""
        djb_dir = tmp_path / "djb"
        djb_dir.mkdir()
        (djb_dir / "pyproject.toml").write_text('name = "djb"\nversion = "0.2.4"')

        with patch("djb.cli.publish.Path.cwd", return_value=tmp_path):
            result = runner.invoke(djb_cli, ["publish", "--minor", "--dry-run"])

        assert result.exit_code == 0
        assert "0.3.0" in result.output

    def test_dry_run_major_bump(self, runner, tmp_path):
        """Test dry-run with --major flag."""
        djb_dir = tmp_path / "djb"
        djb_dir.mkdir()
        (djb_dir / "pyproject.toml").write_text('name = "djb"\nversion = "0.2.4"')

        with patch("djb.cli.publish.Path.cwd", return_value=tmp_path):
            result = runner.invoke(djb_cli, ["publish", "--major", "--dry-run"])

        assert result.exit_code == 0
        assert "1.0.0" in result.output
