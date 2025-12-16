"""Tests for djb editable_stash module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from djb.cli.editable_stash import (
    EditableState,
    capture_editable_state,
    remove_editable_config,
    restore_editable_config,
    restore_editable_with_current_version,
    stashed_editable,
    _remove_djb_source_from_pyproject,
    _add_djb_source_to_pyproject,
)


class TestEditableState:
    """Tests for EditableState dataclass."""

    def test_was_editable_true(self):
        """Test was_editable returns True when editable config present."""
        state = EditableState(
            pyproject_content="",
            uv_lock_content=None,
            djb_source_config={"path": "djb", "editable": True},
            djb_version_specifier=">=0.2.6",
        )
        assert state.was_editable is True

    def test_was_editable_false_no_config(self):
        """Test was_editable returns False when no config."""
        state = EditableState(
            pyproject_content="",
            uv_lock_content=None,
            djb_source_config=None,
            djb_version_specifier=">=0.2.6",
        )
        assert state.was_editable is False

    def test_was_editable_false_not_editable(self):
        """Test was_editable returns False when editable=False."""
        state = EditableState(
            pyproject_content="",
            uv_lock_content=None,
            djb_source_config={"path": "djb", "editable": False},
            djb_version_specifier=">=0.2.6",
        )
        assert state.was_editable is False


class TestCaptureEditableState:
    """Tests for capture_editable_state function."""

    def test_captures_editable_state(self, tmp_path):
        """Test captures editable configuration from pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = ["djb>=0.2.6"]

[tool.uv.sources]
djb = { path = "djb", editable = true }
"""
        )

        uv_lock = tmp_path / "uv.lock"
        uv_lock.write_text('[[package]]\nname = "djb"\nsource = { editable = "djb" }\n')

        state = capture_editable_state(tmp_path)

        assert state.was_editable is True
        assert state.djb_source_config == {"path": "djb", "editable": True}
        assert state.djb_version_specifier == ">=0.2.6"
        assert state.uv_lock_content is not None
        assert "editable" in state.uv_lock_content

    def test_captures_non_editable_state(self, tmp_path):
        """Test captures state when djb is not editable."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = ["djb>=0.2.6"]
"""
        )

        state = capture_editable_state(tmp_path)

        assert state.was_editable is False
        assert state.djb_source_config is None

    def test_handles_missing_uv_lock(self, tmp_path):
        """Test handles missing uv.lock file."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "myproject"')

        state = capture_editable_state(tmp_path)

        assert state.uv_lock_content is None


class TestRemoveDjbSourceFromPyproject:
    """Tests for _remove_djb_source_from_pyproject function."""

    def test_removes_djb_line_from_sources(self):
        """Test removes djb entry from [tool.uv.sources]."""
        content = """
[project]
name = "myproject"

[tool.uv.sources]
djb = { path = "djb", editable = true }
other = { path = "other" }

[tool.other]
key = "value"
"""
        result = _remove_djb_source_from_pyproject(content)

        assert 'djb = { path = "djb"' not in result
        assert 'other = { path = "other" }' in result
        assert "[tool.uv.sources]" in result

    def test_removes_entire_section_when_only_djb(self):
        """Test removes entire [tool.uv.sources] section when only djb entry."""
        content = """
[project]
name = "myproject"

[tool.uv.sources]
djb = { path = "djb", editable = true }

[tool.other]
key = "value"
"""
        result = _remove_djb_source_from_pyproject(content)

        assert "[tool.uv.sources]" not in result
        assert 'djb = { path = "djb"' not in result
        assert "[tool.other]" in result

    def test_preserves_content_when_no_djb(self):
        """Test preserves content when no djb entry."""
        content = """
[project]
name = "myproject"
"""
        result = _remove_djb_source_from_pyproject(content)
        # Should be mostly unchanged
        assert "[project]" in result


class TestAddDjbSourceToPyproject:
    """Tests for _add_djb_source_to_pyproject function."""

    def test_adds_djb_to_existing_sources(self):
        """Test adds djb entry to existing [tool.uv.sources]."""
        content = """
[project]
name = "myproject"

[tool.uv.sources]
other = { path = "other" }
"""
        djb_config = {"path": "djb", "editable": True}

        result = _add_djb_source_to_pyproject(content, djb_config)

        assert 'djb = { path = "djb", editable = true }' in result
        assert "[tool.uv.sources]" in result

    def test_creates_sources_section_when_missing(self):
        """Test creates [tool.uv.sources] when it doesn't exist."""
        content = """
[project]
name = "myproject"

[tool.uv]
package = true

[tool.other]
key = "value"
"""
        djb_config = {"path": "djb", "editable": True}

        result = _add_djb_source_to_pyproject(content, djb_config)

        assert "[tool.uv.sources]" in result
        assert 'djb = { path = "djb", editable = true }' in result

    def test_creates_uv_and_sources_when_missing(self):
        """Test creates both [tool.uv] and sources when missing."""
        content = """
[project]
name = "myproject"
"""
        djb_config = {"path": "djb", "editable": True}

        result = _add_djb_source_to_pyproject(content, djb_config)

        assert "[tool.uv]" in result
        assert "[tool.uv.sources]" in result
        assert 'djb = { path = "djb", editable = true }' in result


class TestRemoveEditableConfig:
    """Tests for remove_editable_config function."""

    def test_removes_editable_config(self, tmp_path):
        """Test removes editable djb config from pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        original_content = """
[project]
name = "myproject"

[tool.uv.sources]
djb = { path = "djb", editable = true }
"""
        pyproject.write_text(original_content)

        state = EditableState(
            pyproject_content=original_content,
            uv_lock_content=None,
            djb_source_config={"path": "djb", "editable": True},
            djb_version_specifier=">=0.2.6",
        )

        remove_editable_config(tmp_path, state)

        new_content = pyproject.read_text()
        assert 'djb = { path = "djb"' not in new_content

    def test_does_nothing_when_not_editable(self, tmp_path):
        """Test does nothing when state was not editable."""
        pyproject = tmp_path / "pyproject.toml"
        original_content = '[project]\nname = "myproject"'
        pyproject.write_text(original_content)

        state = EditableState(
            pyproject_content=original_content,
            uv_lock_content=None,
            djb_source_config=None,
            djb_version_specifier=None,
        )

        remove_editable_config(tmp_path, state)

        # Should be unchanged
        assert pyproject.read_text() == original_content


class TestRestoreEditableConfig:
    """Tests for restore_editable_config function."""

    def test_restores_pyproject_content(self, tmp_path):
        """Test restores original pyproject.toml content."""
        pyproject = tmp_path / "pyproject.toml"
        original_content = """
[project]
name = "myproject"

[tool.uv.sources]
djb = { path = "djb", editable = true }
"""
        # Write different content to simulate modification
        pyproject.write_text('[project]\nname = "modified"')

        state = EditableState(
            pyproject_content=original_content,
            uv_lock_content=None,
            djb_source_config={"path": "djb", "editable": True},
            djb_version_specifier=">=0.2.6",
        )

        restore_editable_config(tmp_path, state)

        assert pyproject.read_text() == original_content

    def test_restores_uv_lock_content(self, tmp_path):
        """Test restores original uv.lock content."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("")

        uv_lock = tmp_path / "uv.lock"
        original_lock = '[[package]]\nname = "djb"\nsource = { editable = "djb" }\n'
        uv_lock.write_text("modified content")

        state = EditableState(
            pyproject_content="",
            uv_lock_content=original_lock,
            djb_source_config={"path": "djb", "editable": True},
            djb_version_specifier=">=0.2.6",
        )

        restore_editable_config(tmp_path, state)

        assert uv_lock.read_text() == original_lock


class TestStashedEditableContextManager:
    """Tests for stashed_editable context manager."""

    def test_stashes_and_restores_editable(self, tmp_path):
        """Test context manager removes and restores editable config."""
        pyproject = tmp_path / "pyproject.toml"
        original_content = """
[project]
name = "myproject"

[tool.uv.sources]
djb = { path = "djb", editable = true }
"""
        pyproject.write_text(original_content)

        uv_lock = tmp_path / "uv.lock"
        lock_content = '[[package]]\nname = "djb"\nsource = { editable = "djb" }\n'
        uv_lock.write_text(lock_content)

        with patch("djb.cli.editable_stash.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            with stashed_editable(tmp_path, quiet=True) as state:
                assert state.was_editable is True
                # Inside context: editable should be removed
                content = pyproject.read_text()
                assert 'djb = { path = "djb"' not in content

            # After context: editable should be restored
            content = pyproject.read_text()
            assert "[tool.uv.sources]" in content
            assert 'djb = { path = "djb"' in content or "editable" in content

    def test_restores_on_exception(self, tmp_path):
        """Test context manager restores state even on exception."""
        pyproject = tmp_path / "pyproject.toml"
        original_content = """
[project]
name = "myproject"

[tool.uv.sources]
djb = { path = "djb", editable = true }
"""
        pyproject.write_text(original_content)

        uv_lock = tmp_path / "uv.lock"
        uv_lock.write_text('[[package]]\nname = "djb"\nsource = { editable = "djb" }\n')

        with patch("djb.cli.editable_stash.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            with pytest.raises(ValueError):
                with stashed_editable(tmp_path, quiet=True):
                    raise ValueError("Test exception")

            # After exception: editable should still be restored
            content = pyproject.read_text()
            assert original_content == content

    def test_does_nothing_when_not_editable(self, tmp_path):
        """Test context manager does nothing when not in editable mode."""
        pyproject = tmp_path / "pyproject.toml"
        original_content = '[project]\nname = "myproject"'
        pyproject.write_text(original_content)

        with stashed_editable(tmp_path, quiet=True) as state:
            assert state.was_editable is False
            # Content should be unchanged
            assert pyproject.read_text() == original_content

        # Still unchanged after context
        assert pyproject.read_text() == original_content


class TestRestoreEditableWithCurrentVersion:
    """Tests for restore_editable_with_current_version function."""

    def test_adds_editable_config_preserving_current_version(self, tmp_path):
        """Test adds editable config while preserving the current pyproject.toml version."""
        pyproject = tmp_path / "pyproject.toml"
        # Current content has the NEW version (0.2.7) - simulating after version bump commit
        pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = ["djb>=0.2.7"]
"""
        )

        # Original state had OLD version (0.2.6) with editable source
        state = EditableState(
            pyproject_content="""
[project]
name = "myproject"
dependencies = ["djb>=0.2.6"]

[tool.uv.sources]
djb = { path = "djb", editable = true }
""",
            uv_lock_content='[[package]]\nname = "djb"\nsource = { editable = "djb" }\n',
            djb_source_config={"path": "djb", "editable": True},
            djb_version_specifier=">=0.2.6",
        )

        with patch("djb.cli.editable_stash.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            restore_editable_with_current_version(tmp_path, state)

        content = pyproject.read_text()
        # Should have added editable config
        assert "[tool.uv.sources]" in content
        assert 'djb = { path = "djb", editable = true }' in content
        # Version should still be the NEW version from current content (not restored to old)
        assert "0.2.7" in content
        assert "0.2.6" not in content


class TestStashRestoreRoundTrip:
    """Tests for the full stash/restore cycle to ensure no extra blank lines.

    The canonical format (matching what uv produces and expects) is:
    - No blank line between [tool.uv] contents and [tool.uv.sources]
    - No blank line between [tool.uv.sources] contents and next section
    """

    # Canonical format that uv produces (no blank lines around sources)
    CANONICAL_WITHOUT_SOURCES = """\
[project]
name = "myproject"
dependencies = ["djb>=0.2.6"]

[tool.uv]
package = true
[tool.setuptools]
packages = ["myproject"]
"""

    # Format with editable sources (no extra blank lines - matches uv's format)
    WITH_SOURCES = """\
[project]
name = "myproject"
dependencies = ["djb>=0.2.6"]

[tool.uv]
package = true
[tool.uv.sources]
djb = { path = "djb", editable = true }
[tool.setuptools]
packages = ["myproject"]
"""

    def test_remove_then_add_produces_same_result(self):
        """Test that remove followed by add produces consistent output."""
        # Start with editable config
        content_with_sources = self.WITH_SOURCES

        # Remove the sources section
        content_without = _remove_djb_source_from_pyproject(content_with_sources)

        # Should match canonical format (no extra blank lines)
        assert content_without == self.CANONICAL_WITHOUT_SOURCES

        # Add the sources back
        djb_config = {"path": "djb", "editable": True}
        content_restored = _add_djb_source_to_pyproject(content_without, djb_config)

        # Should match the original format
        assert content_restored == self.WITH_SOURCES

    def test_remove_does_not_leave_extra_blank_line(self):
        """Test that removing sources doesn't leave an extra blank line."""
        content = self.WITH_SOURCES
        result = _remove_djb_source_from_pyproject(content)

        # Check there's no blank line between [tool.uv] block and [tool.setuptools]
        lines = result.split("\n")
        for i, line in enumerate(lines):
            if line == "[tool.setuptools]":
                # Previous line should be "package = true", not blank
                assert lines[i - 1] == "package = true", (
                    f"Expected 'package = true' before [tool.setuptools], "
                    f"got '{lines[i - 1]}'"
                )
                break

    def test_add_inserts_sources_without_extra_blank_lines(self):
        """Test that adding sources doesn't add extra blank lines."""
        content = self.CANONICAL_WITHOUT_SOURCES
        djb_config = {"path": "djb", "editable": True}
        result = _add_djb_source_to_pyproject(content, djb_config)

        # Check [tool.uv.sources] comes right after "package = true"
        lines = result.split("\n")
        for i, line in enumerate(lines):
            if line == "[tool.uv.sources]":
                # Previous line should be "package = true" (no blank line)
                assert lines[i - 1] == "package = true", (
                    f"Expected 'package = true' before [tool.uv.sources], got '{lines[i - 1]}'"
                )
                break

    def test_multiple_round_trips_are_stable(self):
        """Test that multiple remove/add cycles produce stable output."""
        djb_config = {"path": "djb", "editable": True}

        # Start with sources
        content = self.WITH_SOURCES

        # Do multiple round trips
        for _ in range(3):
            content = _remove_djb_source_from_pyproject(content)
            assert content == self.CANONICAL_WITHOUT_SOURCES
            content = _add_djb_source_to_pyproject(content, djb_config)
            assert content == self.WITH_SOURCES

    def test_real_world_pyproject_format(self):
        """Test with a pyproject.toml format matching actual beachresort25 structure."""
        # This matches the actual committed format in beachresort25
        real_world_without_sources = """\
[project]
name = "beachresort25"
version = "0.1.0"
dependencies = ["djb>=0.2.18"]

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[tool.uv]
package = true
[tool.setuptools]
packages = ["beachresort25"]

[dependency-groups]
dev = ["pytest>=8.3.3"]
"""

        real_world_with_sources = """\
[project]
name = "beachresort25"
version = "0.1.0"
dependencies = ["djb>=0.2.18"]

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[tool.uv]
package = true
[tool.uv.sources]
djb = { path = "djb", editable = true }
[tool.setuptools]
packages = ["beachresort25"]

[dependency-groups]
dev = ["pytest>=8.3.3"]
"""

        djb_config = {"path": "djb", "editable": True}

        # Add sources to the clean version
        result = _add_djb_source_to_pyproject(real_world_without_sources, djb_config)
        assert result == real_world_with_sources

        # Remove sources should restore the clean version
        result = _remove_djb_source_from_pyproject(real_world_with_sources)
        assert result == real_world_without_sources
