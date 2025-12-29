#!/usr/bin/env python3
"""
Splunk Output Formatters

Provides formatting utilities for Splunk data and command output.
Includes table formatting, JSON output, CSV export, and colored terminal output.
"""

import csv
import json
import sys
from datetime import datetime
from io import StringIO
from typing import Any, Dict, List, Optional, Sequence, Union


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


def supports_color() -> bool:
    """Check if terminal supports color output."""
    if not hasattr(sys.stdout, 'isatty'):
        return False
    if not sys.stdout.isatty():
        return False
    return True


def colorize(text: str, color: str) -> str:
    """Apply color to text if terminal supports it."""
    if supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text


def print_success(message: str) -> None:
    """Print success message in green."""
    print(colorize(f"✓ {message}", Colors.GREEN))


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    print(colorize(f"⚠ {message}", Colors.YELLOW))


def print_info(message: str) -> None:
    """Print info message in blue."""
    print(colorize(f"ℹ {message}", Colors.BLUE))


def print_error(message: str) -> None:
    """Print error message in red to stderr."""
    print(colorize(f"✗ {message}", Colors.RED), file=sys.stderr)


def format_json(data: Any, pretty: bool = True, indent: int = 2) -> str:
    """
    Format data as JSON string.

    Args:
        data: Data to format
        pretty: Use pretty printing with indentation
        indent: Indentation level for pretty printing

    Returns:
        JSON formatted string
    """
    if pretty:
        return json.dumps(data, indent=indent, default=str, ensure_ascii=False)
    return json.dumps(data, default=str, ensure_ascii=False)


def format_table(
    data: List[Dict[str, Any]],
    columns: Optional[List[str]] = None,
    headers: Optional[List[str]] = None,
    max_width: int = 40,
    truncate: bool = True,
) -> str:
    """
    Format data as ASCII table.

    Args:
        data: List of dictionaries to format
        columns: Column keys to display (auto-detect if None)
        headers: Header labels (uses column names if None)
        max_width: Maximum column width
        truncate: Truncate values exceeding max_width

    Returns:
        Formatted table string
    """
    if not data:
        return "No data to display."

    # Auto-detect columns from first row
    if columns is None:
        columns = list(data[0].keys())

    # Use column names as headers if not specified
    if headers is None:
        headers = columns

    # Calculate column widths
    widths = []
    for i, col in enumerate(columns):
        header_width = len(str(headers[i]))
        data_width = max(len(str(row.get(col, ''))) for row in data)
        width = min(max(header_width, data_width), max_width)
        widths.append(width)

    def truncate_value(value: str, width: int) -> str:
        """Truncate value to width with ellipsis."""
        value = str(value)
        if truncate and len(value) > width:
            return value[:width - 3] + '...'
        return value

    # Build table
    lines = []

    # Header row
    header_row = ' | '.join(
        str(h).ljust(w) for h, w in zip(headers, widths)
    )
    lines.append(header_row)

    # Separator
    separator = '-+-'.join('-' * w for w in widths)
    lines.append(separator)

    # Data rows
    for row in data:
        values = [truncate_value(row.get(col, ''), w) for col, w in zip(columns, widths)]
        row_str = ' | '.join(v.ljust(w) for v, w in zip(values, widths))
        lines.append(row_str)

    return '\n'.join(lines)


def format_search_results(
    results: Union[Dict[str, Any], List[Dict[str, Any]]],
    fields: Optional[List[str]] = None,
    max_results: int = 50,
    output_format: str = 'table',
) -> str:
    """
    Format search results for display.

    Args:
        results: Search results (Splunk response or result list)
        fields: Fields to display (auto-detect if None)
        max_results: Maximum results to display
        output_format: Output format ('table', 'json', 'csv')

    Returns:
        Formatted results string
    """
    # Extract results from Splunk response format
    if isinstance(results, dict):
        result_list = results.get('results', results.get('rows', []))
        if not result_list and 'entry' in results:
            result_list = [e.get('content', {}) for e in results['entry']]
    else:
        result_list = results

    if not result_list:
        return "No results found."

    # Limit results
    if len(result_list) > max_results:
        result_list = result_list[:max_results]
        truncated = True
    else:
        truncated = False

    # Auto-detect fields
    if fields is None and result_list:
        # Use first result's keys, excluding internal fields
        fields = [k for k in result_list[0].keys() if not k.startswith('_')][:10]

    # Format based on output format
    if output_format == 'json':
        output = format_json(result_list)
    elif output_format == 'csv':
        output = export_csv_string(result_list, fields)
    else:  # table
        output = format_table(result_list, columns=fields)

    if truncated:
        output += f"\n\n... (showing first {max_results} of more results)"

    return output


def format_job_status(job: Dict[str, Any]) -> str:
    """
    Format search job status for display.

    Args:
        job: Job information dictionary

    Returns:
        Formatted status string
    """
    content = job.get('content', job)

    sid = content.get('sid', 'Unknown')
    state = content.get('dispatchState', 'Unknown')
    done_progress = content.get('doneProgress', 0)
    event_count = content.get('eventCount', 0)
    result_count = content.get('resultCount', 0)
    scan_count = content.get('scanCount', 0)
    run_duration = content.get('runDuration', 0)

    # State color
    state_colors = {
        'QUEUED': Colors.YELLOW,
        'PARSING': Colors.YELLOW,
        'RUNNING': Colors.BLUE,
        'FINALIZING': Colors.CYAN,
        'DONE': Colors.GREEN,
        'FAILED': Colors.RED,
        'PAUSED': Colors.MAGENTA,
    }
    state_color = state_colors.get(state, Colors.RESET)

    lines = [
        f"Job ID:     {sid}",
        f"State:      {colorize(state, state_color)}",
        f"Progress:   {done_progress * 100:.1f}%",
        f"Events:     {event_count:,}",
        f"Results:    {result_count:,}",
        f"Scanned:    {scan_count:,}",
        f"Duration:   {run_duration:.2f}s",
    ]

    # Add error message if failed
    if state == 'FAILED':
        messages = content.get('messages', [])
        if messages:
            lines.append(f"Error:      {messages[0].get('text', 'Unknown error')}")

    return '\n'.join(lines)


def format_metadata(meta: Dict[str, Any]) -> str:
    """
    Format metadata information for display.

    Args:
        meta: Metadata dictionary

    Returns:
        Formatted metadata string
    """
    lines = []

    # Index metadata
    if 'totalEventCount' in meta:
        lines.extend([
            f"Index:           {meta.get('title', meta.get('name', 'Unknown'))}",
            f"Total Events:    {meta.get('totalEventCount', 0):,}",
            f"Total Size:      {format_bytes(meta.get('currentDBSizeMB', 0) * 1024 * 1024)}",
            f"Earliest Event:  {format_splunk_time(meta.get('minTime', ''))}",
            f"Latest Event:    {format_splunk_time(meta.get('maxTime', ''))}",
        ])
    # Sourcetype metadata
    elif 'values' in meta:
        lines.append(f"Field:    {meta.get('field', 'Unknown')}")
        lines.append(f"Values:   {len(meta.get('values', []))}")
        for v in meta.get('values', [])[:10]:
            lines.append(f"  - {v.get('value', v)}: {v.get('count', 0):,}")
    else:
        # Generic metadata
        for key, value in meta.items():
            if not key.startswith('_'):
                lines.append(f"{key}: {value}")

    return '\n'.join(lines)


def format_saved_search(search: Dict[str, Any]) -> str:
    """
    Format saved search details for display.

    Args:
        search: Saved search configuration

    Returns:
        Formatted saved search string
    """
    content = search.get('content', search)

    lines = [
        f"Name:           {search.get('name', content.get('name', 'Unknown'))}",
        f"App:            {content.get('eai:acl', {}).get('app', 'Unknown')}",
        f"Owner:          {content.get('eai:acl', {}).get('owner', 'Unknown')}",
        f"Search:         {content.get('search', 'N/A')[:80]}...",
        f"Disabled:       {content.get('disabled', False)}",
        f"Scheduled:      {content.get('is_scheduled', False)}",
    ]

    if content.get('is_scheduled'):
        lines.extend([
            f"Cron:           {content.get('cron_schedule', 'N/A')}",
            f"Next Run:       {content.get('next_scheduled_time', 'N/A')}",
        ])

    return '\n'.join(lines)


def format_bytes(size: Union[int, float]) -> str:
    """
    Format byte size in human-readable format.

    Args:
        size: Size in bytes

    Returns:
        Human-readable size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size) < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def format_splunk_time(time_str: str) -> str:
    """
    Format Splunk timestamp for display.

    Args:
        time_str: Splunk timestamp string

    Returns:
        Human-readable timestamp
    """
    if not time_str:
        return 'N/A'

    try:
        # Try parsing ISO format
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, AttributeError):
        return str(time_str)


def export_csv(
    data: List[Dict[str, Any]],
    file_path: str,
    columns: Optional[List[str]] = None,
) -> str:
    """
    Export data to CSV file.

    Args:
        data: List of dictionaries to export
        file_path: Output file path
        columns: Columns to include (all if None)

    Returns:
        Path to created file
    """
    if not data:
        raise ValueError("No data to export")

    if columns is None:
        columns = list(data[0].keys())

    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)

    return file_path


def export_csv_string(
    data: List[Dict[str, Any]],
    columns: Optional[List[str]] = None,
) -> str:
    """
    Export data to CSV string.

    Args:
        data: List of dictionaries to export
        columns: Columns to include (all if None)

    Returns:
        CSV formatted string
    """
    if not data:
        return ""

    if columns is None:
        columns = list(data[0].keys())

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(data)

    return output.getvalue()


def format_list(
    items: Sequence[Any],
    numbered: bool = False,
    bullet: str = '•',
    max_items: int = 50,
) -> str:
    """
    Format list of items for display.

    Args:
        items: Items to format
        numbered: Use numbered list instead of bullets
        bullet: Bullet character for non-numbered lists
        max_items: Maximum items to display

    Returns:
        Formatted list string
    """
    if not items:
        return "No items."

    lines = []
    truncated = len(items) > max_items

    for i, item in enumerate(items[:max_items], 1):
        prefix = f"{i}." if numbered else bullet
        lines.append(f" {prefix} {item}")

    if truncated:
        lines.append(f" ... and {len(items) - max_items} more")

    return '\n'.join(lines)


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Human-readable duration string
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_count(count: int) -> str:
    """
    Format large count with K/M/B suffix.

    Args:
        count: Count to format

    Returns:
        Formatted count string
    """
    if count < 1000:
        return str(count)
    elif count < 1_000_000:
        return f"{count / 1000:.1f}K"
    elif count < 1_000_000_000:
        return f"{count / 1_000_000:.1f}M"
    else:
        return f"{count / 1_000_000_000:.1f}B"
