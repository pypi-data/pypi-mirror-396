"""Tests for djb app name detection."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from djb.cli.app_name import get_app_name, _parse_settings_file, _find_settings_file


class TestGetAppName:
    """Tests for get_app_name function."""

    def test_returns_none_when_no_settings_found(self, tmp_path):
        """Test that None is returned when no settings can be found."""
        # Mock Django settings lookup to return None (simulating no Django setup)
        with patch(
            "djb.cli.app_name._get_from_django_settings", return_value=None
        ):
            result = get_app_name(tmp_path)
        assert result is None

    def test_parses_app_name_from_settings_file(self, tmp_path, monkeypatch):
        """Test parsing DJB_APP_NAME from settings.py."""
        # Create a project structure
        project_dir = tmp_path / "myproject"
        project_dir.mkdir()
        settings_file = project_dir / "settings.py"
        settings_file.write_text('DJB_APP_NAME = "myapp"\n')

        # Create pyproject.toml pointing to project
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "myproject"\n')

        # Clear DJANGO_SETTINGS_MODULE to force file discovery
        monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)

        # Mock Django settings lookup to return None (force file parsing)
        with patch(
            "djb.cli.app_name._get_from_django_settings", return_value=None
        ):
            result = get_app_name(tmp_path)
        assert result == "myapp"

    def test_parses_single_quoted_app_name(self, tmp_path, monkeypatch):
        """Test parsing DJB_APP_NAME with single quotes."""
        project_dir = tmp_path / "myproject"
        project_dir.mkdir()
        settings_file = project_dir / "settings.py"
        settings_file.write_text("DJB_APP_NAME = 'myapp'\n")

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "myproject"\n')

        monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)

        with patch(
            "djb.cli.app_name._get_from_django_settings", return_value=None
        ):
            result = get_app_name(tmp_path)
        assert result == "myapp"

    def test_handles_spaces_around_equals(self, tmp_path, monkeypatch):
        """Test parsing with various spacing around equals sign."""
        project_dir = tmp_path / "myproject"
        project_dir.mkdir()
        settings_file = project_dir / "settings.py"
        settings_file.write_text('DJB_APP_NAME   =   "spaced-app"\n')

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "myproject"\n')

        monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)

        with patch(
            "djb.cli.app_name._get_from_django_settings", return_value=None
        ):
            result = get_app_name(tmp_path)
        assert result == "spaced-app"

    def test_uses_django_settings_when_available(self, tmp_path):
        """Test that Django settings are used when available."""
        with patch(
            "djb.cli.app_name._get_from_django_settings", return_value="django-app"
        ):
            result = get_app_name(tmp_path)
        assert result == "django-app"


class TestParseSettingsFile:
    """Tests for _parse_settings_file function."""

    def test_returns_none_for_missing_file(self, tmp_path):
        """Test that None is returned for non-existent settings."""
        result = _parse_settings_file(tmp_path)
        assert result is None

    def test_returns_none_when_setting_not_defined(self, tmp_path):
        """Test that None is returned when DJB_APP_NAME is not defined."""
        settings = tmp_path / "settings.py"
        settings.write_text('DEBUG = True\n')

        with patch.dict("os.environ", {"DJANGO_SETTINGS_MODULE": "settings"}):
            result = _parse_settings_file(tmp_path)

        assert result is None


class TestFindSettingsFile:
    """Tests for _find_settings_file function."""

    def test_finds_settings_from_pyproject(self, tmp_path):
        """Test finding settings.py based on pyproject.toml project name."""
        # Create project structure
        project_dir = tmp_path / "myproject"
        project_dir.mkdir()
        settings_file = project_dir / "settings.py"
        settings_file.write_text("")

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "myproject"\n')

        result = _find_settings_file(tmp_path)
        assert result == settings_file

    def test_returns_none_when_no_settings_found(self, tmp_path):
        """Test that None is returned when no settings file exists."""
        result = _find_settings_file(tmp_path)
        assert result is None

    def test_ignores_venv_directories(self, tmp_path):
        """Test that .venv directories are ignored."""
        # Create settings in .venv (should be ignored)
        venv_dir = tmp_path / ".venv" / "lib" / "python3.14"
        venv_dir.mkdir(parents=True)
        venv_settings = venv_dir / "settings.py"
        venv_settings.write_text('DJB_APP_NAME = "wrong"\n')

        result = _find_settings_file(tmp_path)
        assert result is None
