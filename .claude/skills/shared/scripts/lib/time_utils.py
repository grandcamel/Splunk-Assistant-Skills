#!/usr/bin/env python3
"""
Splunk Time Modifier Utilities

Provides utilities for working with Splunk's time modifiers.
Handles parsing, formatting, and validation of Splunk time formats.

Splunk Time Modifiers:
    Relative time: -1h, -7d, +30m, -1mon
    Snap-to: @h, @d, @w0, @mon, @y
    Combined: -1d@d, -1h@h
    Keywords: now, now(), earliest, latest
    Epoch: 1234567890
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, Union

# Time unit multipliers in seconds
TIME_UNITS = {
    "s": 1,  # second
    "sec": 1,
    "second": 1,
    "seconds": 1,
    "m": 60,  # minute
    "min": 60,
    "minute": 60,
    "minutes": 60,
    "h": 3600,  # hour
    "hr": 3600,
    "hour": 3600,
    "hours": 3600,
    "d": 86400,  # day
    "day": 86400,
    "days": 86400,
    "w": 604800,  # week
    "week": 604800,
    "weeks": 604800,
    "mon": 2592000,  # month (30 days)
    "month": 2592000,
    "months": 2592000,
    "y": 31536000,  # year (365 days)
    "year": 31536000,
    "years": 31536000,
}

# Snap-to unit mappings
SNAP_UNITS = {
    "s": "second",
    "m": "minute",
    "h": "hour",
    "d": "day",
    "w": "week",
    "mon": "month",
    "q": "quarter",
    "y": "year",
}


def parse_splunk_time(time_str: str, reference: Optional[datetime] = None) -> datetime:
    """
    Parse Splunk time modifier to datetime.

    Args:
        time_str: Splunk time modifier string
        reference: Reference datetime (default: now)

    Returns:
        Parsed datetime

    Raises:
        ValueError: If time format is invalid
    """
    if reference is None:
        reference = datetime.now()

    time_str = time_str.strip().lower()

    # Handle special keywords
    if time_str in ("now", "now()"):
        return reference

    if time_str == "earliest":
        # Return epoch 0
        return datetime(1970, 1, 1)

    if time_str == "latest":
        return reference

    if time_str == "0":
        return datetime(1970, 1, 1)

    # Handle epoch timestamp
    if time_str.isdigit():
        return datetime.fromtimestamp(int(time_str))

    # Parse relative time: [+-]N[unit][@snap]
    relative_match = re.match(
        r"^([+-]?)(\d+)([a-zA-Z]+)(?:@([a-zA-Z0-9]+))?$", time_str
    )
    if relative_match:
        sign = relative_match.group(1)
        amount = int(relative_match.group(2))
        unit = relative_match.group(3).lower()
        snap = relative_match.group(4)

        if unit not in TIME_UNITS:
            raise ValueError(f"Unknown time unit: {unit}")

        seconds = amount * TIME_UNITS[unit]
        if sign == "-":
            result = reference - timedelta(seconds=seconds)
        else:
            result = reference + timedelta(seconds=seconds)

        if snap:
            result = snap_to_unit(result, snap)

        return result

    # Parse snap-to only: @[unit][N]
    snap_match = re.match(r"^@([a-zA-Z]+)(\d*)$", time_str)
    if snap_match:
        unit = snap_match.group(1)
        day_num = snap_match.group(2)

        # Handle week day snap @w0-@w6
        if unit.startswith("w") and day_num:
            return snap_to_weekday(reference, int(day_num))
        elif unit == "w":
            return snap_to_weekday(reference, 0)
        else:
            return snap_to_unit(reference, unit)

    raise ValueError(f"Invalid time format: {time_str}")


def snap_to_unit(dt: datetime, unit: str) -> datetime:
    """
    Snap datetime to time unit boundary.

    Args:
        dt: Datetime to snap
        unit: Time unit (s, m, h, d, w, mon, q, y)

    Returns:
        Snapped datetime
    """
    unit = unit.lower()

    if unit in ("s", "sec", "second"):
        return dt.replace(microsecond=0)

    if unit in ("m", "min", "minute"):
        return dt.replace(second=0, microsecond=0)

    if unit in ("h", "hr", "hour"):
        return dt.replace(minute=0, second=0, microsecond=0)

    if unit in ("d", "day"):
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    if unit in ("w", "week"):
        # Snap to week start (Sunday = 0)
        return snap_to_weekday(dt, 0)

    if unit in ("mon", "month"):
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if unit in ("q", "quarter"):
        quarter_start = ((dt.month - 1) // 3) * 3 + 1
        return dt.replace(
            month=quarter_start, day=1, hour=0, minute=0, second=0, microsecond=0
        )

    if unit in ("y", "year"):
        return dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    raise ValueError(f"Unknown snap unit: {unit}")


def snap_to_weekday(dt: datetime, day: int) -> datetime:
    """
    Snap datetime to specific weekday.

    Args:
        dt: Datetime to snap
        day: Day of week (0=Sunday, 6=Saturday)

    Returns:
        Datetime snapped to that weekday at midnight
    """
    # Python's weekday() returns 0=Monday, 6=Sunday
    # Splunk uses 0=Sunday, 6=Saturday
    splunk_day = (dt.weekday() + 1) % 7
    days_diff = (splunk_day - day) % 7

    result = dt - timedelta(days=days_diff)
    return result.replace(hour=0, minute=0, second=0, microsecond=0)


def format_splunk_time(
    dt: Union[datetime, int, float],
    format_type: str = "relative",
) -> str:
    """
    Format datetime as Splunk time modifier.

    Args:
        dt: Datetime or epoch timestamp
        format_type: Output format ('relative', 'epoch', 'iso')

    Returns:
        Formatted time string
    """
    if isinstance(dt, (int, float)):
        dt = datetime.fromtimestamp(dt)

    if format_type == "epoch":
        return str(int(dt.timestamp()))

    if format_type == "iso":
        return dt.isoformat()

    if format_type == "relative":
        now = datetime.now()
        diff = now - dt

        if diff.total_seconds() < 0:
            # Future time
            diff = dt - now
            sign = "+"
        else:
            sign = "-"

        seconds = abs(diff.total_seconds())

        if seconds < 60:
            return f"{sign}{int(seconds)}s"
        elif seconds < 3600:
            return f"{sign}{int(seconds / 60)}m"
        elif seconds < 86400:
            return f"{sign}{int(seconds / 3600)}h"
        elif seconds < 604800:
            return f"{sign}{int(seconds / 86400)}d"
        elif seconds < 2592000:
            return f"{sign}{int(seconds / 604800)}w"
        else:
            return f"{sign}{int(seconds / 2592000)}mon"

    raise ValueError(f"Unknown format type: {format_type}")


def validate_time_range(
    earliest: str,
    latest: str,
    reference: Optional[datetime] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate that earliest is before latest.

    Args:
        earliest: Earliest time modifier
        latest: Latest time modifier
        reference: Reference datetime for parsing

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        earliest_dt = parse_splunk_time(earliest, reference)
        latest_dt = parse_splunk_time(latest, reference)

        if earliest_dt > latest_dt:
            return False, f"Earliest time ({earliest}) is after latest time ({latest})"

        return True, None
    except ValueError as e:
        return False, str(e)


def get_relative_time(
    offset: int,
    unit: str = "h",
    snap_to: Optional[str] = None,
) -> str:
    """
    Build relative time modifier string.

    Args:
        offset: Time offset (negative for past, positive for future)
        unit: Time unit (s, m, h, d, w, mon, y)
        snap_to: Optional snap-to unit

    Returns:
        Splunk time modifier string
    """
    if unit not in TIME_UNITS:
        raise ValueError(f"Unknown time unit: {unit}")

    sign = "-" if offset < 0 else ""
    time_str = f"{sign}{abs(offset)}{unit}"

    if snap_to:
        time_str += f"@{snap_to}"

    return time_str


def get_time_range_presets() -> dict:
    """
    Get common time range presets.

    Returns:
        Dictionary of preset names to (earliest, latest) tuples
    """
    return {
        "last_15_minutes": ("-15m", "now"),
        "last_hour": ("-1h", "now"),
        "last_4_hours": ("-4h", "now"),
        "last_24_hours": ("-24h", "now"),
        "last_7_days": ("-7d", "now"),
        "last_30_days": ("-30d", "now"),
        "today": ("@d", "now"),
        "yesterday": ("-1d@d", "@d"),
        "this_week": ("@w0", "now"),
        "last_week": ("-1w@w0", "@w0"),
        "this_month": ("@mon", "now"),
        "last_month": ("-1mon@mon", "@mon"),
        "all_time": ("0", "now"),
    }


def time_to_epoch(time_str: str, reference: Optional[datetime] = None) -> int:
    """
    Convert Splunk time modifier to epoch timestamp.

    Args:
        time_str: Splunk time modifier
        reference: Reference datetime

    Returns:
        Epoch timestamp as integer
    """
    dt = parse_splunk_time(time_str, reference)
    return int(dt.timestamp())


def epoch_to_iso(epoch: int) -> str:
    """
    Convert epoch timestamp to ISO format.

    Args:
        epoch: Epoch timestamp

    Returns:
        ISO formatted string
    """
    return datetime.fromtimestamp(epoch).isoformat()


def get_search_time_bounds(
    earliest: Optional[str] = None,
    latest: Optional[str] = None,
    default_earliest: str = "-24h",
    default_latest: str = "now",
) -> Tuple[str, str]:
    """
    Get time bounds for search with defaults.

    Args:
        earliest: Earliest time (uses default if None)
        latest: Latest time (uses default if None)
        default_earliest: Default earliest time
        default_latest: Default latest time

    Returns:
        Tuple of (earliest, latest) time modifiers
    """
    return (
        earliest if earliest is not None else default_earliest,
        latest if latest is not None else default_latest,
    )
