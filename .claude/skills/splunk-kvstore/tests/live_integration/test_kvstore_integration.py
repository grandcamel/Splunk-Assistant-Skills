#!/usr/bin/env python3
"""
Live Integration Tests for splunk-kvstore skill.

Tests KV Store collection and record operations against a real Splunk instance.
"""

import pytest
import uuid


class TestKVStoreCollections:
    """Integration tests for KV Store collection operations."""

    @pytest.mark.live
    def test_create_and_list_collection(self, kvstore_helper, test_collection_name):
        """Test creating a collection and listing it."""
        # Create collection
        assert kvstore_helper.create_collection(test_collection_name)

        # List collections and verify it exists
        response = kvstore_helper.client.get(
            f"/servicesNS/nobody/{kvstore_helper.app}/storage/collections/config",
            operation="list collections"
        )

        collection_names = [e.get("name") for e in response.get("entry", [])]
        assert test_collection_name in collection_names

    @pytest.mark.live
    def test_create_collection_with_fields(self, kvstore_helper, test_collection_name):
        """Test creating a collection with field definitions."""
        fields = {
            "username": "string",
            "count": "number",
            "active": "bool"
        }

        assert kvstore_helper.create_collection(test_collection_name, fields)

        # Verify collection exists
        response = kvstore_helper.client.get(
            f"/servicesNS/nobody/{kvstore_helper.app}/storage/collections/config/{test_collection_name}",
            operation="get collection"
        )

        assert "entry" in response
        content = response["entry"][0].get("content", {})
        assert content.get("field.username") == "string"

    @pytest.mark.live
    @pytest.mark.destructive
    def test_delete_collection(self, kvstore_helper, test_collection_name):
        """Test deleting a collection."""
        # Create and then delete
        kvstore_helper.create_collection(test_collection_name)
        kvstore_helper.delete_collection(test_collection_name)

        # Verify it's gone
        with pytest.raises(Exception):
            kvstore_helper.client.get(
                f"/servicesNS/nobody/{kvstore_helper.app}/storage/collections/config/{test_collection_name}",
                operation="get deleted collection"
            )


class TestKVStoreRecords:
    """Integration tests for KV Store record operations."""

    @pytest.mark.live
    def test_insert_and_get_record(self, kvstore_helper, test_collection_name):
        """Test inserting and retrieving a record."""
        kvstore_helper.create_collection(test_collection_name)

        # Insert record
        record = {"username": "testuser", "email": "test@example.com"}
        key = kvstore_helper.insert_record(test_collection_name, record)

        assert key, "Expected _key in response"

        # Get the record
        response = kvstore_helper.client.get(
            f"/servicesNS/nobody/{kvstore_helper.app}/storage/collections/data/{test_collection_name}/{key}",
            operation="get record"
        )

        assert response.get("username") == "testuser"
        assert response.get("email") == "test@example.com"

    @pytest.mark.live
    def test_query_records(self, kvstore_helper, test_collection_name):
        """Test querying records from a collection."""
        kvstore_helper.create_collection(test_collection_name)

        # Insert multiple records
        for i in range(5):
            kvstore_helper.insert_record(test_collection_name, {
                "index": i,
                "name": f"record_{i}"
            })

        # Query all records
        records = kvstore_helper.get_records(test_collection_name)
        assert len(records) == 5

    @pytest.mark.live
    def test_update_record(self, kvstore_helper, test_collection_name):
        """Test updating a record."""
        import json as json_lib
        kvstore_helper.create_collection(test_collection_name)

        # Insert record
        key = kvstore_helper.insert_record(test_collection_name, {"value": "original"})

        # Update record
        url = f"{kvstore_helper.client.base_url.replace('/services', '')}/servicesNS/nobody/{kvstore_helper.app}/storage/collections/data/{test_collection_name}/{key}"
        kvstore_helper.client.session.post(
            url,
            data=json_lib.dumps({"value": "updated"}),
            headers={"Content-Type": "application/json"},
            verify=kvstore_helper.client.verify_ssl
        )

        # Verify update
        response = kvstore_helper.client.get(
            f"/servicesNS/nobody/{kvstore_helper.app}/storage/collections/data/{test_collection_name}/{key}",
            operation="get record"
        )
        assert response.get("value") == "updated"

    @pytest.mark.live
    @pytest.mark.destructive
    def test_delete_record(self, kvstore_helper, test_collection_name):
        """Test deleting a record."""
        kvstore_helper.create_collection(test_collection_name)

        # Insert and delete
        key = kvstore_helper.insert_record(test_collection_name, {"temp": "data"})

        # Use session directly as KV store delete returns empty response
        url = f"{kvstore_helper.client.base_url.replace('/services', '')}/servicesNS/nobody/{kvstore_helper.app}/storage/collections/data/{test_collection_name}/{key}"
        response = kvstore_helper.client.session.delete(
            url,
            verify=kvstore_helper.client.verify_ssl
        )
        response.raise_for_status()

        # Verify deletion
        records = kvstore_helper.get_records(test_collection_name)
        assert len(records) == 0


class TestKVStoreQueryFilters:
    """Integration tests for KV Store query filtering."""

    @pytest.mark.live
    def test_query_with_filter(self, kvstore_helper, test_collection_name):
        """Test querying with a filter."""
        kvstore_helper.create_collection(test_collection_name)

        # Insert records with different statuses
        for status in ["active", "active", "inactive"]:
            kvstore_helper.insert_record(test_collection_name, {"status": status})

        # Query with filter
        response = kvstore_helper.client.get(
            f"/servicesNS/nobody/{kvstore_helper.app}/storage/collections/data/{test_collection_name}",
            params={"query": '{"status": "active"}'},
            operation="filtered query"
        )

        records = response if isinstance(response, list) else []
        assert len(records) == 2

    @pytest.mark.live
    def test_query_with_limit(self, kvstore_helper, test_collection_name):
        """Test querying with a limit."""
        kvstore_helper.create_collection(test_collection_name)

        # Insert 10 records
        for i in range(10):
            kvstore_helper.insert_record(test_collection_name, {"index": i})

        # Query with limit
        response = kvstore_helper.client.get(
            f"/servicesNS/nobody/{kvstore_helper.app}/storage/collections/data/{test_collection_name}",
            params={"limit": 5},
            operation="limited query"
        )

        records = response if isinstance(response, list) else []
        assert len(records) == 5
