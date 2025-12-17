"""Utility functions for djb CLI."""

from __future__ import annotations

import os
import select
import subprocess
import sys
import threading
from pathlib import Path
from typing import BinaryIO, Literal, overload

import click

from djb.cli.logging import get_logger
from djb.types import NestedDict

logger = get_logger(__name__)

# select.poll() is not available on Windows
_HAS_POLL = hasattr(select, "poll")

# Buffer size for reading subprocess output
_READ_BUFFER_SIZE = 4096


def _get_clean_env(cwd: Path | None) -> dict[str, str] | None:
    """Get environment with VIRTUAL_ENV cleared if running in a different directory.

    When running commands in a different project directory (e.g., djb editable from host),
    the inherited VIRTUAL_ENV would point to the wrong venv and cause uv to emit:

        warning: `VIRTUAL_ENV=...` does not match the project environment path `.venv`
        and will be ignored; use `--active` to target the active environment instead

    Clearing VIRTUAL_ENV lets uv auto-detect the correct .venv for the target directory.
    """
    if cwd is None:
        return None
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    return env


def run_cmd(
    cmd: list[str],
    cwd: Path | None = None,
    label: str | None = None,
    done_msg: str | None = None,
    fail_msg: str | None = None,
    halt_on_fail: bool = True,
    quiet: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a shell command with optional error handling.

    Args:
        cmd: Command and arguments to run
        cwd: Working directory
        label: Human-readable label (logged with logger.next)
        done_msg: Success message (logged with logger.done)
        fail_msg: Failure message (logged with logger.fail if halt_on_fail=False)
        halt_on_fail: Whether to raise ClickException on failure
        quiet: Suppress all logging output (except for halt_on_fail errors)

    Returns:
        CompletedProcess with stdout/stderr as text
    """
    if label and not quiet:
        logger.next(label)
    logger.debug(f"Executing: {' '.join(cmd)}")
    env = _get_clean_env(cwd)
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        if halt_on_fail:
            logger.error(f"{label or 'Command'} failed with exit code {result.returncode}")
            if result.stderr:
                logger.debug(result.stderr)
            raise click.ClickException(f"{label or 'Command'} failed")
        elif fail_msg and not quiet:
            logger.fail(fail_msg)
            if result.stderr:
                logger.info(f"  {result.stderr.strip()}")
    if done_msg and result.returncode == 0 and not quiet:
        logger.done(done_msg)
    return result


def check_cmd(cmd: list[str], cwd: Path | None = None) -> bool:
    """Check if a command succeeds (returns True if exit code is 0).

    Useful for checking if something is installed or available.
    """
    result = subprocess.run(cmd, cwd=cwd, capture_output=True)
    return result.returncode == 0


@overload
def run_streaming(
    cmd: list[str],
    cwd: Path | None = ...,
    label: str | None = ...,
    *,
    combine_output: Literal[True],
) -> tuple[int, str]: ...


@overload
def run_streaming(
    cmd: list[str],
    cwd: Path | None = ...,
    label: str | None = ...,
    combine_output: Literal[False] = ...,
) -> tuple[int, str, str]: ...


def run_streaming(
    cmd: list[str],
    cwd: Path | None = None,
    label: str | None = None,
    combine_output: bool = False,
) -> tuple[int, str, str] | tuple[int, str]:
    """Run a command while streaming output to terminal and capturing it.

    Uses select.poll() (Unix) or threads (Windows) for non-blocking I/O to stream
    both stdout and stderr to the terminal in real-time while capturing them.

    Args:
        cmd: Command and arguments to run
        cwd: Working directory
        label: Optional label to print before running
        combine_output: If True, return combined stdout+stderr as single string

    Returns:
        If combine_output=False: Tuple of (return_code, captured_stdout, captured_stderr)
        If combine_output=True: Tuple of (return_code, combined_output)
    """
    if label:
        logger.next(label)

    env = _get_clean_env(cwd)
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert process.stdout is not None
    assert process.stderr is not None

    if _HAS_POLL:
        return _run_streaming_poll(process, combine_output)
    else:
        return _run_streaming_threads(process, combine_output)


def _run_streaming_poll(
    process: subprocess.Popen[bytes],
    combine_output: bool,
) -> tuple[int, str, str] | tuple[int, str]:
    """Stream output using select.poll() (Unix)."""
    assert process.stdout is not None
    assert process.stderr is not None

    # Get file descriptors for polling
    stdout_fd = process.stdout.fileno()
    stderr_fd = process.stderr.fileno()

    # Set up polling
    poller = select.poll()
    poller.register(stdout_fd, select.POLLIN)
    poller.register(stderr_fd, select.POLLIN)

    stdout_chunks: list[bytes] = []
    stderr_chunks: list[bytes] = []
    open_fds = {stdout_fd, stderr_fd}

    while open_fds:
        # Poll with 100ms timeout
        events = poller.poll(100)

        for fd, event in events:
            if event & select.POLLIN:
                chunk = os.read(fd, _READ_BUFFER_SIZE)
                if chunk:
                    # Write to appropriate output stream
                    if fd == stdout_fd:
                        sys.stdout.buffer.write(chunk)
                        sys.stdout.buffer.flush()
                        stdout_chunks.append(chunk)
                    else:
                        sys.stderr.buffer.write(chunk)
                        sys.stderr.buffer.flush()
                        stderr_chunks.append(chunk)
                else:
                    # EOF on this fd
                    poller.unregister(fd)
                    open_fds.discard(fd)
            elif event & (select.POLLHUP | select.POLLERR):
                poller.unregister(fd)
                open_fds.discard(fd)

        # Check if process has exited
        if process.poll() is not None and not events:
            # Process done and no more data, drain any remaining
            for fd in list(open_fds):
                try:
                    while True:
                        chunk = os.read(fd, _READ_BUFFER_SIZE)
                        if not chunk:
                            break
                        if fd == stdout_fd:
                            sys.stdout.buffer.write(chunk)
                            sys.stdout.buffer.flush()
                            stdout_chunks.append(chunk)
                        else:
                            sys.stderr.buffer.write(chunk)
                            sys.stderr.buffer.flush()
                            stderr_chunks.append(chunk)
                except OSError:
                    pass
                poller.unregister(fd)
                open_fds.discard(fd)

    process.wait()
    stdout = b"".join(stdout_chunks).decode(errors="replace")
    stderr = b"".join(stderr_chunks).decode(errors="replace")
    if combine_output:
        return process.returncode, stdout + stderr
    return process.returncode, stdout, stderr


def _run_streaming_threads(
    process: subprocess.Popen[bytes],
    combine_output: bool,
) -> tuple[int, str, str] | tuple[int, str]:
    """Stream output using threads (Windows fallback).

    On Windows, select.poll() is not available and select.select() only works
    with sockets, not pipes. This implementation uses threads to read from
    stdout and stderr concurrently.
    """
    assert process.stdout is not None
    assert process.stderr is not None

    stdout_chunks: list[bytes] = []
    stderr_chunks: list[bytes] = []
    lock = threading.Lock()

    def read_stream(
        stream: BinaryIO,
        chunks: list[bytes],
        output_buffer: BinaryIO,
    ) -> None:
        """Read from stream and write to output buffer."""
        while True:
            chunk = stream.read(_READ_BUFFER_SIZE)
            if not chunk:
                break
            with lock:
                output_buffer.write(chunk)
                output_buffer.flush()
                chunks.append(chunk)

    stdout_thread = threading.Thread(
        target=read_stream,
        args=(process.stdout, stdout_chunks, sys.stdout.buffer),
    )
    stderr_thread = threading.Thread(
        target=read_stream,
        args=(process.stderr, stderr_chunks, sys.stderr.buffer),
    )

    stdout_thread.start()
    stderr_thread.start()
    stdout_thread.join()
    stderr_thread.join()

    process.wait()
    stdout = b"".join(stdout_chunks).decode(errors="replace")
    stderr = b"".join(stderr_chunks).decode(errors="replace")
    if combine_output:
        return process.returncode, stdout + stderr
    return process.returncode, stdout, stderr


def flatten_dict(d: NestedDict, parent_key: str = "") -> dict[str, str]:
    """Flatten a nested dictionary into a flat dict with uppercase keys.

    Nested keys are joined with underscores. All values are converted to strings.

    Args:
        d: Dictionary to flatten
        parent_key: Prefix for all keys (used during recursion)

    Returns:
        Flat dictionary with uppercase keys

    Example:
        >>> flatten_dict({"db": {"host": "localhost", "port": 5432}})
        {"DB_HOST": "localhost", "DB_PORT": "5432"}
    """
    items: list[tuple[str, str]] = []
    for key, value in d.items():
        new_key = f"{parent_key}_{key}".upper() if parent_key else key.upper()
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key).items())
        else:
            items.append((new_key, str(value)))
    return dict(items)
