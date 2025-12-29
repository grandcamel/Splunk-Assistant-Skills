#!/usr/bin/env python3
"""Pytest configuration for live integration tests."""

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


class KVStoreHelper:
    """Helper class for KV Store operations in tests."""

    def __init__(self, client, app="search"):
        self.client = client
        self.app = app
        self._created_collections = []

    def create_collection(self, name, fields=None):
        """Create a KV Store collection."""
        data = {"name": name}
        if fields:
            for field_name, field_type in fields.items():
                data[f"field.{field_name}"] = field_type

        try:
            self.client.post(
                f"/servicesNS/nobody/{self.app}/storage/collections/config",
                data=data,
                operation="create collection",
            )
            self._created_collections.append(name)
            return True
        except Exception:
            return False

    def delete_collection(self, name):
        """Delete a KV Store collection."""
        try:
            self.client.delete(
                f"/servicesNS/nobody/{self.app}/storage/collections/config/{name}",
                operation="delete collection",
            )
            if name in self._created_collections:
                self._created_collections.remove(name)
            return True
        except Exception:
            return False

    def insert_record(self, collection, record):
        """Insert a record into a collection."""
        import json

        url = f"{self.client.base_url.replace('/services', '')}/servicesNS/nobody/{self.app}/storage/collections/data/{collection}"
        response = self.client.session.post(
            url,
            data=json.dumps(record),
            headers={"Content-Type": "application/json"},
            verify=self.client.verify_ssl,
        )
        response.raise_for_status()
        return response.json().get("_key")

    def get_records(self, collection):
        """Get all records from a collection."""
        response = self.client.get(
            f"/servicesNS/nobody/{self.app}/storage/collections/data/{collection}",
            operation="get records",
        )
        return response if isinstance(response, list) else []

    def cleanup(self):
        """Clean up all created collections."""
        for name in self._created_collections[:]:
            try:
                self.delete_collection(name)
            except Exception:
                pass


@pytest.fixture(scope="session")
def kvstore_helper(splunk_client):
    """Fixture providing KV Store helper."""
    helper = KVStoreHelper(splunk_client)
    yield helper
    helper.cleanup()


@pytest.fixture
def test_collection_name():
    """Generate a unique test collection name."""
    return f"test_collection_{uuid.uuid4().hex[:8]}"
