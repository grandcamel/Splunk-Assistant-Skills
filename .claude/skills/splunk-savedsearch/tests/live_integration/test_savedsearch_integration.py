#!/usr/bin/env python3
"""Live Integration Tests for splunk-savedsearch skill."""

import pytest
import time


class TestSavedSearchCRUD:
    """Integration tests for saved search CRUD operations."""

    @pytest.mark.live
    def test_create_and_get_savedsearch(self, savedsearch_helper, test_savedsearch_name):
        """Test creating and retrieving a saved search."""
        search = "index=_internal | head 10"
        assert savedsearch_helper.create(test_savedsearch_name, search)

        response = savedsearch_helper.client.get(
            f"/servicesNS/nobody/{savedsearch_helper.app}/saved/searches/{test_savedsearch_name}",
            operation="get saved search"
        )

        assert "entry" in response
        content = response["entry"][0].get("content", {})
        assert content.get("search") == search

    @pytest.mark.live
    def test_create_scheduled_savedsearch(self, savedsearch_helper, test_savedsearch_name):
        """Test creating a scheduled saved search."""
        assert savedsearch_helper.create(
            test_savedsearch_name,
            "index=_internal | stats count",
            cron_schedule="0 6 * * *",
            is_scheduled="1"
        )

        response = savedsearch_helper.client.get(
            f"/servicesNS/nobody/{savedsearch_helper.app}/saved/searches/{test_savedsearch_name}",
            operation="get saved search"
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
            operation="update saved search"
        )

        response = savedsearch_helper.client.get(
            f"/servicesNS/nobody/{savedsearch_helper.app}/saved/searches/{test_savedsearch_name}",
            operation="get saved search"
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
                operation="get deleted saved search"
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
                f"/search/v2/jobs/{sid}",
                operation="get job status"
            )
            if status.get("entry", [{}])[0].get("content", {}).get("isDone"):
                break
            time.sleep(1)

        # Verify results
        results = savedsearch_helper.client.get(
            f"/search/v2/jobs/{sid}/results",
            params={"output_mode": "json"},
            operation="get results"
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
            operation="list saved searches"
        )

        names = [e.get("name") for e in response.get("entry", [])]
        assert test_savedsearch_name in names
