# -*- coding: utf-8 -*-

"""Common utilities for RC CLI modules.

This module is kept for backward compatibility.
The actual implementation has been moved to rc_cli.common package.
"""

# Re-export everything from common package for backward compatibility
from .common import (
    Result,
    async_command,
    handle_http_error,
    create_error_result,
    ServiceFactory
)

__all__ = [
    "Result",
    "async_command",
    "handle_http_error",
    "create_error_result",
    "ServiceFactory"
]

