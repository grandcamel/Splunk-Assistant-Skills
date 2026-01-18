#!/usr/bin/env python3
"""
Pytest configuration for splunk-metadata live integration tests.

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
