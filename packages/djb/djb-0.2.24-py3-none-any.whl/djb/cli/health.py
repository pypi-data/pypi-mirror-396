"""Health check commands for running lint, typecheck, and tests."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import NamedTuple

import click

from djb.cli.context import CliContext, CliHealthContext
from djb.cli.editable import (
    find_djb_dir,
    get_djb_source_path,
    is_djb_editable,
    is_djb_package_dir,
)
from djb.cli.find_overlap import run_find_overlap
from djb.cli.logging import get_logger
from djb.config import get_project_name
from djb.cli.utils import run_cmd, run_streaming

logger = get_logger(__name__)


def _has_pytest_cov(project_root: Path) -> bool:
    """Check if pytest-cov is available in the project's environment."""
    try:
        result = subprocess.run(
            ["uv", "run", "python", "-c", "import pytest_cov"],
            cwd=project_root,
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


class HealthStep(NamedTuple):
    """A single health check step to execute."""

    label: str
    cmd: list[str]
    cwd: Path | None = None


class ProjectContext(NamedTuple):
    """Context for which projects to run health checks on."""

    djb_path: Path | None  # Path to djb if we should check it
    host_path: Path | None  # Path to host project if we should check it
    inside_djb: bool  # True if running from inside djb directory


class StepFailure(NamedTuple):
    """A failed health check step with captured output."""

    label: str
    returncode: int
    stdout: str
    stderr: str


def _is_inside_djb_dir(path: Path) -> bool:
    """Check if the given path is inside the djb project directory."""
    return is_djb_package_dir(path)


def _get_cli_context(ctx: click.Context) -> CliContext:
    """Get the CliContext from click context, with type assertion."""
    assert isinstance(ctx.obj, CliContext), "Expected CliContext at ctx.obj"
    return ctx.obj


def _get_health_context(ctx: click.Context) -> CliHealthContext:
    """Get the CliHealthContext from click context, with type assertion."""
    assert isinstance(ctx.obj, CliHealthContext), "Expected CliHealthContext at ctx.obj"
    return ctx.obj


def _get_run_scopes(scope_frontend: bool, scope_backend: bool) -> tuple[bool, bool]:
    """Determine which scopes to run based on flags.

    Args:
        scope_frontend: Whether --frontend flag was set
        scope_backend: Whether --backend flag was set

    Returns:
        Tuple of (run_backend, run_frontend). If neither flag is set, both are True.
    """
    neither_specified = not scope_frontend and not scope_backend
    run_frontend = scope_frontend or neither_specified
    run_backend = scope_backend or neither_specified
    return run_backend, run_frontend


def _get_project_context(ctx: click.Context) -> ProjectContext:
    """Determine which projects to run health checks on.

    Returns a ProjectContext with:
    - djb_path: Path to djb if we should check it (editable or inside djb)
    - host_path: Path to host project if we should check it
    - inside_djb: True if running from inside djb directory

    Logic:
    1. If running from inside djb directory: only check djb, skip host
    2. If djb is editable in host project: check djb first, then host
    3. Otherwise: just check the current project (host)
    """
    cli_ctx = _get_cli_context(ctx)
    config = cli_ctx.config
    project_root = (config.project_dir if config and config.project_dir else None) or Path.cwd()

    # Check if we're inside the djb directory
    if _is_inside_djb_dir(project_root):
        return ProjectContext(djb_path=project_root, host_path=None, inside_djb=True)

    # Check if djb is installed in editable mode
    if is_djb_editable(project_root):
        djb_source = get_djb_source_path(project_root)
        if djb_source:
            djb_path = (project_root / djb_source).resolve()
            return ProjectContext(djb_path=djb_path, host_path=project_root, inside_djb=False)

    # Default: just check the host project
    return ProjectContext(djb_path=None, host_path=project_root, inside_djb=False)


def _get_project_root(ctx: click.Context) -> Path:
    """Get project root from context config."""
    cli_ctx = _get_cli_context(ctx)
    if cli_ctx.config and cli_ctx.config.project_dir:
        return cli_ctx.config.project_dir
    return Path.cwd()


def _get_frontend_dir(project_root: Path) -> Path:
    """Get frontend directory path."""
    return project_root / "frontend"


def _get_host_display_name(host_path: Path) -> str:
    """Get the display name for the host project.

    Uses the configured project name if available, otherwise falls back to directory name.
    """
    return get_project_name(host_path) or host_path.name


def _run_steps(
    steps: list[HealthStep], quiet: bool = False, verbose: bool = False
) -> list[StepFailure]:
    """Run health check steps and return failures.

    Args:
        steps: List of health check steps to run
        quiet: Suppress all output
        verbose: Stream output in real-time (shows failures inline)

    Returns:
        List of StepFailure for any failed steps
    """
    failures: list[StepFailure] = []

    for step in steps:
        if verbose:
            # Stream output in real-time
            returncode, stdout, stderr = run_streaming(
                step.cmd,
                cwd=step.cwd,
                label=step.label,
            )
            if returncode != 0:
                logger.fail(f"{step.label} failed (exit {returncode})")
                failures.append(StepFailure(step.label, returncode, stdout, stderr))
        else:
            # Capture output (quiet or normal mode)
            result = run_cmd(
                step.cmd,
                cwd=step.cwd,
                label=step.label,
                halt_on_fail=False,
                quiet=quiet,
            )
            if result.returncode != 0:
                if not quiet:
                    logger.fail(f"{step.label} failed (exit {result.returncode})")
                failures.append(
                    StepFailure(step.label, result.returncode, result.stdout, result.stderr)
                )

    return failures


def _get_command_with_flag(
    flag: str, skip_if_present: list[str] | None = None, append: bool = False
) -> str:
    """Construct a command string with a flag added.

    Uses sys.argv to get the original command and adds the flag.
    Always uses 'djb' as the program name regardless of how it was invoked.

    Args:
        flag: The flag to add (e.g., "-v" or "--fix")
        skip_if_present: List of flags that, if already present, skip insertion
        append: If True, append at end (for subcommand flags like --fix).
                If False, insert after 'djb' (for global flags like -v).
    """
    import sys

    args = sys.argv[:]

    # Replace full path with just 'djb'
    args[0] = "djb"

    # Skip if any of the specified flags are already present
    if skip_if_present and any(f in args for f in skip_if_present):
        return " ".join(args)

    if append:
        # Append at end (for subcommand flags like --fix)
        args.append(flag)
    else:
        # Insert after program name (for global flags like -v)
        if len(args) > 1:
            args.insert(1, flag)
        else:
            args.append(flag)

    return " ".join(args)


def _report_failures(
    failures: list[StepFailure],
    fix: bool = False,
    verbose: bool = False,
) -> None:
    """Report failures and raise exception if any."""
    if failures:
        logger.info("")
        logger.fail("Health checks completed with failures:")
        for failure in failures:
            logger.fail(f"{failure.label} (exit {failure.returncode})")

        if verbose:
            logger.info("")
            logger.warning("=" * 60)
            logger.warning("Failure details:")
            logger.warning("=" * 60)
            for failure in failures:
                logger.warning(f"\n--- {failure.label} ---")
                if failure.stdout:
                    logger.info(failure.stdout)
                if failure.stderr:
                    logger.info(failure.stderr)

        # Show tips for how to fix or get more info
        tips: list[str] = []

        if not verbose:
            verbose_cmd = _get_command_with_flag("-v", skip_if_present=["-v", "--verbose"])
            tips.append(f"re-run with -v to see error details: {verbose_cmd}")

        if not fix:
            fix_cmd = _get_command_with_flag("--fix", skip_if_present=["--fix"], append=True)
            tips.append(f"re-run with --fix to attempt auto-fixes for lint issues: {fix_cmd}")

        if tips:
            logger.info("")
            for tip in tips:
                logger.tip(tip)

        raise click.ClickException("Health checks failed")

    logger.done("Health checks passed")


def _build_backend_lint_steps(
    project_root: Path, fix: bool, prefix: str, scope: str
) -> list[HealthStep]:
    """Build backend lint steps for a project."""
    label_prefix = f"{prefix} " if prefix else ""
    if fix:
        return [
            HealthStep(
                f"{label_prefix}{scope} format (black)", ["uv", "run", "black", "."], project_root
            )
        ]
    return [
        HealthStep(
            f"{label_prefix}{scope} lint (black --check)",
            ["uv", "run", "black", "--check", "."],
            project_root,
        )
    ]


def _build_backend_typecheck_steps(project_root: Path, prefix: str, scope: str) -> list[HealthStep]:
    """Build backend typecheck steps for a project."""
    label_prefix = f"{prefix} " if prefix else ""
    return [
        HealthStep(
            f"{label_prefix}{scope} typecheck (pyright)", ["uv", "run", "pyright"], project_root
        )
    ]


def _build_backend_test_steps(
    project_root: Path, prefix: str, scope: str, cov: bool = False
) -> list[HealthStep]:
    """Build backend test steps for a project."""
    label_prefix = f"{prefix} " if prefix else ""
    cmd = ["uv", "run", "pytest"]
    label_suffix = ""

    if cov:
        if _has_pytest_cov(project_root):
            cmd.extend(["--cov", "--cov-report=term-missing"])
            label_suffix = " with coverage"
        else:
            logger.notice(
                f"pytest-cov not installed in {project_root.name}, "
                "skipping coverage. Run: uv add --dev pytest-cov"
            )

    return [
        HealthStep(
            f"{label_prefix}{scope} tests (pytest{label_suffix})",
            cmd,
            project_root,
        )
    ]


def _build_backend_coverage_steps(project_root: Path, prefix: str, scope: str) -> list[HealthStep]:
    """Build backend coverage steps for a project."""
    label_prefix = f"{prefix} " if prefix else ""
    return [
        HealthStep(
            f"{label_prefix}{scope} coverage (pytest --cov)",
            ["uv", "run", "pytest", "--cov", "--cov-report=term-missing"],
            project_root,
        )
    ]


def _build_frontend_lint_steps(frontend_dir: Path, fix: bool, prefix: str = "") -> list[HealthStep]:
    """Build frontend lint steps for a project."""
    if not frontend_dir.exists():
        return []
    label_prefix = f"{prefix} " if prefix else ""
    if fix:
        return [
            HealthStep(
                f"{label_prefix}Frontend lint (bun lint --fix)",
                ["bun", "run", "lint", "--fix"],
                frontend_dir,
            )
        ]
    return [
        HealthStep(f"{label_prefix}Frontend lint (bun lint)", ["bun", "run", "lint"], frontend_dir)
    ]


def _build_frontend_typecheck_steps(frontend_dir: Path, prefix: str = "") -> list[HealthStep]:
    """Build frontend typecheck steps for a project."""
    if not frontend_dir.exists():
        return []
    label_prefix = f"{prefix} " if prefix else ""
    return [
        HealthStep(f"{label_prefix}Frontend typecheck (tsc)", ["bun", "run", "tsc"], frontend_dir)
    ]


def _build_frontend_test_steps(frontend_dir: Path, prefix: str = "") -> list[HealthStep]:
    """Build frontend test steps for a project."""
    if not frontend_dir.exists():
        return []
    label_prefix = f"{prefix} " if prefix else ""
    return [HealthStep(f"{label_prefix}Frontend tests (bun test)", ["bun", "test"], frontend_dir)]


def _build_e2e_steps(project_root: Path, prefix: str = "") -> list[HealthStep]:
    """Build E2E test steps for a project."""
    label_prefix = f"{prefix} " if prefix else ""
    return [
        HealthStep(
            f"{label_prefix}E2E tests (pytest --run-e2e)",
            ["uv", "run", "pytest", "--run-e2e"],
            project_root,
        )
    ]


@click.group(invoke_without_command=True)
@click.option(
    "--fix",
    is_flag=True,
    help="Attempt to auto-fix lint/format issues.",
)
@click.option(
    "--cov",
    is_flag=True,
    help="Enable code coverage reporting for tests.",
)
@click.pass_context
def health(ctx: click.Context, fix: bool, cov: bool):
    """Run health checks: lint, typecheck, and tests.

    \b
    When run without a subcommand, executes all checks:
      • Linting (black for backend, bun lint for frontend)
      • Type checking (pyright for backend, tsc for frontend)
      • Tests (pytest for backend, bun test for frontend)

    \b
    Subcommands:
      lint       Run linting only
      typecheck  Run type checking only
      test       Run tests only
      e2e        Run E2E tests only

    \b
    Examples:
      djb health                    # Run all checks
      djb --backend health          # Backend checks only
      djb --frontend health         # Frontend checks only
      djb health lint --fix         # Run linting with auto-fix
      djb health typecheck          # Type checking only
      djb health test               # Tests only
      djb health test --cov         # Tests with coverage
      djb health e2e                # E2E tests only
      djb -v health                 # Show error details on failure
    """
    # Specialize context for health subcommands
    parent_context = ctx.obj
    ctx.ensure_object(CliHealthContext)
    assert isinstance(ctx.obj, CliHealthContext)
    ctx.obj.__dict__.update(parent_context.__dict__)
    ctx.obj.fix = fix
    ctx.obj.cov = cov

    # If no subcommand, run all checks
    if ctx.invoked_subcommand is None:
        _run_all_checks(ctx)


def _run_all_checks(ctx: click.Context) -> None:
    """Run all health checks."""
    health_ctx = _get_health_context(ctx)
    fix = health_ctx.fix
    cov = health_ctx.cov
    verbose = health_ctx.verbose
    quiet = health_ctx.quiet
    run_backend, run_frontend = _get_run_scopes(health_ctx.scope_frontend, health_ctx.scope_backend)

    project_ctx = _get_project_context(ctx)
    all_failures: list[StepFailure] = []

    # Run checks for djb if present
    if project_ctx.djb_path:
        prefix = "[djb]" if project_ctx.host_path else ""
        if prefix and not quiet:
            logger.section("Running health checks for djb (editable)")

        steps: list[HealthStep] = []
        djb_frontend = _get_frontend_dir(project_ctx.djb_path)

        if run_backend:
            steps.extend(
                _build_backend_lint_steps(project_ctx.djb_path, fix, prefix, scope="Python")
            )
            steps.extend(
                _build_backend_typecheck_steps(project_ctx.djb_path, prefix, scope="Python")
            )
            steps.extend(
                _build_backend_test_steps(project_ctx.djb_path, prefix, scope="Python", cov=cov)
            )

        if run_frontend:
            steps.extend(_build_frontend_lint_steps(djb_frontend, fix, prefix))
            steps.extend(_build_frontend_typecheck_steps(djb_frontend, prefix))
            steps.extend(_build_frontend_test_steps(djb_frontend, prefix))

        all_failures.extend(_run_steps(steps, quiet, verbose))

    # Run checks for host project if present
    if project_ctx.host_path:
        host_name = _get_host_display_name(project_ctx.host_path)
        prefix = f"[{host_name}]" if project_ctx.djb_path else ""
        if prefix and not quiet:
            logger.section(f"Running health checks for {host_name}")

        steps = []
        host_frontend = _get_frontend_dir(project_ctx.host_path)

        if run_backend:
            steps.extend(
                _build_backend_lint_steps(project_ctx.host_path, fix, prefix, scope="Backend")
            )
            steps.extend(
                _build_backend_typecheck_steps(project_ctx.host_path, prefix, scope="Backend")
            )
            steps.extend(
                _build_backend_test_steps(project_ctx.host_path, prefix, scope="Backend", cov=cov)
            )

        if run_frontend:
            steps.extend(_build_frontend_lint_steps(host_frontend, fix, prefix))
            steps.extend(_build_frontend_typecheck_steps(host_frontend, prefix))
            steps.extend(_build_frontend_test_steps(host_frontend, prefix))

        all_failures.extend(_run_steps(steps, quiet, verbose))

    # Show skip message if inside djb
    if project_ctx.inside_djb and project_ctx.host_path is None and not quiet:
        logger.notice("Running from djb directory, skipping host project checks.")

    _report_failures(all_failures, fix, verbose)


@health.command()
@click.option("--fix", is_flag=True, help="Attempt to auto-fix lint issues.")
@click.pass_context
def lint(ctx: click.Context, fix: bool):
    """Run linting checks.

    Backend: black (--check unless --fix)
    Frontend: bun run lint
    """
    health_ctx = _get_health_context(ctx)
    verbose = health_ctx.verbose
    quiet = health_ctx.quiet
    fix = fix or health_ctx.fix
    run_backend, run_frontend = _get_run_scopes(health_ctx.scope_frontend, health_ctx.scope_backend)

    project_ctx = _get_project_context(ctx)
    all_failures: list[StepFailure] = []

    # Run lint for djb if present
    if project_ctx.djb_path:
        prefix = "[djb]" if project_ctx.host_path else ""
        if prefix and not quiet:
            logger.section("Running lint for djb (editable)")

        steps: list[HealthStep] = []
        djb_frontend = _get_frontend_dir(project_ctx.djb_path)

        if run_backend:
            steps.extend(
                _build_backend_lint_steps(project_ctx.djb_path, fix, prefix, scope="Python")
            )
        if run_frontend:
            steps.extend(_build_frontend_lint_steps(djb_frontend, fix, prefix))

        all_failures.extend(_run_steps(steps, quiet, verbose))

    # Run lint for host project if present
    if project_ctx.host_path:
        host_name = _get_host_display_name(project_ctx.host_path)
        prefix = f"[{host_name}]" if project_ctx.djb_path else ""
        if prefix and not quiet:
            logger.section(f"Running lint for {host_name}")

        steps = []
        host_frontend = _get_frontend_dir(project_ctx.host_path)

        if run_backend:
            steps.extend(
                _build_backend_lint_steps(project_ctx.host_path, fix, prefix, scope="Backend")
            )
        if run_frontend:
            steps.extend(_build_frontend_lint_steps(host_frontend, fix, prefix))

        all_failures.extend(_run_steps(steps, quiet, verbose))

    if project_ctx.inside_djb and project_ctx.host_path is None and not quiet:
        logger.notice("Running from djb directory, skipping host project checks.")

    _report_failures(all_failures, fix, verbose)


@health.command()
@click.pass_context
def typecheck(ctx: click.Context):
    """Run type checking.

    Backend: pyright
    Frontend: bun run tsc
    """
    health_ctx = _get_health_context(ctx)
    verbose = health_ctx.verbose
    quiet = health_ctx.quiet
    run_backend, run_frontend = _get_run_scopes(health_ctx.scope_frontend, health_ctx.scope_backend)

    project_ctx = _get_project_context(ctx)
    all_failures: list[StepFailure] = []

    # Run typecheck for djb if present
    if project_ctx.djb_path:
        prefix = "[djb]" if project_ctx.host_path else ""
        if prefix and not quiet:
            logger.section("Running typecheck for djb (editable)")

        steps: list[HealthStep] = []
        djb_frontend = _get_frontend_dir(project_ctx.djb_path)

        if run_backend:
            steps.extend(
                _build_backend_typecheck_steps(project_ctx.djb_path, prefix, scope="Python")
            )
        if run_frontend:
            steps.extend(_build_frontend_typecheck_steps(djb_frontend, prefix))

        all_failures.extend(_run_steps(steps, quiet, verbose))

    # Run typecheck for host project if present
    if project_ctx.host_path:
        host_name = _get_host_display_name(project_ctx.host_path)
        prefix = f"[{host_name}]" if project_ctx.djb_path else ""
        if prefix and not quiet:
            logger.section(f"Running typecheck for {host_name}")

        steps = []
        host_frontend = _get_frontend_dir(project_ctx.host_path)

        if run_backend:
            steps.extend(
                _build_backend_typecheck_steps(project_ctx.host_path, prefix, scope="Backend")
            )
        if run_frontend:
            steps.extend(_build_frontend_typecheck_steps(host_frontend, prefix))

        all_failures.extend(_run_steps(steps, quiet, verbose))

    if project_ctx.inside_djb and project_ctx.host_path is None and not quiet:
        logger.notice("Running from djb directory, skipping host project checks.")

    _report_failures(all_failures, verbose=verbose)


@health.group(invoke_without_command=True)
@click.option("--cov/--no-cov", default=False, help="Enable/disable code coverage reporting.")
@click.pass_context
def test(ctx: click.Context, cov: bool):
    """Run tests (excluding E2E).

    Backend: pytest
    Frontend: bun test

    Use --cov to enable code coverage reporting.

    Subcommands:
        overlap    Find tests with overlapping coverage
    """
    # If a subcommand was invoked, don't run the default behavior
    if ctx.invoked_subcommand is not None:
        return

    health_ctx = _get_health_context(ctx)
    verbose = health_ctx.verbose
    quiet = health_ctx.quiet
    # Combine local --cov flag with parent --cov flag from health group
    cov = cov or health_ctx.cov
    run_backend, run_frontend = _get_run_scopes(health_ctx.scope_frontend, health_ctx.scope_backend)

    project_ctx = _get_project_context(ctx)
    all_failures: list[StepFailure] = []

    # Run tests for djb if present
    if project_ctx.djb_path:
        prefix = "[djb]" if project_ctx.host_path else ""
        if prefix and not quiet:
            logger.section("Running tests for djb (editable)")

        steps: list[HealthStep] = []
        djb_frontend = _get_frontend_dir(project_ctx.djb_path)

        if run_backend:
            steps.extend(
                _build_backend_test_steps(project_ctx.djb_path, prefix, scope="Python", cov=cov)
            )
        if run_frontend:
            steps.extend(_build_frontend_test_steps(djb_frontend, prefix))

        all_failures.extend(_run_steps(steps, quiet, verbose))

    # Run tests for host project if present
    if project_ctx.host_path:
        host_name = _get_host_display_name(project_ctx.host_path)
        prefix = f"[{host_name}]" if project_ctx.djb_path else ""
        if prefix and not quiet:
            logger.section(f"Running tests for {host_name}")

        steps = []
        host_frontend = _get_frontend_dir(project_ctx.host_path)

        if run_backend:
            steps.extend(
                _build_backend_test_steps(project_ctx.host_path, prefix, scope="Backend", cov=cov)
            )
        if run_frontend:
            steps.extend(_build_frontend_test_steps(host_frontend, prefix))

        all_failures.extend(_run_steps(steps, quiet, verbose))

    if project_ctx.inside_djb and project_ctx.host_path is None and not quiet:
        logger.notice("Running from djb directory, skipping host project checks.")

    _report_failures(all_failures, verbose=verbose)


@test.command("overlap")
@click.option(
    "--min-similarity",
    type=float,
    default=0.95,
    help="Minimum Jaccard similarity to report (0-1, default: 0.95)",
)
@click.option(
    "--show-pairs",
    is_flag=True,
    help="Show all overlapping test pairs instead of parametrization groups.",
)
@click.option(
    "-p",
    "--package",
    "packages",
    multiple=True,
    help="Package(s) to analyze (can be specified multiple times). Defaults to 'src'.",
)
@click.pass_context
def overlap(
    ctx: click.Context, min_similarity: float, show_pairs: bool, packages: tuple[str, ...]
):
    """Find tests with overlapping coverage for potential consolidation.

    Collects per-test coverage data and identifies tests in the same class
    that cover the same code paths. These are candidates for consolidation
    using @pytest.mark.parametrize.

    Examples:
        djb health test overlap
        djb health test overlap -p src/djb/cli -p src/djb/core
        djb health test overlap --min-similarity 0.90
    """
    project_ctx = _get_project_context(ctx)
    project_root = project_ctx.djb_path or project_ctx.host_path

    if not project_root:
        raise click.ClickException("No project directory found")

    run_find_overlap(project_root, min_similarity, show_pairs, list(packages) or None)


@health.command()
@click.pass_context
def e2e(ctx: click.Context):
    """Run E2E tests.

    Runs pytest with --run-e2e flag for browser-based tests.
    """
    health_ctx = _get_health_context(ctx)
    verbose = health_ctx.verbose
    quiet = health_ctx.quiet
    project_ctx = _get_project_context(ctx)
    all_failures: list[StepFailure] = []

    # Run E2E tests for djb if present
    if project_ctx.djb_path:
        prefix = "[djb]" if project_ctx.host_path else ""
        if prefix and not quiet:
            logger.section("Running E2E tests for djb (editable)")

        steps = _build_e2e_steps(project_ctx.djb_path, prefix)
        all_failures.extend(_run_steps(steps, quiet, verbose))

    # Run E2E tests for host project if present
    if project_ctx.host_path:
        host_name = _get_host_display_name(project_ctx.host_path)
        prefix = f"[{host_name}]" if project_ctx.djb_path else ""
        if prefix and not quiet:
            logger.section(f"Running E2E tests for {host_name}")

        steps = _build_e2e_steps(project_ctx.host_path, prefix)
        all_failures.extend(_run_steps(steps, quiet, verbose))

    if project_ctx.inside_djb and project_ctx.host_path is None and not quiet:
        logger.notice("Running from djb directory, skipping host project checks.")

    _report_failures(all_failures, verbose=verbose)
