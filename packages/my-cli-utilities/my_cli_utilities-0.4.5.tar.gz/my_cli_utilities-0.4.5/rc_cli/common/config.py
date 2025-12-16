# -*- coding: utf-8 -*-

"""Common configuration constants for RC CLI modules."""

# Timeout constants (in seconds)
DEFAULT_HTTP_TIMEOUT = 30.0  # Default timeout for HTTP requests
DEFAULT_SSH_TIMEOUT = 5.0    # Default timeout for SSH operations
DEFAULT_INPUT_TIMEOUT = 10.0  # Default timeout for user input
DEFAULT_NOTIFICATION_TIMEOUT = 2.0  # Default timeout for UI notifications
DEFAULT_WARNING_TIMEOUT = 3.0  # Default timeout for warnings
DEFAULT_ERROR_TIMEOUT = 5.0    # Default timeout for error messages

# Cache TTL constants (in seconds)
DEFAULT_CACHE_TTL = 300        # 5 minutes - default cache TTL
ALIAS_MAPPING_CACHE_TTL = 3600  # 1 hour - alias mapping cache TTL

# Display formatting constants
DEFAULT_SEPARATOR_WIDTH = 60   # Default width for separator lines
SHORT_SEPARATOR_WIDTH = 40     # Short separator width
MEDIUM_SEPARATOR_WIDTH = 50    # Medium separator width
LONG_SEPARATOR_WIDTH = 80      # Long separator width

