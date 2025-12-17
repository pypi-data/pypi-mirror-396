"""Tests for djb.config module."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from djb.config import (
    DjbConfig,
    get_config,
    get_config_dir,
    get_config_path,
    get_email,
    get_name,
    get_project_name,
    get_project_name_from_pyproject,
    load_config_file,
    save_config_file,
    set_email,
    set_name,
    set_project_name,
)
from djb.types import Mode, Target


class TestConfigPaths:
    """Tests for config path helpers."""

    def test_get_config_dir(self, tmp_path):
        """Test get_config_dir returns .djb directory."""
        result = get_config_dir(tmp_path)
        assert result == tmp_path / ".djb"

    def test_get_config_path(self, tmp_path):
        """Test get_config_path returns config.yaml path."""
        result = get_config_path(tmp_path)
        assert result == tmp_path / ".djb" / "config.yaml"


class TestLoadSaveConfigFile:
    """Tests for load_config_file and save_config_file."""

    def test_load_config_file_missing(self, tmp_path):
        """Test loading when config file doesn't exist."""
        result = load_config_file(tmp_path)
        assert result == {}

    def test_load_config_file_exists(self, tmp_path):
        """Test loading existing config file."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text("name: John\nemail: john@example.com\n")

        result = load_config_file(tmp_path)
        assert result == {"name": "John", "email": "john@example.com"}

    def test_load_config_file_empty(self, tmp_path):
        """Test loading empty config file."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text("")

        result = load_config_file(tmp_path)
        assert result == {}

    def test_save_config_file_creates_directory(self, tmp_path):
        """Test save_config_file creates .djb directory if needed."""
        config = {"name": "John"}
        save_config_file(config, tmp_path)

        assert (tmp_path / ".djb").exists()
        assert (tmp_path / ".djb" / "config.yaml").exists()

    def test_save_config_file_content(self, tmp_path):
        """Test save_config_file writes correct content."""
        config = {"name": "John", "email": "john@example.com"}
        save_config_file(config, tmp_path)

        result = load_config_file(tmp_path)
        assert result == config


class TestGetProjectNameFromPyproject:
    """Tests for get_project_name_from_pyproject."""

    def test_reads_project_name(self, tmp_path):
        """Test reading project name from pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "myproject"\nversion = "1.0.0"\n')

        result = get_project_name_from_pyproject(tmp_path)
        assert result == "myproject"

    def test_missing_pyproject(self, tmp_path):
        """Test when pyproject.toml doesn't exist."""
        result = get_project_name_from_pyproject(tmp_path)
        assert result is None

    def test_missing_project_section(self, tmp_path):
        """Test when pyproject.toml has no project section."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.pytest]\n")

        result = get_project_name_from_pyproject(tmp_path)
        assert result is None

    def test_missing_name_field(self, tmp_path):
        """Test when project section has no name."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "1.0.0"\n')

        result = get_project_name_from_pyproject(tmp_path)
        assert result is None

    def test_invalid_toml(self, tmp_path):
        """Test with invalid TOML content."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("this is not valid toml [[[")

        result = get_project_name_from_pyproject(tmp_path)
        assert result is None


class TestDjbConfig:
    """Tests for DjbConfig class."""

    def test_default_values(self):
        """Test DjbConfig default values."""
        config = DjbConfig()
        assert config.project_dir is None
        assert config.project_name is None
        assert config.mode == Mode.DEVELOPMENT
        assert config.target == Target.HEROKU
        assert config.name is None
        assert config.email is None

    def test_with_overrides(self):
        """Test with_overrides creates new config with values."""
        config = DjbConfig()
        new_config = config.with_overrides(
            name="John",
            email="john@example.com",
            mode=Mode.PRODUCTION,
        )

        # Original unchanged
        assert config.name is None
        assert config.mode == Mode.DEVELOPMENT

        # New config has overrides
        assert new_config.name == "John"
        assert new_config.email == "john@example.com"
        assert new_config.mode == Mode.PRODUCTION

    def test_with_overrides_ignores_none(self):
        """Test with_overrides ignores None values."""
        config = DjbConfig(name="John")
        new_config = config.with_overrides(name=None, email="john@example.com")

        # name should be preserved since override was None
        assert new_config.name == "John"
        assert new_config.email == "john@example.com"

    def test_with_overrides_tracks_cli_overrides(self):
        """Test with_overrides tracks which fields were set."""
        config = DjbConfig()
        new_config = config.with_overrides(mode=Mode.STAGING, name="John")

        assert new_config._cli_overrides == {"mode": Mode.STAGING, "name": "John"}

    def test_save(self, tmp_path):
        """Test save persists config to file."""
        config = DjbConfig(
            project_dir=tmp_path,
            project_name="myproject",
            name="John",
            email="john@example.com",
            mode=Mode.STAGING,
            target=Target.HEROKU,
        )
        config.save()

        loaded = load_config_file(tmp_path)
        assert loaded["name"] == "John"
        assert loaded["email"] == "john@example.com"
        assert loaded["project_name"] == "myproject"
        assert loaded["mode"] == "staging"
        assert loaded["target"] == "heroku"

    def test_save_removes_none_values(self, tmp_path):
        """Test save doesn't write None values."""
        config = DjbConfig(project_dir=tmp_path, name="John", email=None)
        config.save()

        loaded = load_config_file(tmp_path)
        assert loaded["name"] == "John"
        assert "email" not in loaded

    def test_save_mode(self, tmp_path):
        """Test save_mode only saves mode."""
        # Create existing config
        save_config_file({"name": "John", "mode": "development"}, tmp_path)

        config = DjbConfig(project_dir=tmp_path, mode=Mode.PRODUCTION)
        config.save_mode()

        loaded = load_config_file(tmp_path)
        assert loaded["mode"] == "production"
        assert loaded["name"] == "John"  # Preserved


class TestGetConfig:
    """Tests for get_config function."""

    def test_loads_from_file(self, tmp_path):
        """Test get_config loads from config file."""
        save_config_file({"name": "John", "email": "john@example.com", "mode": "staging"}, tmp_path)

        config = get_config(tmp_path)
        assert config.name == "John"
        assert config.email == "john@example.com"
        assert config.mode == Mode.STAGING

    def test_env_overrides_file(self, tmp_path):
        """Test environment variables override file config."""
        save_config_file({"name": "John"}, tmp_path)

        with patch.dict(os.environ, {"DJB_NAME": "Jane"}):
            config = get_config(tmp_path)
            assert config.name == "Jane"

    def test_project_name_from_pyproject(self, tmp_path):
        """Test project_name falls back to pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "myproject"\n')

        config = get_config(tmp_path)
        assert config.project_name == "myproject"

    def test_project_name_config_overrides_pyproject(self, tmp_path):
        """Test config file project_name overrides pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "pyproject-name"\n')
        save_config_file({"project_name": "config-name"}, tmp_path)

        config = get_config(tmp_path)
        assert config.project_name == "config-name"

    def test_default_mode(self, tmp_path):
        """Test default mode is DEVELOPMENT."""
        config = get_config(tmp_path)
        assert config.mode == Mode.DEVELOPMENT

    def test_default_target(self, tmp_path):
        """Test default target is HEROKU."""
        config = get_config(tmp_path)
        assert config.target == Target.HEROKU

    def test_env_mode(self, tmp_path):
        """Test DJB_MODE environment variable."""
        with patch.dict(os.environ, {"DJB_MODE": "production"}):
            config = get_config(tmp_path)
            assert config.mode == Mode.PRODUCTION

    def test_env_target(self, tmp_path):
        """Test DJB_TARGET environment variable."""
        with patch.dict(os.environ, {"DJB_TARGET": "heroku"}):
            config = get_config(tmp_path)
            assert config.target == Target.HEROKU

    def test_project_dir_defaults_to_passed_root(self, tmp_path):
        """Test project_dir defaults to the passed project_root."""
        config = get_config(tmp_path)
        assert config.project_dir == tmp_path

    def test_invalid_mode_falls_back_to_default(self, tmp_path):
        """Test that invalid mode in file falls back to development."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text("mode: invalid_mode\n")

        config = get_config(tmp_path)

        assert config.mode == Mode.DEVELOPMENT

    def test_invalid_target_falls_back_to_default(self, tmp_path):
        """Test that invalid target in file falls back to heroku."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text("target: invalid_target\n")

        config = get_config(tmp_path)

        assert config.target == Target.HEROKU


class TestConfigPriority:
    """Tests for configuration priority (CLI > env > file > default)."""

    def test_cli_overrides_env(self, tmp_path):
        """Test that CLI overrides take precedence over env vars."""
        with patch.dict(os.environ, {"DJB_MODE": "staging"}):
            config = get_config(tmp_path)
            config = config.with_overrides(mode=Mode.PRODUCTION)

            assert config.mode == Mode.PRODUCTION


class TestSimpleHelpers:
    """Tests for simple get/set helper functions."""

    def test_get_name(self, tmp_path):
        """Test get_name returns configured name."""
        save_config_file({"name": "John"}, tmp_path)
        assert get_name(tmp_path) == "John"

    def test_get_name_missing(self, tmp_path):
        """Test get_name returns None when not configured."""
        assert get_name(tmp_path) is None

    def test_set_name(self, tmp_path):
        """Test set_name saves name to config."""
        set_name("John", tmp_path)
        assert get_name(tmp_path) == "John"

    def test_get_email(self, tmp_path):
        """Test get_email returns configured email."""
        save_config_file({"email": "john@example.com"}, tmp_path)
        assert get_email(tmp_path) == "john@example.com"

    def test_get_email_missing(self, tmp_path):
        """Test get_email returns None when not configured."""
        assert get_email(tmp_path) is None

    def test_set_email(self, tmp_path):
        """Test set_email saves email to config."""
        set_email("john@example.com", tmp_path)
        assert get_email(tmp_path) == "john@example.com"

    def test_get_project_name_from_config(self, tmp_path):
        """Test get_project_name returns from config."""
        save_config_file({"project_name": "myproject"}, tmp_path)
        assert get_project_name(tmp_path) == "myproject"

    def test_get_project_name_from_pyproject(self, tmp_path):
        """Test get_project_name falls back to pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "pyproject-name"\n')

        assert get_project_name(tmp_path) == "pyproject-name"

    def test_get_project_name_config_overrides_pyproject(self, tmp_path):
        """Test get_project_name prefers config over pyproject."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "pyproject-name"\n')
        save_config_file({"project_name": "config-name"}, tmp_path)

        assert get_project_name(tmp_path) == "config-name"

    def test_set_project_name(self, tmp_path):
        """Test set_project_name saves to config."""
        set_project_name("myproject", tmp_path)
        assert get_project_name(tmp_path) == "myproject"

    def test_helpers_preserve_other_config(self, tmp_path):
        """Test helpers preserve other config values."""
        save_config_file({"name": "John", "email": "john@example.com"}, tmp_path)

        set_project_name("myproject", tmp_path)

        config = load_config_file(tmp_path)
        assert config["name"] == "John"
        assert config["email"] == "john@example.com"
        assert config["project_name"] == "myproject"
