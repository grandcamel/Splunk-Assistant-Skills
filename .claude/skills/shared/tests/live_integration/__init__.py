"""
Live Integration Test Framework for Splunk Assistant Skills

This module provides infrastructure for running integration tests against
a real Splunk instance, either via Docker (testcontainers) or an external
Splunk deployment.

Usage:
    # Run with Docker (default)
    pytest .claude/skills/*/tests/live_integration/ -v

    # Run against external Splunk
    SPLUNK_TEST_URL=https://splunk.example.com:8089 \
    SPLUNK_TEST_TOKEN=your-token \
    pytest .claude/skills/*/tests/live_integration/ -v

    # Skip Docker tests in CI without Docker
    pytest -m "not docker_required"
"""

from .fixtures import (
    splunk_client,
    splunk_connection,
    test_data,
    test_index,
)
from .splunk_container import (
    ExternalSplunkConnection,
    SplunkContainer,
    get_splunk_connection,
)
from .test_utils import (
    cleanup_test_data,
    generate_test_events,
    wait_for_indexing,
)

__all__ = [
    "SplunkContainer",
    "ExternalSplunkConnection",
    "get_splunk_connection",
    "splunk_connection",
    "splunk_client",
    "test_index",
    "test_data",
    "generate_test_events",
    "wait_for_indexing",
    "cleanup_test_data",
]
