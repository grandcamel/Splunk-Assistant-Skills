#!/usr/bin/env python3
"""
Test Utilities for Splunk Live Integration Tests

Provides utilities for:
- Generating synthetic test data via SPL
- Waiting for data to be indexed
- Cleaning up test artifacts
- Common test assertions
"""

import time
import random
import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def generate_test_events(
    connection,
    index: str,
    count: int = 100,
    fields: Optional[Dict[str, Any]] = None,
    earliest: str = "-1h",
    latest: str = "now",
) -> int:
    """
    Generate synthetic test events using SPL | makeresults.

    This approach doesn't require HEC or external data files.
    Events are generated and indexed directly via SPL.

    Args:
        connection: SplunkContainer or ExternalSplunkConnection
        index: Target index for the events
        count: Number of events to generate
        fields: Dictionary of field names to values (or lists for random selection)
        earliest: Earliest time for event timestamps
        latest: Latest time for event timestamps

    Returns:
        int: Number of events generated

    Example:
        generate_test_events(
            connection,
            index="test",
            count=100,
            fields={
                "sourcetype": "access_combined",
                "host": ["web01", "web02", "web03"],
                "status": [200, 200, 200, 404, 500],
            }
        )
    """
    fields = fields or {}

    # Build the SPL query for generating events
    spl_parts = [
        f"| makeresults count={count}",
        "| eval _time=_time - random() % 3600",  # Spread events over last hour
    ]

    # Add field assignments
    for field_name, field_value in fields.items():
        if isinstance(field_value, list):
            # Random selection from list
            values_str = ", ".join(f'"{v}"' for v in field_value)
            spl_parts.append(
                f'| eval {field_name}=mvindex(split("{",".join(str(v) for v in field_value)}", ","), random() % {len(field_value)})'
            )
        else:
            # Static value
            spl_parts.append(f'| eval {field_name}="{field_value}"')

    # Add a unique event ID
    spl_parts.append("| eval event_id=md5(_time.random())")

    # Add raw event content
    spl_parts.append('| eval _raw=_time." ".host." ".sourcetype." event_id=".event_id')

    # Collect to the target index
    spl_parts.append(
        f'| collect index="{index}" sourcetype="{fields.get("sourcetype", "test_events")}"'
    )

    spl = " ".join(spl_parts)

    logger.debug(f"Generating events with SPL: {spl}")

    try:
        # Execute the search to generate events
        client = connection.get_client()
        client.post(
            "/search/jobs/oneshot",
            data={
                "search": spl,
                "output_mode": "json",
                "earliest_time": earliest,
                "latest_time": latest,
            },
            timeout=120,
            operation="generate test events",
        )
        logger.info(f"Generated {count} test events in index={index}")
        return count
    except Exception as e:
        logger.error(f"Failed to generate test events: {e}")
        return 0


def generate_simple_events(
    connection,
    index: str,
    count: int = 10,
    sourcetype: str = "test_events",
    host: str = "testhost",
    message: str = "Test event",
) -> int:
    """
    Generate simple test events with minimal configuration.

    Args:
        connection: SplunkContainer or ExternalSplunkConnection
        index: Target index
        count: Number of events
        sourcetype: Sourcetype for events
        host: Host field value
        message: Message content

    Returns:
        int: Number of events generated
    """
    spl = f"""
    | makeresults count={count}
    | eval _time=_time - random() % 3600
    | eval host="{host}"
    | eval message="{message} " . (random() % 1000)
    | eval _raw=_time . " " . host . " " . message
    | collect index="{index}" sourcetype="{sourcetype}"
    """

    try:
        client = connection.get_client()
        client.post(
            "/search/jobs/oneshot",
            data={"search": spl, "output_mode": "json"},
            timeout=60,
            operation="generate simple events",
        )
        return count
    except Exception as e:
        logger.error(f"Failed to generate simple events: {e}")
        return 0


def wait_for_indexing(
    connection,
    index: str,
    min_events: int = 1,
    timeout: int = 60,
    poll_interval: float = 2.0,
) -> bool:
    """
    Wait for events to be indexed and searchable.

    Args:
        connection: SplunkContainer or ExternalSplunkConnection
        index: Index to check
        min_events: Minimum number of events expected
        timeout: Maximum time to wait in seconds
        poll_interval: Time between checks in seconds

    Returns:
        bool: True if events are available, False if timeout
    """
    client = connection.get_client()
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = client.post(
                "/search/jobs/oneshot",
                data={
                    "search": f"search index={index} | stats count",
                    "output_mode": "json",
                    "earliest_time": "-24h",
                    "latest_time": "now",
                },
                timeout=30,
                operation="check indexing",
            )

            results = response.get("results", [])
            if results:
                count = int(results[0].get("count", 0))
                if count >= min_events:
                    logger.info(f"Index {index} has {count} events (>= {min_events})")
                    return True

        except Exception as e:
            logger.debug(f"Indexing check failed: {e}")

        time.sleep(poll_interval)

    logger.warning(f"Timeout waiting for {min_events} events in index {index}")
    return False


def cleanup_test_data(
    connection,
    index: str,
    delete_index: bool = False,
) -> bool:
    """
    Clean up test data from an index.

    Args:
        connection: SplunkContainer or ExternalSplunkConnection
        index: Index to clean
        delete_index: If True, delete the entire index

    Returns:
        bool: True if cleanup successful
    """
    try:
        if delete_index:
            return connection.delete_test_index(index)
        else:
            # Just delete the events (requires admin access and delete enabled)
            client = connection.get_client()
            client.post(
                "/search/jobs/oneshot",
                data={
                    "search": f"search index={index} | delete",
                    "output_mode": "json",
                },
                timeout=60,
                operation="delete test events",
            )
            return True
    except Exception as e:
        logger.warning(f"Failed to cleanup test data: {e}")
        return False


def cancel_all_jobs(connection, user: Optional[str] = None) -> int:
    """
    Cancel all running search jobs.

    Args:
        connection: SplunkContainer or ExternalSplunkConnection
        user: Optional user filter

    Returns:
        int: Number of jobs cancelled
    """
    client = connection.get_client()
    cancelled = 0

    try:
        response = client.get("/search/jobs", operation="list jobs")
        for entry in response.get("entry", []):
            content = entry.get("content", {})
            if not content.get("isDone") and not content.get("isFailed"):
                sid = entry.get("name")
                try:
                    client.post(
                        f"/search/v2/jobs/{sid}/control",
                        data={"action": "cancel"},
                        operation=f"cancel job {sid}",
                    )
                    cancelled += 1
                except Exception:
                    pass
    except Exception as e:
        logger.warning(f"Failed to cancel jobs: {e}")

    return cancelled


class EventBuilder:
    """
    Builder class for constructing test event SPL.

    Example:
        spl = (EventBuilder()
            .with_count(100)
            .with_index("test")
            .with_field("host", ["web01", "web02"])
            .with_field("status", [200, 404, 500])
            .with_timestamp_spread(3600)
            .build())
    """

    def __init__(self):
        self.count = 10
        self.index = "main"
        self.sourcetype = "test_events"
        self.fields: Dict[str, Any] = {}
        self.timestamp_spread = 3600
        self.include_raw = True

    def with_count(self, count: int) -> "EventBuilder":
        """Set event count."""
        self.count = count
        return self

    def with_index(self, index: str) -> "EventBuilder":
        """Set target index."""
        self.index = index
        return self

    def with_sourcetype(self, sourcetype: str) -> "EventBuilder":
        """Set sourcetype."""
        self.sourcetype = sourcetype
        self.fields["sourcetype"] = sourcetype
        return self

    def with_field(self, name: str, value: Union[str, int, List]) -> "EventBuilder":
        """Add a field with static value or list for random selection."""
        self.fields[name] = value
        return self

    def with_timestamp_spread(self, seconds: int) -> "EventBuilder":
        """Set timestamp spread in seconds."""
        self.timestamp_spread = seconds
        return self

    def with_raw(self, include: bool = True) -> "EventBuilder":
        """Include _raw field generation."""
        self.include_raw = include
        return self

    def build(self) -> str:
        """Build the SPL query."""
        parts = [
            f"| makeresults count={self.count}",
            f"| eval _time=_time - random() % {self.timestamp_spread}",
        ]

        for name, value in self.fields.items():
            if isinstance(value, list):
                values_csv = ",".join(str(v) for v in value)
                parts.append(
                    f'| eval {name}=mvindex(split("{values_csv}", ","), random() % {len(value)})'
                )
            else:
                parts.append(f'| eval {name}="{value}"')

        parts.append("| eval event_id=md5(_time.random())")

        if self.include_raw:
            field_names = list(self.fields.keys())
            raw_expr = '" ".'.join([f"{f}" for f in field_names[:5]])
            parts.append(f'| eval _raw=_time." ".{raw_expr}')

        parts.append(f'| collect index="{self.index}" sourcetype="{self.sourcetype}"')

        return " ".join(parts)


def assert_search_returns_results(
    connection,
    spl: str,
    min_count: int = 1,
    message: str = None,
) -> List[Dict]:
    """
    Assert that a search returns at least min_count results.

    Args:
        connection: SplunkContainer or ExternalSplunkConnection
        spl: SPL query
        min_count: Minimum expected results
        message: Optional assertion message

    Returns:
        List of result dictionaries

    Raises:
        AssertionError: If result count is less than min_count
    """
    results = connection.execute_search(spl)
    count = len(results)

    if count < min_count:
        msg = message or f"Expected at least {min_count} results, got {count}"
        raise AssertionError(msg)

    return results


def assert_search_returns_empty(
    connection,
    spl: str,
    message: str = None,
) -> None:
    """
    Assert that a search returns no results.

    Args:
        connection: SplunkContainer or ExternalSplunkConnection
        spl: SPL query
        message: Optional assertion message

    Raises:
        AssertionError: If results are returned
    """
    results = connection.execute_search(spl)

    if results:
        msg = message or f"Expected no results, got {len(results)}"
        raise AssertionError(msg)


def get_splunk_version(connection) -> tuple:
    """
    Get Splunk version as a tuple.

    Returns:
        tuple: Version tuple (major, minor, patch)
    """
    client = connection.get_client()
    info = client.get_server_info()
    version_str = info.get("version", "0.0.0")
    parts = version_str.split(".")[:3]
    return tuple(int(p) for p in parts)


def skip_if_version_below(connection, min_version: tuple, reason: str = None):
    """
    Skip test if Splunk version is below minimum.

    Args:
        connection: SplunkContainer or ExternalSplunkConnection
        min_version: Minimum version tuple (major, minor, patch)
        reason: Skip reason
    """
    import pytest

    current = get_splunk_version(connection)
    if current < min_version:
        version_str = ".".join(str(v) for v in min_version)
        pytest.skip(reason or f"Requires Splunk {version_str}+")
