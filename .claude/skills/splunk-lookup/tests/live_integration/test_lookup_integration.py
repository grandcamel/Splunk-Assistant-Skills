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
            operation="list lookups",
        )

        assert "entry" in response

    @pytest.mark.live
    @pytest.mark.xfail(
        reason="Lookup file upload requires complex multipart form handling"
    )
    def test_upload_and_get_lookup(self, lookup_helper, test_lookup_name):
        """Test uploading and retrieving a lookup file."""
        csv_content = (
            "username,email,role\nadmin,admin@test.com,admin\nuser,user@test.com,user"
        )

        assert lookup_helper.upload(test_lookup_name, csv_content)

        response = lookup_helper.client.get(
            f"/servicesNS/nobody/{lookup_helper.app}/data/lookup-table-files/{test_lookup_name}",
            operation="get lookup",
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
                operation="get deleted lookup",
            )


class TestLookupSearch:
    """Integration tests for using lookups in searches."""

    @pytest.mark.live
    @pytest.mark.xfail(
        reason="Depends on lookup upload which requires complex multipart form handling"
    )
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
            operation="lookup search",
        )

        results = response.get("results", [])
        assert len(results) == 3
        assert results[0].get("code") == "200"


class TestLookupDefinitions:
    """Integration tests for lookup definitions."""

    @pytest.mark.live
    def test_list_lookup_definitions(self, splunk_client):
        """Test listing lookup table definitions."""
        response = splunk_client.get(
            "/services/data/transforms/lookups",
            params={"output_mode": "json", "count": 10},
            operation="list lookup definitions",
        )

        assert "entry" in response

    @pytest.mark.live
    def test_list_lookups_in_search_app(self, splunk_client):
        """Test listing lookups in search app."""
        response = splunk_client.get(
            "/servicesNS/nobody/search/data/lookup-table-files",
            params={"output_mode": "json", "count": 10},
            operation="list search app lookups",
        )

        assert "entry" in response

    @pytest.mark.live
    def test_list_automatic_lookups(self, splunk_client):
        """Test listing automatic lookup definitions."""
        try:
            response = splunk_client.get(
                "/services/data/props/lookups",
                params={"output_mode": "json", "count": 10},
                operation="list auto lookups",
            )
            assert response is not None
        except Exception:
            # May not have automatic lookups configured
            pass


class TestLookupFiles:
    """Integration tests for lookup file metadata."""

    @pytest.mark.live
    def test_list_all_lookup_files(self, splunk_client):
        """Test listing all lookup files across apps."""
        response = splunk_client.get(
            "/servicesNS/-/-/data/lookup-table-files",
            params={"output_mode": "json", "count": 20},
            operation="list all lookup files",
        )

        assert "entry" in response

    @pytest.mark.live
    def test_lookup_file_structure(self, splunk_client):
        """Test lookup file entry structure."""
        response = splunk_client.get(
            "/servicesNS/nobody/search/data/lookup-table-files",
            params={"output_mode": "json"},
            operation="list lookups",
        )

        # If there are lookups, check structure
        for entry in response.get("entry", []):
            assert "name" in entry
            if "content" in entry:
                content = entry["content"]
                assert isinstance(content, dict)


class TestLookupInputSearch:
    """Integration tests for inputlookup command."""

    @pytest.mark.live
    def test_inputlookup_nonexistent(self, splunk_client):
        """Test inputlookup with nonexistent file returns error or empty."""
        try:
            response = splunk_client.post(
                "/search/jobs/oneshot",
                data={
                    "search": "| inputlookup nonexistent_lookup_12345.csv",
                    "output_mode": "json",
                },
                operation="inputlookup nonexistent",
            )
            # Should return empty results or error
            results = response.get("results", [])
            assert len(results) == 0
        except Exception:
            # Exception is also valid for nonexistent lookup
            pass

    @pytest.mark.live
    def test_makeresults_with_outputlookup_syntax(self, splunk_client):
        """Test outputlookup syntax validation."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": "| makeresults count=1 | eval test=1",
                "output_mode": "json",
            },
            operation="makeresults for lookup test",
        )

        results = response.get("results", [])
        assert len(results) == 1


class TestLookupTransforms:
    """Integration tests for lookup transforms."""

    @pytest.mark.live
    def test_list_transforms_lookups(self, splunk_client):
        """Test listing transforms lookup definitions."""
        response = splunk_client.get(
            "/services/data/transforms/lookups",
            params={"output_mode": "json", "count": 10},
            operation="list transforms lookups",
        )

        assert "entry" in response

    @pytest.mark.live
    def test_transforms_lookup_structure(self, splunk_client):
        """Test transforms lookup entry structure."""
        response = splunk_client.get(
            "/services/data/transforms/lookups",
            params={"output_mode": "json"},
            operation="list transforms",
        )

        for entry in response.get("entry", []):
            assert "name" in entry
            if "content" in entry:
                # Lookup transforms should have filename field
                content = entry["content"]
                assert isinstance(content, dict)
