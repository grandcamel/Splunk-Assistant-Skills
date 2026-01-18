#!/usr/bin/env python3
"""
Pytest configuration for splunk-lookup live integration tests.

Shared fixtures are automatically loaded from shared/tests/live_integration/fixtures.py
via pytest_plugins. The shared path is configured in pytest.ini's pythonpath.
"""

import logging
import uuid

import pytest

# Load all shared fixtures (splunk_connection, splunk_client, test_index, etc.)
pytest_plugins = ["fixtures"]


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
