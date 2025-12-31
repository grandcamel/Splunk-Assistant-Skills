#!/usr/bin/env python3
"""
Pytest configuration for splunk-metadata live integration tests.

Imports fixtures from the shared live_integration module to ensure
a single Splunk container is reused across all skills.
"""

import logging
import sys
import uuid
from pathlib import Path

import pytest
import urllib3

logging.basicConfig(level=logging.INFO)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add shared test utilities to path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path / "tests" / "live_integration"))

# Import session-scoped fixtures from shared module
# DO NOT redefine splunk_connection - this ensures a single container is shared
from fixtures import (
    splunk_connection,
    splunk_client,
    splunk_info,
    test_index_name,
    test_index,
    test_data,
    fresh_test_data,
    search_helper,
    job_helper,
)

# Re-export for pytest discovery
__all__ = [
    "splunk_connection",
    "splunk_client",
    "splunk_info",
    "test_index_name",
    "test_index",
    "test_data",
    "fresh_test_data",
    "search_helper",
    "job_helper",
    "index_helper",
    "unique_index_name",
]


# =============================================================================
# Skill-Specific Fixtures
# =============================================================================


class IndexHelper:
    """Helper class for index operations in tests."""

    def __init__(self, client):
        self.client = client
        self._created_indexes = []

    def create(self, name):
        """Create an index."""
        try:
            self.client.post(
                "/data/indexes", data={"name": name}, operation="create index"
            )
            self._created_indexes.append(name)
            return True
        except Exception:
            return False

    def delete(self, name):
        """Delete an index."""
        try:
            self.client.delete(f"/data/indexes/{name}", operation="delete index")
            if name in self._created_indexes:
                self._created_indexes.remove(name)
            return True
        except Exception:
            return False

    def cleanup(self):
        """Clean up all created indexes."""
        for name in self._created_indexes[:]:
            try:
                self.delete(name)
            except Exception:
                pass


@pytest.fixture(scope="session")
def index_helper(splunk_client):
    """Fixture providing index helper."""
    helper = IndexHelper(splunk_client)
    yield helper
    helper.cleanup()


@pytest.fixture
def unique_index_name():
    """Generate a unique test index name."""
    return f"test_idx_{uuid.uuid4().hex[:8]}"
