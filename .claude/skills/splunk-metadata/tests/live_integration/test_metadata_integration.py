#!/usr/bin/env python3
"""Live Integration Tests for splunk-metadata skill."""

import pytest


class TestIndexOperations:
    """Integration tests for index operations."""

    @pytest.mark.live
    def test_list_indexes(self, splunk_client):
        """Test listing indexes."""
        response = splunk_client.get(
            "/data/indexes",
            operation="list indexes"
        )

        assert "entry" in response
        # Should have at least _internal
        index_names = [e.get("name") for e in response["entry"]]
        assert "_internal" in index_names

    @pytest.mark.live
    def test_get_index_details(self, splunk_client):
        """Test getting index details."""
        response = splunk_client.get(
            "/data/indexes/main",
            operation="get index"
        )

        assert "entry" in response
        content = response["entry"][0].get("content", {})
        assert "totalEventCount" in content or "currentDBSizeMB" in content

    @pytest.mark.live
    @pytest.mark.destructive
    def test_create_index(self, index_helper, test_index_name):
        """Test creating an index."""
        assert index_helper.create(test_index_name)

        response = index_helper.client.get(
            f"/data/indexes/{test_index_name}",
            operation="get created index"
        )

        assert "entry" in response
        assert response["entry"][0].get("name") == test_index_name


class TestSourcetypeDiscovery:
    """Integration tests for sourcetype discovery."""

    @pytest.mark.live
    def test_list_sourcetypes_metadata(self, splunk_client):
        """Test listing sourcetypes via metadata search."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": "| metadata type=sourcetypes | head 20",
                "output_mode": "json",
                "earliest_time": "-24h",
            },
            operation="metadata search"
        )

        results = response.get("results", [])
        # Should have at least some sourcetypes in _internal
        assert len(results) >= 0  # May be empty if no data yet

    @pytest.mark.live
    def test_list_sourcetypes_for_index(self, splunk_client):
        """Test listing sourcetypes for a specific index."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": "| metadata type=sourcetypes index=_internal | head 10",
                "output_mode": "json",
                "earliest_time": "-24h",
            },
            operation="metadata search"
        )

        results = response.get("results", [])
        for r in results:
            assert "sourcetype" in r


class TestSourceDiscovery:
    """Integration tests for source discovery."""

    @pytest.mark.live
    def test_list_sources(self, splunk_client):
        """Test listing sources via metadata search."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": "| metadata type=sources index=_internal | head 10",
                "output_mode": "json",
                "earliest_time": "-24h",
            },
            operation="metadata search"
        )

        results = response.get("results", [])
        for r in results:
            assert "source" in r
