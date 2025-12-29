#!/usr/bin/env python3
"""Pytest configuration for live integration tests."""

import logging
import os
import sys
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
    ExternalSplunkConnection,
    SplunkContainer,
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
def test_index_name():
    """Generate a unique test index name."""
    return f"test_idx_{uuid.uuid4().hex[:8]}"
