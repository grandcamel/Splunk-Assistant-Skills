#!/usr/bin/env python3
"""
Splunk Error Handling

Provides a comprehensive exception hierarchy and error handling utilities
for Splunk REST API interactions.

Exception Hierarchy:
    SplunkError (base)
    ├── AuthenticationError (401)
    ├── AuthorizationError (403)
    ├── ValidationError (400)
    ├── NotFoundError (404)
    ├── RateLimitError (429)
    ├── SearchQuotaError (503)
    ├── JobFailedError (job failed state)
    └── ServerError (5xx)
"""

import functools
import json
import re
import sys
import traceback
from typing import Any, Callable, Dict, Optional

import requests


class SplunkError(Exception):
    """Base exception for all Splunk-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.operation = operation
        self.details = details or {}
        super().__init__(self.format_message())

    def format_message(self) -> str:
        """Format error message with context."""
        parts = []
        if self.operation:
            parts.append(f"[{self.operation}]")
        if self.status_code:
            parts.append(f"HTTP {self.status_code}:")
        parts.append(self.message)
        return ' '.join(parts)


class AuthenticationError(SplunkError):
    """Raised when authentication fails (401 Unauthorized)."""

    def __init__(
        self,
        message: str = "Authentication failed. Check your token or credentials.",
        **kwargs,
    ):
        super().__init__(message, status_code=401, **kwargs)


class AuthorizationError(SplunkError):
    """Raised when user lacks required permissions (403 Forbidden)."""

    def __init__(
        self,
        message: str = "Insufficient permissions to perform this operation.",
        capability: Optional[str] = None,
        **kwargs,
    ):
        self.capability = capability
        if capability:
            message = f"{message} Required capability: {capability}"
        super().__init__(message, status_code=403, **kwargs)


class ValidationError(SplunkError):
    """Raised for invalid input or request parameters (400 Bad Request)."""

    def __init__(
        self,
        message: str = "Invalid request parameters.",
        field: Optional[str] = None,
        **kwargs,
    ):
        self.field = field
        if field:
            message = f"Invalid value for '{field}': {message}"
        super().__init__(message, status_code=400, **kwargs)


class NotFoundError(SplunkError):
    """Raised when requested resource is not found (404 Not Found)."""

    def __init__(
        self,
        message: str = "Resource not found.",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs,
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        if resource_type and resource_id:
            message = f"{resource_type} '{resource_id}' not found."
        elif resource_type:
            message = f"{resource_type} not found."
        super().__init__(message, status_code=404, **kwargs)


class RateLimitError(SplunkError):
    """Raised when rate limit is exceeded (429 Too Many Requests)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Too many concurrent searches.",
        retry_after: Optional[int] = None,
        **kwargs,
    ):
        self.retry_after = retry_after
        if retry_after:
            message = f"{message} Retry after {retry_after} seconds."
        super().__init__(message, status_code=429, **kwargs)


class SearchQuotaError(SplunkError):
    """Raised when search quota is exhausted (503 Service Unavailable)."""

    def __init__(
        self,
        message: str = "Search quota exhausted. No available search slots.",
        **kwargs,
    ):
        super().__init__(message, status_code=503, **kwargs)


class JobFailedError(SplunkError):
    """Raised when a search job fails."""

    def __init__(
        self,
        message: str = "Search job failed.",
        sid: Optional[str] = None,
        dispatch_state: Optional[str] = None,
        **kwargs,
    ):
        self.sid = sid
        self.dispatch_state = dispatch_state
        if sid:
            message = f"Search job '{sid}' failed."
        if dispatch_state:
            message = f"{message} State: {dispatch_state}"
        super().__init__(message, **kwargs)


class ServerError(SplunkError):
    """Raised for server-side errors (5xx)."""

    def __init__(
        self,
        message: str = "Splunk server error.",
        **kwargs,
    ):
        super().__init__(message, **kwargs)


def parse_error_response(response: requests.Response) -> Dict[str, Any]:
    """
    Parse error details from Splunk response.

    Args:
        response: HTTP response object

    Returns:
        Dictionary with error details
    """
    try:
        data = response.json()
        messages = data.get('messages', [])
        if messages:
            return {
                'message': messages[0].get('text', 'Unknown error'),
                'type': messages[0].get('type', 'ERROR'),
                'code': messages[0].get('code'),
                'details': data,
            }
        return {'message': str(data), 'details': data}
    except (json.JSONDecodeError, ValueError):
        return {'message': response.text or 'Unknown error'}


def sanitize_error_message(message: str) -> str:
    """
    Remove sensitive information from error messages.

    Args:
        message: Original error message

    Returns:
        Sanitized message with sensitive data redacted
    """
    # Patterns to redact
    patterns = [
        (r'(token[=:]\s*)[^\s&]+', r'\1[REDACTED]'),
        (r'(password[=:]\s*)[^\s&]+', r'\1[REDACTED]'),
        (r'(Bearer\s+)[^\s]+', r'\1[REDACTED]'),
        (r'(Authorization[=:]\s*)[^\s]+', r'\1[REDACTED]'),
        (r'(api[_-]?key[=:]\s*)[^\s&]+', r'\1[REDACTED]'),
    ]
    for pattern, replacement in patterns:
        message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
    return message


def handle_splunk_error(response: requests.Response, operation: str = "API request") -> None:
    """
    Handle Splunk API error response.

    Args:
        response: HTTP response object
        operation: Description of the operation for error context

    Raises:
        Appropriate SplunkError subclass based on status code
    """
    status_code = response.status_code
    error_info = parse_error_response(response)
    message = sanitize_error_message(error_info.get('message', 'Unknown error'))
    details = error_info.get('details', {})

    error_kwargs = {
        'operation': operation,
        'details': details,
    }

    if status_code == 400:
        raise ValidationError(message, **error_kwargs)
    elif status_code == 401:
        raise AuthenticationError(message, **error_kwargs)
    elif status_code == 403:
        raise AuthorizationError(message, **error_kwargs)
    elif status_code == 404:
        raise NotFoundError(message, **error_kwargs)
    elif status_code == 429:
        retry_after = response.headers.get('Retry-After')
        raise RateLimitError(
            message,
            retry_after=int(retry_after) if retry_after else None,
            **error_kwargs,
        )
    elif status_code == 503:
        # Check if it's a search quota error
        if 'search' in message.lower() or 'quota' in message.lower():
            raise SearchQuotaError(message, **error_kwargs)
        raise ServerError(message, status_code=status_code, **error_kwargs)
    elif status_code >= 500:
        raise ServerError(message, status_code=status_code, **error_kwargs)
    else:
        raise SplunkError(message, status_code=status_code, **error_kwargs)


def print_error(message: str, include_traceback: bool = False) -> None:
    """
    Print error message to stderr with formatting.

    Args:
        message: Error message to print
        include_traceback: Whether to include traceback
    """
    sanitized = sanitize_error_message(message)
    print(f"\033[91mError:\033[0m {sanitized}", file=sys.stderr)
    if include_traceback:
        traceback.print_exc(file=sys.stderr)


def handle_errors(func: Callable) -> Callable:
    """
    Decorator for handling errors in CLI scripts.

    Catches SplunkError exceptions and prints user-friendly messages.
    Exits with appropriate return code.

    Usage:
        @handle_errors
        def main():
            # Script logic
            pass
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SplunkError as e:
            print_error(str(e))
            sys.exit(1)
        except requests.exceptions.ConnectionError as e:
            print_error(f"Connection failed: {sanitize_error_message(str(e))}")
            sys.exit(1)
        except requests.exceptions.Timeout as e:
            print_error(f"Request timed out: {sanitize_error_message(str(e))}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.", file=sys.stderr)
            sys.exit(130)
        except Exception as e:
            print_error(f"Unexpected error: {sanitize_error_message(str(e))}", include_traceback=True)
            sys.exit(1)

    return wrapper


def format_error_for_json(error: SplunkError) -> Dict[str, Any]:
    """
    Format error for JSON output.

    Args:
        error: SplunkError instance

    Returns:
        Dictionary suitable for JSON serialization
    """
    return {
        'error': True,
        'type': type(error).__name__,
        'message': error.message,
        'status_code': error.status_code,
        'operation': error.operation,
        'details': error.details,
    }
