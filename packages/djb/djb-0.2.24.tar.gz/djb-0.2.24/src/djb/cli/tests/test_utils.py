"""Tests for djb.cli.utils module."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import click
import pytest

from djb.cli.utils import (
    _get_clean_env,
    _run_streaming_threads,
    check_cmd,
    flatten_dict,
    run_cmd,
    run_streaming,
)


class TestGetCleanEnv:
    """Tests for _get_clean_env helper."""

    def test_returns_none_when_no_cwd(self):
        """Test returns None when cwd is None."""
        result = _get_clean_env(None)
        assert result is None

    def test_removes_virtual_env_when_cwd_provided(self, tmp_path):
        """Test removes VIRTUAL_ENV from environment when cwd is provided."""
        with patch.dict(os.environ, {"VIRTUAL_ENV": "/some/venv", "OTHER_VAR": "value"}):
            result = _get_clean_env(tmp_path)
            assert result is not None
            assert "VIRTUAL_ENV" not in result
            assert result["OTHER_VAR"] == "value"

    def test_works_without_virtual_env_set(self, tmp_path):
        """Test works when VIRTUAL_ENV is not in environment."""
        env_without_venv = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
        with patch.dict(os.environ, env_without_venv, clear=True):
            result = _get_clean_env(tmp_path)
            assert result is not None
            assert "VIRTUAL_ENV" not in result


class TestRunCmd:
    """Tests for run_cmd function."""

    def test_successful_command(self, tmp_path):
        """Test running a successful command."""
        result = run_cmd(["echo", "hello"], cwd=tmp_path)
        assert result.returncode == 0
        assert "hello" in result.stdout

    def test_successful_command_with_label(self, tmp_path):
        """Test running command with label logs correctly."""
        with patch("djb.cli.utils.logger") as mock_logger:
            result = run_cmd(["echo", "test"], cwd=tmp_path, label="Test command")
            assert result.returncode == 0
            mock_logger.next.assert_called_with("Test command")

    def test_successful_command_with_done_msg(self, tmp_path):
        """Test done message is logged on success."""
        with patch("djb.cli.utils.logger") as mock_logger:
            run_cmd(["echo", "test"], cwd=tmp_path, done_msg="All done!")
            mock_logger.done.assert_called_with("All done!")

    def test_quiet_mode_suppresses_logging(self, tmp_path):
        """Test quiet mode suppresses label and done_msg logging."""
        with patch("djb.cli.utils.logger") as mock_logger:
            run_cmd(
                ["echo", "test"],
                cwd=tmp_path,
                label="Should not log",
                done_msg="Should not log either",
                quiet=True,
            )
            mock_logger.next.assert_not_called()
            mock_logger.done.assert_not_called()

    def test_failed_command_with_halt_on_fail(self, tmp_path):
        """Test failed command raises ClickException when halt_on_fail=True."""
        with pytest.raises(click.ClickException):
            run_cmd(["false"], cwd=tmp_path, halt_on_fail=True)

    def test_failed_command_without_halt_on_fail(self, tmp_path):
        """Test failed command returns result when halt_on_fail=False."""
        result = run_cmd(["false"], cwd=tmp_path, halt_on_fail=False)
        assert result.returncode != 0

    def test_failed_command_logs_fail_msg(self, tmp_path):
        """Test failed command logs fail_msg when halt_on_fail=False."""
        with patch("djb.cli.utils.logger") as mock_logger:
            run_cmd(
                ["false"],
                cwd=tmp_path,
                halt_on_fail=False,
                fail_msg="Command failed!",
            )
            mock_logger.fail.assert_called_with("Command failed!")

    def test_failed_command_logs_stderr(self, tmp_path):
        """Test failed command logs stderr when halt_on_fail=False."""
        # Create a script that outputs to stderr
        script = tmp_path / "fail.sh"
        script.write_text("#!/bin/bash\necho 'error message' >&2\nexit 1")
        script.chmod(0o755)

        with patch("djb.cli.utils.logger") as mock_logger:
            run_cmd(
                [str(script)],
                cwd=tmp_path,
                halt_on_fail=False,
                fail_msg="Failed",
            )
            # Check that info was called with stderr content
            calls = [str(call) for call in mock_logger.info.call_args_list]
            assert any("error message" in call for call in calls)

    def test_failed_command_with_label_in_error(self, tmp_path):
        """Test failed command includes label in error message."""
        with pytest.raises(click.ClickException) as exc_info:
            run_cmd(["false"], cwd=tmp_path, label="My command", halt_on_fail=True)
        assert "My command" in str(exc_info.value)


class TestCheckCmd:
    """Tests for check_cmd function."""

    def test_returns_true_for_successful_command(self, tmp_path):
        """Test returns True when command succeeds."""
        result = check_cmd(["true"], cwd=tmp_path)
        assert result is True

    def test_returns_false_for_failed_command(self, tmp_path):
        """Test returns False when command fails."""
        result = check_cmd(["false"], cwd=tmp_path)
        assert result is False

    def test_works_with_real_command(self, tmp_path):
        """Test with a real command that produces output."""
        result = check_cmd(["echo", "test"], cwd=tmp_path)
        assert result is True


class TestRunStreaming:
    """Tests for run_streaming function."""

    def test_captures_stdout(self, tmp_path):
        """Test captures stdout from command."""
        returncode, stdout, stderr = run_streaming(["echo", "hello world"], cwd=tmp_path)
        assert returncode == 0
        assert "hello world" in stdout

    def test_captures_stderr(self, tmp_path):
        """Test captures stderr from command."""
        script = tmp_path / "stderr.sh"
        script.write_text("#!/bin/bash\necho 'error output' >&2")
        script.chmod(0o755)

        returncode, stdout, stderr = run_streaming([str(script)], cwd=tmp_path)
        assert returncode == 0
        assert "error output" in stderr

    def test_returns_nonzero_for_failed_command(self, tmp_path):
        """Test returns non-zero code for failed command."""
        returncode, stdout, stderr = run_streaming(["false"], cwd=tmp_path)
        assert returncode != 0

    def test_logs_label_when_provided(self, tmp_path):
        """Test logs label when provided."""
        with patch("djb.cli.utils.logger") as mock_logger:
            run_streaming(["echo", "test"], cwd=tmp_path, label="Running test")
            mock_logger.next.assert_called_with("Running test")

    def test_handles_mixed_stdout_stderr(self, tmp_path):
        """Test handles interleaved stdout and stderr."""
        script = tmp_path / "mixed.sh"
        script.write_text(
            "#!/bin/bash\n"
            "echo 'stdout line 1'\n"
            "echo 'stderr line 1' >&2\n"
            "echo 'stdout line 2'\n"
        )
        script.chmod(0o755)

        returncode, stdout, stderr = run_streaming([str(script)], cwd=tmp_path)
        assert returncode == 0
        assert "stdout line 1" in stdout
        assert "stdout line 2" in stdout
        assert "stderr line 1" in stderr

    def test_combine_output_returns_two_tuple(self, tmp_path):
        """Test combine_output=True returns (returncode, combined)."""
        script = tmp_path / "mixed.sh"
        script.write_text("#!/bin/bash\n" "echo 'stdout output'\n" "echo 'stderr output' >&2\n")
        script.chmod(0o755)

        returncode, combined = run_streaming([str(script)], cwd=tmp_path, combine_output=True)
        assert returncode == 0
        assert "stdout output" in combined
        assert "stderr output" in combined


class TestRunStreamingThreads:
    """Tests for _run_streaming_threads (Windows fallback).

    These tests run on all platforms to ensure the Windows code path is tested.
    """

    def test_captures_stdout(self, tmp_path):
        """Test captures stdout from command."""
        process = subprocess.Popen(
            ["echo", "hello world"],
            cwd=tmp_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        result = _run_streaming_threads(process, combine_output=False)
        assert len(result) == 3
        returncode, stdout, stderr = result
        assert returncode == 0
        assert "hello world" in stdout

    def test_captures_stderr(self, tmp_path):
        """Test captures stderr from command."""
        script = tmp_path / "stderr.sh"
        script.write_text("#!/bin/bash\necho 'error output' >&2")
        script.chmod(0o755)

        process = subprocess.Popen(
            [str(script)],
            cwd=tmp_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        result = _run_streaming_threads(process, combine_output=False)
        assert len(result) == 3
        returncode, stdout, stderr = result
        assert returncode == 0
        assert "error output" in stderr

    def test_handles_mixed_stdout_stderr(self, tmp_path):
        """Test handles interleaved stdout and stderr."""
        script = tmp_path / "mixed.sh"
        script.write_text(
            "#!/bin/bash\n"
            "echo 'stdout line 1'\n"
            "echo 'stderr line 1' >&2\n"
            "echo 'stdout line 2'\n"
        )
        script.chmod(0o755)

        process = subprocess.Popen(
            [str(script)],
            cwd=tmp_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        result = _run_streaming_threads(process, combine_output=False)
        assert len(result) == 3
        returncode, stdout, stderr = result
        assert returncode == 0
        assert "stdout line 1" in stdout
        assert "stdout line 2" in stdout
        assert "stderr line 1" in stderr

    def test_combine_output(self, tmp_path):
        """Test combine_output=True returns (returncode, combined)."""
        script = tmp_path / "mixed.sh"
        script.write_text("#!/bin/bash\necho 'stdout'\necho 'stderr' >&2\n")
        script.chmod(0o755)

        process = subprocess.Popen(
            [str(script)],
            cwd=tmp_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        result = _run_streaming_threads(process, combine_output=True)
        assert len(result) == 2
        returncode, combined = result
        assert returncode == 0
        assert "stdout" in combined
        assert "stderr" in combined


class TestFlattenDict:
    """Tests for flatten_dict function."""

    def test_empty_dict(self):
        """Test flattening empty dict."""
        result = flatten_dict({})
        assert result == {}

    def test_flat_dict(self):
        """Test flattening already flat dict."""
        result = flatten_dict({"key": "value", "other": "data"})
        assert result == {"KEY": "value", "OTHER": "data"}

    def test_nested_dict(self):
        """Test flattening nested dict."""
        result = flatten_dict({"db": {"host": "localhost", "port": 5432}})
        assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}

    def test_deeply_nested_dict(self):
        """Test flattening deeply nested dict."""
        result = flatten_dict({"a": {"b": {"c": "value"}}})
        assert result == {"A_B_C": "value"}

    def test_mixed_nesting(self):
        """Test flattening dict with mixed nesting levels."""
        result = flatten_dict(
            {
                "simple": "value",
                "nested": {"key": "data"},
                "deep": {"level1": {"level2": "deep_value"}},
            }
        )
        assert result == {
            "SIMPLE": "value",
            "NESTED_KEY": "data",
            "DEEP_LEVEL1_LEVEL2": "deep_value",
        }

    def test_converts_non_string_values(self):
        """Test converts non-string values to strings."""
        result = flatten_dict({"count": 42, "enabled": True, "ratio": 3.14})
        assert result == {"COUNT": "42", "ENABLED": "True", "RATIO": "3.14"}

    def test_uppercase_keys(self):
        """Test all keys are uppercased."""
        result = flatten_dict({"mixedCase": "value", "UPPER": "data", "lower": "test"})
        assert result == {"MIXEDCASE": "value", "UPPER": "data", "LOWER": "test"}
