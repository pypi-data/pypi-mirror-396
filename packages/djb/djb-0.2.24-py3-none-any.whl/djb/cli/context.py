"""CLI context for passing global options to subcommands."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from djb.config import DjbConfig


@dataclass
class CliContext:
    """Context object passed through click's ctx.obj.

    This dataclass holds global CLI options that any subcommand can access.
    Use ctx.ensure_object(CliContext) in the main CLI group and access
    values via ctx.obj.<field_name> in subcommands.

    Subcommand groups can specialize the context by:
    1. Saving the parent context: `parent_ctx = ctx.obj`
    2. Creating their specialized context: `ctx.ensure_object(CliHealthContext)`
    3. Copying parent fields: `ctx.obj.__dict__.update(parent_ctx.__dict__)`
    4. Setting specialized fields: `ctx.obj.fix = fix`

    Example:
        @click.pass_context
        def my_command(ctx: click.Context):
            if ctx.obj.verbose:
                click.echo("Verbose mode enabled")
    """

    # Global options (set by djb_cli)
    log_level: str = "info"
    verbose: bool = False
    quiet: bool = False
    config: DjbConfig | None = field(default=None)

    # Scope options (useful for multiple commands)
    scope_frontend: bool = False
    scope_backend: bool = False


@dataclass
class CliHealthContext(CliContext):
    """Specialized context for `djb health` command group.

    Inherits all global options from CliContext and adds health-specific options.
    """

    fix: bool = False
    cov: bool = False
