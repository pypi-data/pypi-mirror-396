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
    update_and_restore_editable,
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


class TestUpdateAndRestoreEditable:
    """Tests for update_and_restore_editable function."""

    def test_restores_editable_config(self, tmp_path):
        """Test restores editable config to current pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        # Current content (maybe version was updated)
        pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = ["djb>=0.2.7"]
"""
        )

        uv_lock = tmp_path / "uv.lock"
        original_lock = '[[package]]\nname = "djb"\nsource = { editable = "djb" }\n'

        state = EditableState(
            pyproject_content="""
[project]
name = "myproject"
dependencies = ["djb>=0.2.6"]

[tool.uv.sources]
djb = { path = "djb", editable = true }
""",
            uv_lock_content=original_lock,
            djb_source_config={"path": "djb", "editable": True},
            djb_version_specifier=">=0.2.6",
        )

        with patch("djb.cli.editable_stash.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            update_and_restore_editable(tmp_path, state, "0.2.7")

        content = pyproject.read_text()
        # Should have added editable config to current content
        assert "[tool.uv.sources]" in content
        assert 'djb = { path = "djb", editable = true }' in content
        # Version should still be the updated one from current content
        assert "0.2.7" in content
