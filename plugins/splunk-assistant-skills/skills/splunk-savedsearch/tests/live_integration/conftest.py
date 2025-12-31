#!/usr/bin/env python3
"""
Pytest configuration for splunk-savedsearch live integration tests.

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
    "savedsearch_helper",
    "test_savedsearch_name",
]


# =============================================================================
# Skill-Specific Fixtures
# =============================================================================


class SavedSearchHelper:
    """Helper class for saved search operations in tests."""

    def __init__(self, client, app="search"):
        self.client = client
        self.app = app
        self._created_searches = []

    def create(self, name, search, **kwargs):
        """Create a saved search."""
        data = {"name": name, "search": search}
        data.update(kwargs)

        try:
            self.client.post(
                f"/servicesNS/nobody/{self.app}/saved/searches",
                data=data,
                operation="create saved search",
            )
            self._created_searches.append(name)
            return True
        except Exception:
            return False

    def delete(self, name):
        """Delete a saved search."""
        try:
            self.client.delete(
                f"/servicesNS/nobody/{self.app}/saved/searches/{name}",
                operation="delete saved search",
            )
            if name in self._created_searches:
                self._created_searches.remove(name)
            return True
        except Exception:
            return False

    def dispatch(self, name):
        """Dispatch a saved search and return the SID."""
        response = self.client.post(
            f"/servicesNS/nobody/{self.app}/saved/searches/{name}/dispatch",
            data={"dispatch.now": "true"},
            operation="dispatch saved search",
        )
        return response.get("sid")

    def cleanup(self):
        """Clean up all created saved searches."""
        for name in self._created_searches[:]:
            try:
                self.delete(name)
            except Exception:
                pass


@pytest.fixture(scope="session")
def savedsearch_helper(splunk_client):
    """Fixture providing saved search helper."""
    helper = SavedSearchHelper(splunk_client)
    yield helper
    helper.cleanup()


@pytest.fixture
def test_savedsearch_name():
    """Generate a unique test saved search name."""
    return f"test_savedsearch_{uuid.uuid4().hex[:8]}"
