# -*- coding: utf-8 -*-

"""Result types and error handling using the returns library."""

from enum import Enum
from typing import Dict, List, Optional, Any
import typer
from returns.result import Result
from returns.maybe import Maybe
from dataclasses import dataclass


class ErrorType(Enum):
    """Enumeration of different error types."""
    NETWORK_ERROR = "network_error"
    DATA_NOT_FOUND = "data_not_found"
    VALIDATION_ERROR = "validation_error"
    SYSTEM_ERROR = "system_error"
    CACHE_ERROR = "cache_error"


@dataclass
class AppError:
    """Standardized error information."""
    error_type: ErrorType
    message: str
    details: Optional[str] = None
    suggestions: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "type": self.error_type.value,
            "message": self.message,
            "details": self.details,
            "suggestions": self.suggestions or []
        }


class ErrorDisplay:
    """Handles consistent error display."""
    
    @staticmethod
    def show_error(error: AppError) -> None:
        """Display error in a consistent format."""
        typer.echo(f"   ❌ {error.message}")
        
        if error.details:
            typer.echo(f"   📄 Details: {error.details}")
        
        if error.suggestions:
            typer.echo(f"   💡 Suggestions:")
            for suggestion in error.suggestions:
                typer.echo(f"      - {suggestion}")


class ResultHandler:
    """Handles Result and Maybe types and CLI exits."""

    @staticmethod
    def _show_error_and_exit(error: AppError, exit_code: int):
        ErrorDisplay.show_error(error)
        raise typer.Exit(code=exit_code)

    @staticmethod
    def handle_result(result: Result[Any, AppError]) -> Any:
        """
        Unwraps a Result, exiting with an error message on Failure.
        """
        return result.alt(
            lambda error: ResultHandler._show_error_and_exit(error, 1)
        ).unwrap()

    @staticmethod
    def handle_maybe(maybe: Maybe[Any], error: AppError) -> Any:
        """
        Unwraps a Maybe, exiting with a specified error on Nothing.
        """
        return maybe.alt(
            lambda: ResultHandler._show_error_and_exit(error, 1)
        ).unwrap()


# Type aliases for common patterns
AccountResult = Result[Dict, AppError]
AccountListResult = Result[List[Dict], AppError]


# Common error creators
def network_error(message: str, details: Optional[str] = None) -> AppError:
    """Create a network error."""
    return AppError(
        ErrorType.NETWORK_ERROR,
        message,
        details,
        ["Check network connectivity", "Verify API endpoint is accessible"]
    )


def data_not_found_error(message: str, suggestions: Optional[List[str]] = None) -> AppError:
    """Create a data not found error."""
    return AppError(
        ErrorType.DATA_NOT_FOUND,
        message,
        suggestions=suggestions or ["Verify the input parameters", "Try a different search query"]
    )


def validation_error(message: str, details: Optional[str] = None) -> AppError:
    """Create a validation error."""
    return AppError(
        ErrorType.VALIDATION_ERROR,
        message,
        details,
        ["Check input format", "Refer to command help for valid options"]
    )

def cache_error(message: str, details: Optional[str] = None) -> AppError:
    """Create a cache error."""
    return AppError(
        ErrorType.CACHE_ERROR,
        message,
        details,
        ["Check file permissions", "Try clearing the cache with 'rc ap cache clear'"]
    ) 