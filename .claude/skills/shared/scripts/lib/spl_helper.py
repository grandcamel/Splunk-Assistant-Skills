#!/usr/bin/env python3
"""
SPL Query Building and Parsing

Provides utilities for building, parsing, validating, and optimizing
SPL (Search Processing Language) queries.

Features:
    - Query building with time bounds and field extraction
    - Syntax validation
    - Command pipeline parsing
    - Complexity estimation
    - Query optimization suggestions
"""

import re
from typing import Any, Dict, List, Optional, Tuple

# Common SPL commands by category
GENERATING_COMMANDS = {
    "search",
    "tstats",
    "mstats",
    "inputlookup",
    "metadata",
    "rest",
    "eventcount",
    "dbinspect",
    "datamodel",
    "pivot",
    "loadjob",
    "metasearch",
    "mcatalog",
    "mpreview",
}

TRANSFORMING_COMMANDS = {
    "stats",
    "chart",
    "timechart",
    "top",
    "rare",
    "eval",
    "where",
    "sort",
    "head",
    "tail",
    "table",
    "fields",
    "rename",
    "rex",
    "spath",
    "mvexpand",
    "transaction",
    "dedup",
    "cluster",
    "bucket",
    "bin",
    "predict",
    "trendline",
    "anomalies",
    "outlier",
}

STREAMING_COMMANDS = {
    "eval",
    "where",
    "regex",
    "rex",
    "rename",
    "replace",
    "fields",
    "table",
    "spath",
    "convert",
    "makemv",
    "mvexpand",
    "lookup",
}

EXPENSIVE_COMMANDS = {
    "transaction",
    "join",
    "append",
    "appendcols",
    "map",
    "foreach",
    "cluster",
    "kmeans",
    "anomalydetection",
    "predict",
}


def build_search(
    base_query: str,
    earliest_time: Optional[str] = None,
    latest_time: Optional[str] = None,
    fields: Optional[List[str]] = None,
    head: Optional[int] = None,
    index: Optional[str] = None,
    sourcetype: Optional[str] = None,
) -> str:
    """
    Build complete search query with common modifications.

    Args:
        base_query: Base SPL query
        earliest_time: Earliest time modifier
        latest_time: Latest time modifier
        fields: Fields to extract
        head: Limit results count
        index: Index to search (prepended if not in query)
        sourcetype: Sourcetype filter (prepended if not in query)

    Returns:
        Complete SPL query string
    """
    query = base_query.strip()

    # Add index if not present and specified
    if index and not re.search(r"\bindex\s*=", query, re.IGNORECASE):
        if not query.startswith("|"):
            query = f"index={index} {query}"

    # Add sourcetype if not present and specified
    if sourcetype and not re.search(r"\bsourcetype\s*=", query, re.IGNORECASE):
        if not query.startswith("|"):
            query = f"{query} sourcetype={sourcetype}"

    # Add time bounds
    if earliest_time or latest_time:
        query = add_time_bounds(query, earliest_time, latest_time)

    # Add field extraction
    if fields:
        query = add_field_extraction(query, fields)

    # Add head limit
    if head:
        query = add_head_limit(query, head)

    return query


def add_time_bounds(
    spl: str,
    earliest: Optional[str] = None,
    latest: Optional[str] = None,
) -> str:
    """
    Add time bounds to SPL query.

    Time modifiers are added at the start of the search for generating commands.

    Args:
        spl: SPL query
        earliest: Earliest time modifier
        latest: Latest time modifier

    Returns:
        SPL with time bounds
    """
    spl = spl.strip()

    # Check if query already has time bounds
    has_earliest = re.search(r"\bearliest\s*=", spl, re.IGNORECASE)
    has_latest = re.search(r"\blatest\s*=", spl, re.IGNORECASE)

    if has_earliest and has_latest:
        return spl

    time_parts = []
    if earliest and not has_earliest:
        time_parts.append(f"earliest={earliest}")
    if latest and not has_latest:
        time_parts.append(f"latest={latest}")

    if not time_parts:
        return spl

    time_clause = " ".join(time_parts)

    # Insert time bounds after initial search/index
    if spl.startswith("|"):
        # Generating command - add time to relevant commands
        return spl  # Time handled by search context
    elif re.match(r"^(search\s+)?index\s*=", spl, re.IGNORECASE):
        # Has index clause - insert after index
        match = re.match(r"^((?:search\s+)?index\s*=\s*\S+)", spl, re.IGNORECASE)
        if match:
            return f"{match.group(1)} {time_clause} {spl[match.end():]}"
    else:
        # Prepend to query
        return f"{time_clause} {spl}"

    return spl


def add_field_extraction(spl: str, fields: List[str]) -> str:
    """
    Add fields command to limit returned fields.

    Args:
        spl: SPL query
        fields: List of field names to extract

    Returns:
        SPL with fields command
    """
    if not fields:
        return spl

    spl = spl.strip()

    # Check if fields command already exists at the end
    if re.search(r"\|\s*fields\s+[^|]+$", spl, re.IGNORECASE):
        return spl

    # Check if table command exists (implies field selection)
    if re.search(r"\|\s*table\s+[^|]+$", spl, re.IGNORECASE):
        return spl

    field_str = ", ".join(fields)
    return f"{spl} | fields {field_str}"


def add_head_limit(spl: str, limit: int) -> str:
    """
    Add head command to limit results.

    Args:
        spl: SPL query
        limit: Maximum number of results

    Returns:
        SPL with head command
    """
    spl = spl.strip()

    # Check if head/tail command already exists at the end
    if re.search(r"\|\s*(head|tail)\s+\d+\s*$", spl, re.IGNORECASE):
        return spl

    return f"{spl} | head {limit}"


def validate_spl_syntax(spl: str) -> Tuple[bool, List[str]]:
    """
    Validate SPL syntax and return issues.

    Args:
        spl: SPL query to validate

    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []

    if not spl or not spl.strip():
        return False, ["SPL query cannot be empty"]

    spl = spl.strip()

    # Check balanced parentheses
    paren_count = 0
    bracket_count = 0
    brace_count = 0
    in_string = False
    string_char = None

    for i, char in enumerate(spl):
        if char in "\"'":
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
        elif not in_string:
            if char == "(":
                paren_count += 1
            elif char == ")":
                paren_count -= 1
            elif char == "[":
                bracket_count += 1
            elif char == "]":
                bracket_count -= 1
            elif char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1

    if paren_count != 0:
        issues.append("Unbalanced parentheses")
    if bracket_count != 0:
        issues.append("Unbalanced square brackets")
    if brace_count != 0:
        issues.append("Unbalanced curly braces")
    if in_string:
        issues.append("Unterminated string literal")

    # Check for empty pipes
    if re.search(r"\|\s*\|", spl):
        issues.append("Empty pipe segment")

    # Check for trailing pipe
    if spl.rstrip().endswith("|"):
        issues.append("Query cannot end with a pipe")

    # Check for invalid command start
    commands = parse_spl_commands(spl)
    for cmd_name, _ in commands:
        if cmd_name.startswith("="):
            issues.append(f"Invalid command: {cmd_name}")

    return len(issues) == 0, issues


def parse_spl_commands(spl: str) -> List[Tuple[str, str]]:
    """
    Parse SPL into command pipeline.

    Args:
        spl: SPL query

    Returns:
        List of (command_name, arguments) tuples
    """
    commands = []
    spl = spl.strip()

    # Handle implicit search command
    if not spl.startswith("|"):
        spl = f"search {spl}"

    # Split by pipe, handling nested brackets and strings
    current_cmd = []
    in_string = False
    string_char = None
    bracket_depth = 0

    for char in spl:
        if char in "\"'":
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
            current_cmd.append(char)
        elif not in_string:
            if char in "[(":
                bracket_depth += 1
                current_cmd.append(char)
            elif char in "])":
                bracket_depth -= 1
                current_cmd.append(char)
            elif char == "|" and bracket_depth == 0:
                cmd_str = "".join(current_cmd).strip()
                if cmd_str:
                    cmd_parts = cmd_str.split(None, 1)
                    cmd_name = cmd_parts[0]
                    cmd_args = cmd_parts[1] if len(cmd_parts) > 1 else ""
                    commands.append((cmd_name, cmd_args))
                current_cmd = []
            else:
                current_cmd.append(char)
        else:
            current_cmd.append(char)

    # Handle last command
    cmd_str = "".join(current_cmd).strip()
    if cmd_str:
        cmd_parts = cmd_str.split(None, 1)
        cmd_name = cmd_parts[0]
        cmd_args = cmd_parts[1] if len(cmd_parts) > 1 else ""
        commands.append((cmd_name, cmd_args))

    return commands


def estimate_search_complexity(spl: str) -> str:
    """
    Estimate search complexity.

    Args:
        spl: SPL query

    Returns:
        Complexity level: 'simple', 'medium', 'complex'
    """
    commands = parse_spl_commands(spl)
    cmd_names = {cmd[0].lower() for cmd in commands}

    # Check for expensive commands
    expensive = cmd_names & EXPENSIVE_COMMANDS
    if expensive:
        return "complex"

    # Check for multiple transforming commands
    transforming = cmd_names & TRANSFORMING_COMMANDS
    if len(transforming) > 3:
        return "complex"
    if len(transforming) > 1:
        return "medium"

    # Check for subsearches
    if re.search(r"\[.*\]", spl):
        return "complex"

    # Check for macro usage
    if re.search(r"`[^`]+`", spl):
        return "medium"

    return "simple"


def optimize_spl(spl: str) -> Tuple[str, List[str]]:
    """
    Apply optimization suggestions to SPL query.

    Args:
        spl: SPL query

    Returns:
        Tuple of (optimized_spl, list of changes made)
    """
    changes = []
    optimized = spl.strip()

    # Ensure time bounds exist
    if not re.search(r"\b(earliest|latest)\s*=", optimized, re.IGNORECASE):
        changes.append("Consider adding time bounds (earliest/latest)")

    # Check for missing fields command with search
    if "search" in optimized.lower() and not re.search(
        r"\|\s*fields\b", optimized, re.IGNORECASE
    ):
        if not re.search(r"\|\s*table\b", optimized, re.IGNORECASE):
            changes.append("Consider adding | fields to limit data transfer")

    # Suggest moving fields early
    commands = parse_spl_commands(optimized)
    cmd_names = [cmd[0].lower() for cmd in commands]
    if "fields" in cmd_names:
        fields_idx = cmd_names.index("fields")
        if fields_idx > 2 and "search" in cmd_names:
            changes.append("Consider moving 'fields' command earlier in pipeline")

    # Check for transaction without limits
    if "transaction" in cmd_names:
        # Check if maxspan/maxpause are set
        for cmd_name, cmd_args in commands:
            if cmd_name.lower() == "transaction":
                if "maxspan" not in cmd_args.lower():
                    changes.append("Add maxspan to transaction command to limit scope")
                break

    # Check for expensive join without limits
    if "join" in cmd_names:
        changes.append(
            "Consider using stats/lookup instead of join for better performance"
        )

    # Check for wildcard in index
    if re.search(r"index\s*=\s*\*", optimized, re.IGNORECASE):
        changes.append(
            "Avoid index=* - specify explicit indexes for better performance"
        )

    return optimized, changes


def get_search_command_info(command: str) -> Dict[str, Any]:
    """
    Get information about a SPL command.

    Args:
        command: Command name

    Returns:
        Dictionary with command information
    """
    command = command.lower()

    info = {
        "name": command,
        "is_generating": command in GENERATING_COMMANDS,
        "is_transforming": command in TRANSFORMING_COMMANDS,
        "is_streaming": command in STREAMING_COMMANDS,
        "is_expensive": command in EXPENSIVE_COMMANDS,
    }

    return info


def extract_fields_from_spl(spl: str) -> List[str]:
    """
    Extract field names referenced in SPL query.

    Args:
        spl: SPL query

    Returns:
        List of field names
    """
    fields = set()

    # Common patterns for field references
    patterns = [
        r"\bby\s+([a-zA-Z_][\w.]*(?:\s*,\s*[a-zA-Z_][\w.]*)*)",  # by clause
        r"\bfields?\s+[+-]?\s*([a-zA-Z_][\w.]*(?:\s*,\s*[a-zA-Z_][\w.]*)*)",  # fields command
        r"\btable\s+([a-zA-Z_][\w.]*(?:\s*,\s*[a-zA-Z_][\w.]*)*)",  # table command
        r"([a-zA-Z_][\w.]*)\s*=",  # field=value
        r"\beval\s+([a-zA-Z_][\w.]*)\s*=",  # eval field=
        r"\brename\s+[^\s]+\s+(?:as|AS)\s+([a-zA-Z_][\w.]*)",  # rename as
    ]

    for pattern in patterns:
        matches = re.findall(pattern, spl, re.IGNORECASE)
        for match in matches:
            # Handle comma-separated fields
            if "," in match:
                for field in match.split(","):
                    fields.add(field.strip())
            else:
                fields.add(match.strip())

    # Remove Splunk internal fields if present
    fields = {
        f
        for f in fields
        if not f.startswith("_") or f in ("_time", "_raw", "_indextime")
    }

    return sorted(list(fields))


def quote_field_value(value: str) -> str:
    """
    Quote a field value if necessary for SPL.

    Args:
        value: Value to quote

    Returns:
        Quoted value if needed
    """
    # Check if quoting is needed
    if re.match(r"^[a-zA-Z0-9_.-]+$", value):
        return value

    # Escape quotes and wrap
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def build_filter_clause(filters: Dict[str, Any]) -> str:
    """
    Build SPL filter clause from dictionary.

    Args:
        filters: Dictionary of field=value filters

    Returns:
        SPL filter string
    """
    clauses = []

    for field, value in filters.items():
        if isinstance(value, list):
            # OR clause for multiple values
            value_strs = [quote_field_value(str(v)) for v in value]
            clauses.append(f"({' OR '.join(f'{field}={v}' for v in value_strs)})")
        elif value is None:
            clauses.append(f"NOT {field}=*")
        elif isinstance(value, bool):
            clauses.append(f"{field}={str(value).lower()}")
        else:
            clauses.append(f"{field}={quote_field_value(str(value))}")

    return " ".join(clauses)
