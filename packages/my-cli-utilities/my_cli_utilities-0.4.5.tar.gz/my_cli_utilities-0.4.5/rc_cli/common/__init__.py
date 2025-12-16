# -*- coding: utf-8 -*-

"""Common utilities package for RC CLI modules."""

# Re-export all common utilities
from .utils import (
    Result,
    async_command,
    handle_http_error,
    create_error_result,
    format_separator,
    format_section_header
)
from .service_factory import ServiceFactory
from .company_config import replace_company_placeholders, apply_company_config
from .config import (
    DEFAULT_HTTP_TIMEOUT,
    DEFAULT_SSH_TIMEOUT,
    DEFAULT_INPUT_TIMEOUT,
    DEFAULT_NOTIFICATION_TIMEOUT,
    DEFAULT_WARNING_TIMEOUT,
    DEFAULT_ERROR_TIMEOUT,
    DEFAULT_CACHE_TTL,
    ALIAS_MAPPING_CACHE_TTL,
    DEFAULT_SEPARATOR_WIDTH,
    SHORT_SEPARATOR_WIDTH,
    MEDIUM_SEPARATOR_WIDTH,
    LONG_SEPARATOR_WIDTH
)

__all__ = [
    "Result",
    "async_command",
    "handle_http_error",
    "create_error_result",
    "format_separator",
    "format_section_header",
    "ServiceFactory",
    "replace_company_placeholders",
    "apply_company_config",
    "DEFAULT_HTTP_TIMEOUT",
    "DEFAULT_SSH_TIMEOUT",
    "DEFAULT_INPUT_TIMEOUT",
    "DEFAULT_NOTIFICATION_TIMEOUT",
    "DEFAULT_WARNING_TIMEOUT",
    "DEFAULT_ERROR_TIMEOUT",
    "DEFAULT_CACHE_TTL",
    "ALIAS_MAPPING_CACHE_TTL",
    "DEFAULT_SEPARATOR_WIDTH",
    "SHORT_SEPARATOR_WIDTH",
    "MEDIUM_SEPARATOR_WIDTH",
    "LONG_SEPARATOR_WIDTH"
]

