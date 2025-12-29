#!/usr/bin/env python3
"""
Splunk-Specific Input Validators

Provides validation functions for Splunk-specific formats and values.
All validators return the validated value or raise ValidationError.
"""

import re
from typing import Any, List, Optional, Union
from urllib.parse import urlparse


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(f"Validation error{f' for {field}' if field else ''}: {message}")


def validate_sid(sid: str) -> str:
    """
    Validate Splunk Search ID (SID) format.

    SIDs typically have format: {timestamp}.{random}[_{user}]
    Example: 1703779200.12345_admin

    Args:
        sid: Search ID to validate

    Returns:
        Validated SID

    Raises:
        ValidationError: If SID format is invalid
    """
    if not sid or not isinstance(sid, str):
        raise ValidationError("SID must be a non-empty string", field="sid")

    sid = sid.strip()

    # SID pattern: digits.digits optionally followed by _username
    # Also allow scheduled search SIDs: scheduler__{app}__{user}__search__{name}__{timestamp}
    sid_pattern = r'^(\d+\.\d+(_\w+)?|scheduler__\w+__\w+__\w+__\w+__\w+)$'
    if not re.match(sid_pattern, sid):
        raise ValidationError(f"Invalid SID format: {sid}", field="sid")

    return sid


def validate_spl(spl: str) -> str:
    """
    Validate SPL (Search Processing Language) query.

    Performs basic syntax validation:
    - Non-empty string
    - Balanced parentheses and brackets
    - Valid pipe structure
    - No obvious syntax errors

    Args:
        spl: SPL query to validate

    Returns:
        Validated SPL query (trimmed)

    Raises:
        ValidationError: If SPL syntax is invalid
    """
    if not spl or not isinstance(spl, str):
        raise ValidationError("SPL query must be a non-empty string", field="spl")

    spl = spl.strip()

    # Check for balanced parentheses
    paren_count = 0
    bracket_count = 0
    in_string = False
    string_char = None

    for i, char in enumerate(spl):
        if char in '"\'':
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
        elif not in_string:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                if paren_count < 0:
                    raise ValidationError("Unbalanced parentheses: extra ')'", field="spl")
            elif char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count < 0:
                    raise ValidationError("Unbalanced brackets: extra ']'", field="spl")

    if paren_count != 0:
        raise ValidationError("Unbalanced parentheses: missing ')'", field="spl")
    if bracket_count != 0:
        raise ValidationError("Unbalanced brackets: missing ']'", field="spl")
    if in_string:
        raise ValidationError("Unterminated string literal", field="spl")

    # Check for empty pipes
    if '||' in spl.replace(' ', ''):
        raise ValidationError("Empty pipe segment (||)", field="spl")

    # Check for trailing pipe
    if spl.rstrip().endswith('|'):
        raise ValidationError("SPL cannot end with a pipe", field="spl")

    return spl


def validate_time_modifier(time_str: str) -> str:
    """
    Validate Splunk time modifier format.

    Valid formats include:
    - Relative: -1h, -7d, -30m, +1d
    - Snap-to: @h, @d, @w0, @mon
    - Combined: -1d@d, -1h@h
    - Absolute: epoch timestamp
    - Keywords: now, now(), earliest, latest

    Args:
        time_str: Time modifier to validate

    Returns:
        Validated time modifier

    Raises:
        ValidationError: If time format is invalid
    """
    if not time_str or not isinstance(time_str, str):
        raise ValidationError("Time modifier must be a non-empty string", field="time")

    time_str = time_str.strip().lower()

    # Special keywords
    if time_str in ('now', 'now()', 'earliest', 'latest', '0'):
        return time_str

    # Epoch timestamp (all digits)
    if time_str.isdigit():
        return time_str

    # Relative time pattern: [+-]N[smhdwMy][@snap]
    relative_pattern = r'^[+-]?\d+[smhdwMy](@[smhdwMy]?\d*)?$'
    if re.match(relative_pattern, time_str, re.IGNORECASE):
        return time_str

    # Snap-to pattern: @[smhdwMy]N?
    snap_pattern = r'^@[smhdwMy]\d*$'
    if re.match(snap_pattern, time_str, re.IGNORECASE):
        return time_str

    # Week day snap: @w[0-6]
    weekday_pattern = r'^@w[0-6]$'
    if re.match(weekday_pattern, time_str, re.IGNORECASE):
        return time_str

    # Month snap: @mon, @q (quarter), @y (year)
    month_pattern = r'^@(mon|q\d?|y)$'
    if re.match(month_pattern, time_str, re.IGNORECASE):
        return time_str

    # Combined relative + snap
    combined_pattern = r'^[+-]?\d+[smhdwMy]@[smhdwMy0-6]?\d*$'
    if re.match(combined_pattern, time_str, re.IGNORECASE):
        return time_str

    raise ValidationError(
        f"Invalid time modifier format: {time_str}. "
        "Valid formats: -1h, -7d@d, @h, now, epoch timestamp",
        field="time"
    )


def validate_index_name(index: str) -> str:
    """
    Validate Splunk index name.

    Index naming rules:
    - Must start with a letter or underscore
    - Can contain letters, digits, underscores, hyphens
    - Cannot be a reserved name (internal, _*)
    - Maximum 80 characters

    Args:
        index: Index name to validate

    Returns:
        Validated index name

    Raises:
        ValidationError: If index name is invalid
    """
    if not index or not isinstance(index, str):
        raise ValidationError("Index name must be a non-empty string", field="index")

    index = index.strip()

    if len(index) > 80:
        raise ValidationError("Index name cannot exceed 80 characters", field="index")

    # Pattern: starts with letter/underscore, contains alphanumeric/underscore/hyphen
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_-]*$'
    if not re.match(pattern, index):
        raise ValidationError(
            f"Invalid index name: {index}. "
            "Must start with letter/underscore, contain only alphanumeric/underscore/hyphen",
            field="index"
        )

    # Reserved internal indexes start with _
    # Allow wildcards for search
    if index.startswith('_') and index not in ('_internal', '_audit', '_introspection', '_telemetry', '*'):
        # Allow _* for searching all internal indexes
        if index != '_*':
            pass  # Allow internal indexes to be specified

    return index


def validate_app_name(app: str) -> str:
    """
    Validate Splunk app name.

    App naming conventions:
    - Must start with a letter
    - Can contain letters, digits, underscores
    - Cannot contain spaces or special characters
    - Maximum 80 characters

    Args:
        app: App name to validate

    Returns:
        Validated app name

    Raises:
        ValidationError: If app name is invalid
    """
    if not app or not isinstance(app, str):
        raise ValidationError("App name must be a non-empty string", field="app")

    app = app.strip()

    if len(app) > 80:
        raise ValidationError("App name cannot exceed 80 characters", field="app")

    # Pattern: starts with letter, contains alphanumeric/underscore
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
    if not re.match(pattern, app):
        raise ValidationError(
            f"Invalid app name: {app}. "
            "Must start with letter, contain only alphanumeric/underscore",
            field="app"
        )

    return app


def validate_port(port: Union[int, str]) -> int:
    """
    Validate port number.

    Args:
        port: Port number to validate

    Returns:
        Validated port as integer

    Raises:
        ValidationError: If port is invalid
    """
    try:
        port_int = int(port)
    except (ValueError, TypeError):
        raise ValidationError(f"Port must be a number: {port}", field="port")

    if port_int < 1 or port_int > 65535:
        raise ValidationError(f"Port must be between 1 and 65535: {port_int}", field="port")

    return port_int


def validate_url(url: str, require_https: bool = False) -> str:
    """
    Validate URL format.

    Args:
        url: URL to validate
        require_https: If True, only HTTPS URLs are allowed

    Returns:
        Validated URL

    Raises:
        ValidationError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string", field="url")

    url = url.strip()

    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"

    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValidationError(f"Invalid URL format: {e}", field="url")

    if not parsed.scheme:
        raise ValidationError("URL must have a scheme (http/https)", field="url")

    if not parsed.netloc:
        raise ValidationError("URL must have a host", field="url")

    if require_https and parsed.scheme != 'https':
        raise ValidationError("URL must use HTTPS for security", field="url")

    return url


def validate_output_mode(mode: str) -> str:
    """
    Validate Splunk output mode.

    Valid modes: json, csv, xml, raw

    Args:
        mode: Output mode to validate

    Returns:
        Validated output mode

    Raises:
        ValidationError: If mode is invalid
    """
    valid_modes = ('json', 'csv', 'xml', 'raw')

    if not mode or not isinstance(mode, str):
        raise ValidationError(
            f"Output mode must be one of: {', '.join(valid_modes)}",
            field="output_mode"
        )

    mode = mode.strip().lower()

    if mode not in valid_modes:
        raise ValidationError(
            f"Invalid output mode: {mode}. Must be one of: {', '.join(valid_modes)}",
            field="output_mode"
        )

    return mode


def validate_count(count: Union[int, str]) -> int:
    """
    Validate result count parameter.

    Args:
        count: Count value to validate (0 = unlimited)

    Returns:
        Validated count as integer

    Raises:
        ValidationError: If count is invalid
    """
    try:
        count_int = int(count)
    except (ValueError, TypeError):
        raise ValidationError(f"Count must be a number: {count}", field="count")

    if count_int < 0:
        raise ValidationError("Count cannot be negative", field="count")

    return count_int


def validate_offset(offset: Union[int, str]) -> int:
    """
    Validate result offset parameter.

    Args:
        offset: Offset value to validate

    Returns:
        Validated offset as integer

    Raises:
        ValidationError: If offset is invalid
    """
    try:
        offset_int = int(offset)
    except (ValueError, TypeError):
        raise ValidationError(f"Offset must be a number: {offset}", field="offset")

    if offset_int < 0:
        raise ValidationError("Offset cannot be negative", field="offset")

    return offset_int


def validate_field_list(fields: Union[str, List[str]]) -> List[str]:
    """
    Validate and normalize field list.

    Args:
        fields: Comma-separated string or list of field names

    Returns:
        List of validated field names

    Raises:
        ValidationError: If fields are invalid
    """
    if isinstance(fields, str):
        fields = [f.strip() for f in fields.split(',') if f.strip()]
    elif not isinstance(fields, list):
        raise ValidationError("Fields must be a string or list", field="fields")

    validated = []
    for field in fields:
        if not isinstance(field, str) or not field.strip():
            continue
        # Field names can contain alphanumeric, underscore, period, colon
        field = field.strip()
        if not re.match(r'^[\w.:]+$', field):
            raise ValidationError(f"Invalid field name: {field}", field="fields")
        validated.append(field)

    if not validated:
        raise ValidationError("At least one field must be specified", field="fields")

    return validated


def validate_search_mode(mode: str) -> str:
    """
    Validate search execution mode.

    Valid modes: normal, blocking, oneshot

    Args:
        mode: Search mode to validate

    Returns:
        Validated search mode

    Raises:
        ValidationError: If mode is invalid
    """
    valid_modes = ('normal', 'blocking', 'oneshot')

    if not mode or not isinstance(mode, str):
        raise ValidationError(
            f"Search mode must be one of: {', '.join(valid_modes)}",
            field="exec_mode"
        )

    mode = mode.strip().lower()

    if mode not in valid_modes:
        raise ValidationError(
            f"Invalid search mode: {mode}. Must be one of: {', '.join(valid_modes)}",
            field="exec_mode"
        )

    return mode
