#!/usr/bin/env python3
"""Live Integration Tests for splunk-lookup skill."""

import pytest


class TestLookupOperations:
    """Integration tests for lookup file operations."""

    @pytest.mark.live
    def test_list_lookups(self, splunk_client):
        """Test listing lookup files."""
        response = splunk_client.get(
            "/servicesNS/nobody/search/data/lookup-table-files",
            operation="list lookups"
        )

        assert "entry" in response

    @pytest.mark.live
    @pytest.mark.xfail(reason="Lookup file upload requires complex multipart form handling")
    def test_upload_and_get_lookup(self, lookup_helper, test_lookup_name):
        """Test uploading and retrieving a lookup file."""
        csv_content = "username,email,role\nadmin,admin@test.com,admin\nuser,user@test.com,user"

        assert lookup_helper.upload(test_lookup_name, csv_content)

        response = lookup_helper.client.get(
            f"/servicesNS/nobody/{lookup_helper.app}/data/lookup-table-files/{test_lookup_name}",
            operation="get lookup"
        )

        assert "entry" in response
        assert response["entry"][0].get("name") == test_lookup_name

    @pytest.mark.live
    @pytest.mark.destructive
    def test_delete_lookup(self, lookup_helper, test_lookup_name):
        """Test deleting a lookup file."""
        csv_content = "col1,col2\nval1,val2"
        lookup_helper.upload(test_lookup_name, csv_content)

        lookup_helper.delete(test_lookup_name)

        with pytest.raises(Exception):
            lookup_helper.client.get(
                f"/servicesNS/nobody/{lookup_helper.app}/data/lookup-table-files/{test_lookup_name}",
                operation="get deleted lookup"
            )


class TestLookupSearch:
    """Integration tests for using lookups in searches."""

    @pytest.mark.live
    @pytest.mark.xfail(reason="Depends on lookup upload which requires complex multipart form handling")
    def test_lookup_in_search(self, lookup_helper, splunk_client, test_lookup_name):
        """Test using a lookup in a search."""
        csv_content = "code,description\n200,OK\n404,Not Found\n500,Server Error"
        lookup_helper.upload(test_lookup_name, csv_content)

        # Search using the lookup
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": f"| inputlookup {test_lookup_name}",
                "output_mode": "json",
            },
            operation="lookup search"
        )

        results = response.get("results", [])
        assert len(results) == 3
        assert results[0].get("code") == "200"
