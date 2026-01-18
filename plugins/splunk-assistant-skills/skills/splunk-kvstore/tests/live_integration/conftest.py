#!/usr/bin/env python3
"""
Pytest configuration for splunk-kvstore live integration tests.

Shared fixtures are automatically loaded from shared/tests/live_integration/fixtures.py
via pytest_plugins. The shared path is configured in pytest.ini's pythonpath.
"""

import json
import uuid

import pytest

# Load all shared fixtures (splunk_connection, splunk_client, test_index, etc.)
pytest_plugins = ["fixtures"]


# =============================================================================
# Skill-Specific Fixtures
# =============================================================================


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
