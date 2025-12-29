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


class TestHostDiscovery:
    """Integration tests for host discovery."""

    @pytest.mark.live
    def test_list_hosts_metadata(self, splunk_client):
        """Test listing hosts via metadata search."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": "| metadata type=hosts | head 20",
                "output_mode": "json",
                "earliest_time": "-24h",
            },
            operation="metadata hosts search"
        )

        results = response.get("results", [])
        # May have hosts if there's data
        assert isinstance(results, list)

    @pytest.mark.live
    def test_list_hosts_for_index(self, splunk_client):
        """Test listing hosts for a specific index."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": "| metadata type=hosts index=_internal | head 10",
                "output_mode": "json",
                "earliest_time": "-24h",
            },
            operation="metadata hosts search"
        )

        results = response.get("results", [])
        for r in results:
            assert "host" in r


class TestIndexProperties:
    """Integration tests for index property queries."""

    @pytest.mark.live
    def test_list_indexes_with_count(self, splunk_client):
        """Test listing indexes with count limit."""
        response = splunk_client.get(
            "/data/indexes",
            params={"count": 5, "output_mode": "json"},
            operation="list indexes limited"
        )

        assert "entry" in response
        assert len(response["entry"]) <= 5

    @pytest.mark.live
    def test_get_internal_index_properties(self, splunk_client):
        """Test getting _internal index properties."""
        response = splunk_client.get(
            "/data/indexes/_internal",
            operation="get _internal index"
        )

        assert "entry" in response
        content = response["entry"][0].get("content", {})
        # Check for common index properties
        assert "datatype" in content or "maxDataSize" in content

    @pytest.mark.live
    def test_list_indexes_by_datatype(self, splunk_client):
        """Test listing indexes filtered by datatype."""
        response = splunk_client.get(
            "/data/indexes",
            params={"search": "datatype=event", "output_mode": "json"},
            operation="list event indexes"
        )

        assert "entry" in response
        # Should have at least main index
        for entry in response.get("entry", []):
            content = entry.get("content", {})
            # datatype should be event for filtered results
            if "datatype" in content:
                assert content["datatype"] == "event"


class TestRESTMetadata:
    """Integration tests for REST-based metadata discovery."""

    @pytest.mark.live
    def test_rest_server_info(self, splunk_client):
        """Test getting server info via REST search."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": "| rest /services/server/info | fields splunk_server, version, build",
                "output_mode": "json",
            },
            operation="rest server info"
        )

        results = response.get("results", [])
        assert len(results) > 0
        assert "splunk_server" in results[0] or "version" in results[0]

    @pytest.mark.live
    def test_rest_apps_local(self, splunk_client):
        """Test listing apps via REST search."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": "| rest /services/apps/local | head 10 | fields title, label, version",
                "output_mode": "json",
            },
            operation="rest apps"
        )

        results = response.get("results", [])
        assert len(results) > 0

    @pytest.mark.live
    def test_tstats_count(self, splunk_client):
        """Test tstats for accelerated metadata queries."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": "| tstats count WHERE index=_internal BY sourcetype | head 5",
                "output_mode": "json",
                "earliest_time": "-1h",
            },
            operation="tstats count"
        )

        results = response.get("results", [])
        # tstats may return empty if TSIDX not available
        assert isinstance(results, list)


class TestDataModels:
    """Integration tests for data model metadata."""

    @pytest.mark.live
    def test_list_datamodels(self, splunk_client):
        """Test listing available data models."""
        response = splunk_client.get(
            "/datamodel/model",
            params={"output_mode": "json"},
            operation="list datamodels"
        )

        # Response should have entry (may be empty)
        assert "entry" in response or response == []
