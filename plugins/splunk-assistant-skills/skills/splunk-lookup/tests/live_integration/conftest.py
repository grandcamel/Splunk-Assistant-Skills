#!/usr/bin/env python3
"""
Pytest configuration for splunk-lookup live integration tests.

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
    "lookup_helper",
    "test_lookup_name",
]


# =============================================================================
# Skill-Specific Fixtures
# =============================================================================


class LookupHelper:
    """Helper class for lookup operations in tests."""

    def __init__(self, client, app="search"):
        self.client = client
        self.app = app
        self._created_lookups = []

    def upload(self, name, content):
        """Upload a lookup file."""
        try:
            # Use the client's upload_lookup method which handles the eai:data format
            self.client.upload_lookup(
                lookup_name=name,
                content=content,
                app=self.app,
            )
            self._created_lookups.append(name)
            return True
        except Exception as e:
            logging.error(f"Upload failed: {e}")
            return False

    def delete(self, name):
        """Delete a lookup file."""
        try:
            self.client.delete(
                f"/servicesNS/nobody/{self.app}/data/lookup-table-files/{name}",
                operation="delete lookup",
            )
            if name in self._created_lookups:
                self._created_lookups.remove(name)
            return True
        except Exception:
            return False

    def cleanup(self):
        """Clean up all created lookups."""
        for name in self._created_lookups[:]:
            try:
                self.delete(name)
            except Exception:
                pass


@pytest.fixture(scope="session")
def lookup_helper(splunk_client):
    """Fixture providing lookup helper."""
    helper = LookupHelper(splunk_client)
    yield helper
    helper.cleanup()


@pytest.fixture
def test_lookup_name():
    """Generate a unique test lookup name."""
    return f"test_lookup_{uuid.uuid4().hex[:8]}.csv"
