"""
Live integration test infrastructure for Splunk Assistant Skills.

This package provides fixtures and utilities for testing against a real
Splunk instance (Docker container or external).

Usage in skill tests:
    # In your skill's tests/live_integration/conftest.py
    pytest_plugins = ["fixtures"]

Environment Variables:
    SPLUNK_TEST_URL: Splunk instance URL
    SPLUNK_TEST_TOKEN: Admin authentication token
    SPLUNK_TEST_INDEX: Test index name (default: test_integration)

Builders:
    EventBuilder: Fluent API for generating test events via SPL

        spl = (EventBuilder()
            .with_count(100)
            .with_index("test")
            .with_field("host", ["web01", "web02"])
            .with_field("status", [200, 404, 500])
            .with_timestamp_spread(3600)
            .build())
"""

from .splunk_container import (
    ExternalSplunkConnection,
    SplunkContainer,
    get_splunk_connection,
)
from .test_utils import (
    EventBuilder,
    assert_search_returns_empty,
    assert_search_returns_results,
    cancel_all_jobs,
    cleanup_test_data,
    generate_simple_events,
    generate_test_events,
    get_splunk_version,
    skip_if_version_below,
    wait_for_indexing,
)

__all__ = [
    # Connection
    "SplunkContainer",
    "ExternalSplunkConnection",
    "get_splunk_connection",
    # Builders
    "EventBuilder",
    # Test data generation
    "generate_test_events",
    "generate_simple_events",
    "wait_for_indexing",
    "cleanup_test_data",
    "cancel_all_jobs",
    # Assertions
    "assert_search_returns_results",
    "assert_search_returns_empty",
    # Version utilities
    "get_splunk_version",
    "skip_if_version_below",
]
