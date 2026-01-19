#!/usr/bin/env python3
"""
Pytest configuration for splunk-savedsearch live integration tests.

Shared fixtures are automatically loaded from shared/tests/live_integration/fixtures.py
via pytest_plugins. The shared path is configured in pytest.ini's pythonpath.
"""

import uuid

import pytest

# Load all shared fixtures (splunk_connection, splunk_client, test_index, etc.)
pytest_plugins = ["fixtures"]


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
