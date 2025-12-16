"""
Stash/restore editable djb configuration.

Provides a clean way to temporarily remove editable djb configuration from
pyproject.toml and uv.lock for operations that need to push/commit clean files
(like deploy and publish), then restore the editable state afterward.

This approach avoids the complexity of using uv commands which can have caching
issues and require polling PyPI.
"""

from __future__ import annotations

import re
import subprocess
import tomllib
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import click


@dataclass
class EditableState:
    """Captured state of editable djb configuration."""

    pyproject_content: str
    uv_lock_content: str | None
    djb_source_config: dict | None
    djb_version_specifier: str | None

    @property
    def was_editable(self) -> bool:
        """Check if djb was in editable mode."""
        if self.djb_source_config is None:
            return False
        return self.djb_source_config.get("editable", False)


def _get_djb_source_config(pyproject_path: Path) -> dict | None:
    """Get the djb source configuration from pyproject.toml.

    Reads [tool.uv.sources.djb] from pyproject.toml if present.
    """
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError):
        return None

    tool = data.get("tool", {})
    uv = tool.get("uv", {})
    sources = uv.get("sources", {})
    return sources.get("djb")


def _get_djb_version_specifier(pyproject_path: Path) -> str | None:
    """Get the djb version specifier from pyproject.toml dependencies.

    Returns the version specifier (e.g., ">=0.2.6") or None if not found.
    """
    content = pyproject_path.read_text()
    match = re.search(r'["\']djb(>=[\d.]+)["\']', content)
    if match:
        return match.group(1)
    return None


def _remove_djb_source_from_pyproject(content: str) -> str:
    """Remove [tool.uv.sources].djb from pyproject.toml content.

    Handles the TOML format carefully to preserve other content.
    """
    lines = content.splitlines(keepends=True)
    result_lines = []
    in_sources_section = False
    skip_next_blank = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Track when we enter [tool.uv.sources]
        if stripped == "[tool.uv.sources]":
            in_sources_section = True
            # Check if this section only contains djb
            # Look ahead to see what's in this section
            j = i + 1
            section_lines = []
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith("[") and not next_line.startswith("[["):
                    break  # Hit next section
                if next_line and not next_line.startswith("#"):
                    section_lines.append(next_line)
                j += 1

            # If only djb entry, skip the entire section
            if len(section_lines) == 1 and section_lines[0].startswith("djb"):
                # Skip to the next section
                i = j
                skip_next_blank = True
                continue
            else:
                # Keep the section header, will remove just the djb line
                result_lines.append(line)
                i += 1
                continue

        # Skip djb entry in [tool.uv.sources]
        if in_sources_section and stripped.startswith("djb"):
            i += 1
            skip_next_blank = True
            continue

        # Detect leaving the sources section
        if in_sources_section and stripped.startswith("[") and not stripped.startswith("[["):
            in_sources_section = False

        # Skip blank line after removed content
        if skip_next_blank and not stripped:
            skip_next_blank = False
            i += 1
            continue

        skip_next_blank = False
        result_lines.append(line)
        i += 1

    return "".join(result_lines)


def _add_djb_source_to_pyproject(content: str, djb_config: dict) -> str:
    """Add [tool.uv.sources].djb back to pyproject.toml content."""
    # Format the djb source line
    if djb_config.get("editable"):
        djb_line = f'djb = {{ path = "{djb_config["path"]}", editable = true }}'
    else:
        djb_line = f'djb = {{ path = "{djb_config["path"]}" }}'

    # Check if [tool.uv.sources] section exists
    if "[tool.uv.sources]" in content:
        # Add djb line after the section header
        return content.replace(
            "[tool.uv.sources]\n",
            f"[tool.uv.sources]\n{djb_line}\n",
        )
    else:
        # Check if [tool.uv] section exists
        if "[tool.uv]" in content:
            # Find [tool.uv] and add sources section after it
            lines = content.splitlines(keepends=True)
            result_lines = []
            found_tool_uv = False
            added_sources = False

            for i, line in enumerate(lines):
                result_lines.append(line)
                stripped = line.strip()

                if stripped == "[tool.uv]":
                    found_tool_uv = True
                    continue

                # After [tool.uv], find the next section and insert before it
                if found_tool_uv and not added_sources:
                    if stripped.startswith("[") and not stripped.startswith("[["):
                        # Insert before this new section
                        result_lines.insert(
                            len(result_lines) - 1,
                            f"\n[tool.uv.sources]\n{djb_line}\n",
                        )
                        added_sources = True

            # If we didn't find another section, add at the end of [tool.uv]
            if found_tool_uv and not added_sources:
                result_lines.append(f"\n[tool.uv.sources]\n{djb_line}\n")

            return "".join(result_lines)
        else:
            # No [tool.uv] section, add both
            return content + f"\n[tool.uv]\npackage = true\n\n[tool.uv.sources]\n{djb_line}\n"


def capture_editable_state(repo_root: Path) -> EditableState:
    """Capture the current editable djb state.

    Saves the original pyproject.toml and uv.lock content so they can be
    restored later.
    """
    pyproject_path = repo_root / "pyproject.toml"
    uv_lock_path = repo_root / "uv.lock"

    pyproject_content = pyproject_path.read_text() if pyproject_path.exists() else ""
    uv_lock_content = uv_lock_path.read_text() if uv_lock_path.exists() else None

    djb_config = _get_djb_source_config(pyproject_path) if pyproject_path.exists() else None
    version_spec = _get_djb_version_specifier(pyproject_path) if pyproject_path.exists() else None

    return EditableState(
        pyproject_content=pyproject_content,
        uv_lock_content=uv_lock_content,
        djb_source_config=djb_config,
        djb_version_specifier=version_spec,
    )


def remove_editable_config(repo_root: Path, state: EditableState) -> None:
    """Remove editable djb configuration from pyproject.toml.

    Modifies pyproject.toml to remove the [tool.uv.sources].djb entry.
    Does NOT modify uv.lock - that will be handled separately if needed.
    """
    if not state.was_editable:
        return

    pyproject_path = repo_root / "pyproject.toml"
    new_content = _remove_djb_source_from_pyproject(state.pyproject_content)
    pyproject_path.write_text(new_content)


def restore_editable_config(repo_root: Path, state: EditableState) -> None:
    """Restore the original editable djb configuration.

    Restores both pyproject.toml and uv.lock to their original state.
    """
    pyproject_path = repo_root / "pyproject.toml"
    uv_lock_path = repo_root / "uv.lock"

    # Restore pyproject.toml
    pyproject_path.write_text(state.pyproject_content)

    # Restore uv.lock if we had one
    if state.uv_lock_content is not None:
        uv_lock_path.write_text(state.uv_lock_content)


def restore_editable_with_current_version(repo_root: Path, state: EditableState) -> None:
    """Re-enable editable mode while keeping the current pyproject.toml version.

    Used by publish after committing the version bump. This:
    1. Reads the CURRENT pyproject.toml (which has the new version from the commit)
    2. Adds back the [tool.uv.sources] editable config
    3. Regenerates uv.lock to point to local editable djb

    This is NOT a simple restore - the version in pyproject.toml is preserved
    (e.g., djb>=0.2.14), only the editable source config is added back.
    """
    pyproject_path = repo_root / "pyproject.toml"

    # Read the CURRENT pyproject.toml (which has the new version after commit)
    current_content = pyproject_path.read_text()

    # Add back the editable source config
    if state.was_editable and state.djb_source_config:
        current_content = _add_djb_source_to_pyproject(current_content, state.djb_source_config)
        pyproject_path.write_text(current_content)

    # Bust uv cache for djb so next uv command works correctly
    bust_uv_cache()

    # Regenerate uv.lock with editable source pointing to local djb (now at new version)
    regenerate_uv_lock(repo_root)


def bust_uv_cache() -> None:
    """Clear uv's cache for djb to ensure fresh resolution."""
    subprocess.run(
        ["uv", "cache", "clean", "djb"],
        capture_output=True,
        text=True,
    )


def regenerate_uv_lock(repo_root: Path) -> bool:
    """Regenerate uv.lock with the current pyproject.toml.

    Returns True on success, False on failure.
    """
    result = subprocess.run(
        ["uv", "lock", "--refresh"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


@contextmanager
def stashed_editable(repo_root: Path, quiet: bool = False):
    """Context manager to temporarily remove editable djb configuration.

    Usage:
        with stashed_editable(repo_root) as state:
            # pyproject.toml no longer has editable config
            # do git operations here
            pass
        # editable config is restored

    The state object is yielded so callers can check state.was_editable
    and access the original configuration if needed.

    If an exception occurs, the original state is still restored.
    """
    state = capture_editable_state(repo_root)

    if state.was_editable:
        if not quiet:
            click.echo("Temporarily removing editable djb configuration...")
        remove_editable_config(repo_root, state)

    try:
        yield state
    finally:
        if state.was_editable:
            if not quiet:
                click.echo("Restoring editable djb configuration...")
            restore_editable_config(repo_root, state)
            bust_uv_cache()
