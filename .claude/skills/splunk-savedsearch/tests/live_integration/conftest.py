#!/usr/bin/env python3
"""Pytest configuration for live integration tests."""

import os
import sys
import logging
import uuid
from pathlib import Path

import pytest

logging.basicConfig(level=logging.INFO)
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add shared lib to path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
lib_path = shared_path / "scripts" / "lib"

if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

# Import splunk_container module directly
sys.path.insert(0, str(shared_path / "tests" / "live_integration"))
from splunk_container import (
    SplunkContainer,
    ExternalSplunkConnection,
    get_splunk_connection,
)


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "live: marks tests as requiring live Splunk connection"
    )
    config.addinivalue_line(
        "markers", "destructive: marks tests that modify Splunk configuration"
    )


@pytest.fixture(scope="session")
def splunk_connection():
    connection = get_splunk_connection()
    if isinstance(connection, SplunkContainer):
        connection.start()
        yield connection
        connection.stop()
    else:
        yield connection


@pytest.fixture(scope="session")
def splunk_client(splunk_connection):
    yield splunk_connection.get_client()


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
