# -*- coding: utf-8 -*-

"""Common utility functions for RC CLI modules."""

import asyncio
import functools
from typing import Callable, TypeVar, Coroutine, Any, Optional
from dataclasses import dataclass

T = TypeVar('T')


@dataclass
class Result:
    """Generic result wrapper for service operations."""
    
    success: bool
    data: Optional[Any] = None
    error_message: str = ""
    count: int = 0


def async_command(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    """
    Decorator to convert async command functions to sync functions for Typer.
    
    Usage:
        @async_command
        async def my_command():
            await some_async_operation()
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return asyncio.run(func(*args, **kwargs))
    return wrapper


def handle_http_error(e: Exception, operation: str, not_found_message: Optional[str] = None) -> str:
    """
    Handle HTTP errors and return standardized error message.
    
    Args:
        e: The exception that occurred
        operation: Description of the operation
        not_found_message: Custom message for 404 errors (optional)
        
    Returns:
        Error message string
    """
    import httpx
    
    if isinstance(e, httpx.TimeoutException):
        return f"Request timeout during {operation}: {e}"
    elif isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            if not_found_message:
                return not_found_message
            return f"Resource not found during {operation}"
        response_text = e.response.text[:500] if e.response.text else "No response body"
        return f"HTTP error {e.response.status_code} during {operation}: {response_text}"
    elif isinstance(e, httpx.RequestError):
        error_str = str(e)
        dns_error = _check_dns_error(error_str, operation, e)
        if dns_error:
            return dns_error
        return f"Request failed during {operation}: {e}"
    else:
        error_str = str(e)
        dns_error = _check_dns_error(error_str, operation, e)
        if dns_error:
            return dns_error
        return f"Unexpected error during {operation}: {e}"


def _check_dns_error(error_str: str, operation: str, e: Exception) -> Optional[str]:
    """
    Check if error string contains DNS resolution errors.
    
    Args:
        error_str: Error message string to check
        operation: Description of the operation
        e: The exception object
        
    Returns:
        Formatted DNS error message if DNS error detected, None otherwise
    """
    if "nodename nor servname provided" in error_str or "not known" in error_str:
        return (
            f"DNS resolution failed during {operation}. "
            f"This usually means the server URL is incorrect or unreachable. "
            f"Error: {e}. "
            f"Please check your environment variables or configuration."
        )
    return None


def create_error_result(result_class: type, error_message: str) -> Any:
    """
    Create an error result object of the specified type.
    
    Args:
        result_class: The result class (SPResult, FFSResult, etc.)
        error_message: Error message string
        
    Returns:
        Instance of result_class with success=False
    """
    return result_class(
        success=False,
        error_message=error_message,
        count=0
    )


def format_separator(width: int = 60, char: str = "-") -> str:
    """
    Format a separator line for display.
    
    Args:
        width: Width of the separator line
        char: Character to use for separator (default: "-")
        
    Returns:
        Formatted separator string
        
    Examples:
        >>> format_separator(60)
        '------------------------------------------------------------'
        >>> format_separator(40, "=")
        '========================================'
    """
    return char * width


def format_section_header(title: str, width: int = 60, char: str = "-") -> str:
    """
    Format a section header with title and separator.
    
    Args:
        title: Section title
        width: Width of the separator line
        char: Character to use for separator
        
    Returns:
        Formatted section header string
        
    Examples:
        >>> format_section_header("Service Parameter Value", 60)
        'Service Parameter Value\\n------------------------------------------------------------'
    """
    separator = format_separator(width, char)
    return f"{title}\n{separator}"

