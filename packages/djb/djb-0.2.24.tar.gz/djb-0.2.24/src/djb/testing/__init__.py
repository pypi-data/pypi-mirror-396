"""Reusable testing utilities for djb-based projects.

This module provides testing utilities that can be imported and used
by host projects to verify code quality and type safety.

Example usage in a host project's test file:

    from djb.testing import test_typecheck

    # The test will automatically run when pytest discovers it
"""

from __future__ import annotations

from djb.testing.typecheck import test_typecheck

__all__ = ["test_typecheck"]
