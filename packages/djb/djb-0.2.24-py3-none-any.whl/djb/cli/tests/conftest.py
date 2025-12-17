"""Shared test fixtures for djb CLI tests.

This module provides common fixtures that are automatically available
to all test files in this directory.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from djb.cli.logging import setup_logging


@pytest.fixture(autouse=True)
def configure_logging():
    """Configure logging for all CLI tests.

    This fixture runs automatically before each test to ensure
    the djb CLI logging system is initialized. Without this,
    tests using CliRunner won't capture logger output.

    The logging is set to "info" level to capture standard output
    while excluding debug messages.
    """
    setup_logging("info")


@pytest.fixture
def runner():
    """Click CLI test runner.

    Returns a CliRunner instance for invoking Click commands
    in tests. The CliRunner captures stdout/stderr and provides
    access to exit codes and output.

    Example:
        def test_my_command(runner):
            result = runner.invoke(djb_cli, ["my-command"])
            assert result.exit_code == 0
            assert "expected output" in result.output
    """
    return CliRunner()


# =============================================================================
# Secrets Test Fixtures
# =============================================================================


@pytest.fixture
def secrets_dir(tmp_path: Path) -> Path:
    """Create a secrets directory for testing.

    Returns the path to a freshly created secrets/ directory inside tmp_path.
    """
    dir_path = tmp_path / "secrets"
    dir_path.mkdir()
    return dir_path


@pytest.fixture
def make_age_key(tmp_path: Path) -> Callable[[str], tuple[Path, str]]:
    """Factory fixture to create age key pairs.

    Returns a factory function that creates age key pairs with a given name.

    Example:
        def test_with_keys(make_age_key):
            alice_key_path, alice_public_key = make_age_key("alice")
            bob_key_path, bob_public_key = make_age_key("bob")
    """
    from djb.secrets import generate_age_key

    def _make_key(name: str) -> tuple[Path, str]:
        key_path = tmp_path / ".age" / f"{name}_keys.txt"
        key_path.parent.mkdir(parents=True, exist_ok=True)
        public_key, _ = generate_age_key(key_path)
        return key_path, public_key

    return _make_key


@pytest.fixture
def alice_key(make_age_key: Callable[[str], tuple[Path, str]]) -> tuple[Path, str]:
    """Create Alice's age key pair.

    Returns (key_path, public_key) tuple for Alice.
    """
    return make_age_key("alice")


@pytest.fixture
def bob_key(make_age_key: Callable[[str], tuple[Path, str]]) -> tuple[Path, str]:
    """Create Bob's age key pair.

    Returns (key_path, public_key) tuple for Bob.
    """
    return make_age_key("bob")


# =============================================================================
# Project Structure Fixtures
# =============================================================================

# Common pyproject.toml content for testing
DJB_PYPROJECT_CONTENT = '[project]\nname = "djb"\nversion = "0.1.0"\n'

EDITABLE_PYPROJECT_TEMPLATE = """\
[project]
name = "myproject"

[tool.uv.sources]
djb = {{ path = "{path}", editable = true }}
"""


def make_editable_pyproject(djb_path: str = "djb") -> str:
    """Generate editable pyproject.toml content with given djb path."""
    return EDITABLE_PYPROJECT_TEMPLATE.format(path=djb_path)


@pytest.fixture
def djb_project(tmp_path: Path) -> Path:
    """Create a minimal djb project directory.

    Creates tmp_path/djb/ with a valid pyproject.toml.
    Returns the djb directory path.
    """
    djb_dir = tmp_path / "djb"
    djb_dir.mkdir()
    (djb_dir / "pyproject.toml").write_text(DJB_PYPROJECT_CONTENT)
    return djb_dir


@pytest.fixture
def host_with_editable_djb(tmp_path: Path, djb_project: Path) -> Path:
    """Create a host project with djb in editable mode.

    Creates:
    - tmp_path/djb/ (via djb_project fixture)
    - tmp_path/pyproject.toml with [tool.uv.sources] pointing to djb

    Returns the host project path (tmp_path).
    """
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(make_editable_pyproject("djb"))
    return tmp_path


@pytest.fixture
def setup_sops_config(secrets_dir: Path) -> Callable[[dict[str, str]], Path]:
    """Factory fixture to create .sops.yaml configuration.

    Returns a factory function that creates a .sops.yaml file with the given
    recipients (mapping public_key -> email).

    Example:
        def test_sops(setup_sops_config, alice_key):
            _, alice_public = alice_key
            setup_sops_config({alice_public: "alice@example.com"})
    """
    from djb.secrets.core import create_sops_config

    def _setup(recipients: dict[str, str]) -> Path:
        return create_sops_config(secrets_dir, recipients)

    return _setup
