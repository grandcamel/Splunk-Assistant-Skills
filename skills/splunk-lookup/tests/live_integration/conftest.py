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

# Import splunk_container module directly
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
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
            import logging

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
