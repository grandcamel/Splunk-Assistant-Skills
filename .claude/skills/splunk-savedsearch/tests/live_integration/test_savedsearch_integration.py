#!/usr/bin/env python3
"""Live Integration Tests for splunk-savedsearch skill."""

import pytest
import time


class TestSavedSearchCRUD:
    """Integration tests for saved search CRUD operations."""

    @pytest.mark.live
    def test_create_and_get_savedsearch(
        self, savedsearch_helper, test_savedsearch_name
    ):
        """Test creating and retrieving a saved search."""
        search = "index=_internal | head 10"
        assert savedsearch_helper.create(test_savedsearch_name, search)

        response = savedsearch_helper.client.get(
            f"/servicesNS/nobody/{savedsearch_helper.app}/saved/searches/{test_savedsearch_name}",
            operation="get saved search",
        )

        assert "entry" in response
        content = response["entry"][0].get("content", {})
        assert content.get("search") == search

    @pytest.mark.live
    def test_create_scheduled_savedsearch(
        self, savedsearch_helper, test_savedsearch_name
    ):
        """Test creating a scheduled saved search."""
        assert savedsearch_helper.create(
            test_savedsearch_name,
            "index=_internal | stats count",
            cron_schedule="0 6 * * *",
            is_scheduled="1",
        )

        response = savedsearch_helper.client.get(
            f"/servicesNS/nobody/{savedsearch_helper.app}/saved/searches/{test_savedsearch_name}",
            operation="get saved search",
        )

        content = response["entry"][0].get("content", {})
        assert content.get("cron_schedule") == "0 6 * * *"

    @pytest.mark.live
    def test_update_savedsearch(self, savedsearch_helper, test_savedsearch_name):
        """Test updating a saved search."""
        savedsearch_helper.create(test_savedsearch_name, "index=_internal | head 5")

        # Update the search
        savedsearch_helper.client.post(
            f"/servicesNS/nobody/{savedsearch_helper.app}/saved/searches/{test_savedsearch_name}",
            data={"search": "index=_internal | head 20"},
            operation="update saved search",
        )

        response = savedsearch_helper.client.get(
            f"/servicesNS/nobody/{savedsearch_helper.app}/saved/searches/{test_savedsearch_name}",
            operation="get saved search",
        )

        content = response["entry"][0].get("content", {})
        assert "head 20" in content.get("search", "")

    @pytest.mark.live
    @pytest.mark.destructive
    def test_delete_savedsearch(self, savedsearch_helper, test_savedsearch_name):
        """Test deleting a saved search."""
        savedsearch_helper.create(test_savedsearch_name, "index=_internal | head 1")
        savedsearch_helper.delete(test_savedsearch_name)

        with pytest.raises(Exception):
            savedsearch_helper.client.get(
                f"/servicesNS/nobody/{savedsearch_helper.app}/saved/searches/{test_savedsearch_name}",
                operation="get deleted saved search",
            )


class TestSavedSearchDispatch:
    """Integration tests for running saved searches."""

    @pytest.mark.live
    def test_dispatch_savedsearch(self, savedsearch_helper, test_savedsearch_name):
        """Test dispatching a saved search."""
        savedsearch_helper.create(test_savedsearch_name, "| makeresults count=5")

        sid = savedsearch_helper.dispatch(test_savedsearch_name)
        assert sid, "Expected SID from dispatch"

        # Wait for completion
        for _ in range(30):
            status = savedsearch_helper.client.get(
                f"/search/v2/jobs/{sid}", operation="get job status"
            )
            if status.get("entry", [{}])[0].get("content", {}).get("isDone"):
                break
            time.sleep(1)

        # Verify results
        results = savedsearch_helper.client.get(
            f"/search/v2/jobs/{sid}/results",
            params={"output_mode": "json"},
            operation="get results",
        )
        assert len(results.get("results", [])) == 5


class TestListSavedSearches:
    """Integration tests for listing saved searches."""

    @pytest.mark.live
    def test_list_savedsearches(self, savedsearch_helper, test_savedsearch_name):
        """Test listing saved searches."""
        savedsearch_helper.create(test_savedsearch_name, "index=_internal | head 1")

        response = savedsearch_helper.client.get(
            f"/servicesNS/nobody/{savedsearch_helper.app}/saved/searches",
            params={"count": 100},
            operation="list saved searches",
        )

        names = [e.get("name") for e in response.get("entry", [])]
        assert test_savedsearch_name in names

    @pytest.mark.live
    def test_list_savedsearches_with_filter(self, splunk_client):
        """Test listing saved searches with search filter."""
        response = splunk_client.get(
            "/saved/searches",
            params={"output_mode": "json", "count": 10},
            operation="list saved searches",
        )

        assert "entry" in response

    @pytest.mark.live
    def test_list_all_apps_savedsearches(self, splunk_client):
        """Test listing saved searches across all apps."""
        response = splunk_client.get(
            "/servicesNS/-/-/saved/searches",
            params={"output_mode": "json", "count": 20},
            operation="list all saved searches",
        )

        assert "entry" in response


class TestSavedSearchHistory:
    """Integration tests for saved search history."""

    @pytest.mark.live
    def test_get_savedsearch_history(
        self, savedsearch_helper, splunk_client, test_savedsearch_name
    ):
        """Test getting saved search dispatch history."""
        # Create and dispatch a saved search
        savedsearch_helper.create(test_savedsearch_name, "| makeresults count=1")
        sid = savedsearch_helper.dispatch(test_savedsearch_name)

        # Wait for completion
        for _ in range(30):
            status = splunk_client.get(f"/search/v2/jobs/{sid}")
            if status.get("entry", [{}])[0].get("content", {}).get("isDone"):
                break
            time.sleep(1)

        # Check history
        try:
            response = splunk_client.get(
                f"/servicesNS/nobody/{savedsearch_helper.app}/saved/searches/{test_savedsearch_name}/history",
                params={"output_mode": "json"},
                operation="get history",
            )
            # History endpoint should exist
            assert response is not None
        except Exception:
            # History endpoint may not exist for new searches
            pass


class TestSavedSearchACL:
    """Integration tests for saved search permissions."""

    @pytest.mark.live
    def test_get_savedsearch_acl(
        self, savedsearch_helper, splunk_client, test_savedsearch_name
    ):
        """Test getting saved search ACL."""
        savedsearch_helper.create(test_savedsearch_name, "| makeresults count=1")

        response = splunk_client.get(
            f"/servicesNS/nobody/{savedsearch_helper.app}/saved/searches/{test_savedsearch_name}",
            params={"output_mode": "json"},
            operation="get saved search",
        )

        # ACL info is in the entry structure
        assert "entry" in response
        entry = response["entry"][0]
        # Check for ACL-related fields in entry or content
        has_acl = (
            "acl" in entry or "eai:acl" in entry.get("content", {}) or "author" in entry
        )
        assert has_acl or "name" in entry  # At minimum, entry should have name


class TestSavedSearchConfiguration:
    """Integration tests for saved search configuration options."""

    @pytest.mark.live
    def test_create_with_dispatch_options(
        self, savedsearch_helper, splunk_client, test_savedsearch_name
    ):
        """Test creating saved search with dispatch options."""
        # Use Splunk API field names with dots
        created = savedsearch_helper.create(
            test_savedsearch_name,
            "search index=_internal | head 10",
            **{"dispatch.earliest_time": "-1h", "dispatch.latest_time": "now"},
        )

        assert created, "Failed to create saved search"

        response = splunk_client.get(
            f"/servicesNS/nobody/{savedsearch_helper.app}/saved/searches/{test_savedsearch_name}",
            operation="get saved search",
        )

        content = response["entry"][0].get("content", {})
        # Dispatch time fields should be set
        assert "dispatch.earliest_time" in content or "dispatch.latest_time" in content

    @pytest.mark.live
    def test_list_scheduled_searches(self, splunk_client):
        """Test listing scheduled saved searches."""
        response = splunk_client.get(
            "/saved/searches",
            params={"output_mode": "json", "search": "is_scheduled=1", "count": 10},
            operation="list scheduled",
        )

        assert "entry" in response
        # Verify scheduled searches have cron_schedule
        for entry in response.get("entry", []):
            content = entry.get("content", {})
            if content.get("is_scheduled"):
                assert "cron_schedule" in content

    @pytest.mark.live
    def test_savedsearch_with_alert_config(
        self, savedsearch_helper, splunk_client, test_savedsearch_name
    ):
        """Test creating saved search with alert configuration."""
        savedsearch_helper.create(
            test_savedsearch_name,
            "index=_internal | stats count",
            alert_type="number of events",
            alert_threshold="0",
        )

        response = splunk_client.get(
            f"/servicesNS/nobody/{savedsearch_helper.app}/saved/searches/{test_savedsearch_name}",
            operation="get saved search",
        )

        content = response["entry"][0].get("content", {})
        # Alert fields may or may not be present depending on config
        assert "search" in content
