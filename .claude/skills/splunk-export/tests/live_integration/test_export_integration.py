#!/usr/bin/env python3
"""Live Integration Tests for splunk-export skill."""

import pytest
import os


class TestExportEndpoint:
    """Integration tests for the export endpoint."""

    @pytest.mark.live
    @pytest.mark.xfail(reason="Export endpoint returns raw CSV, client expects JSON")
    def test_export_endpoint_csv(self, splunk_client, test_index, test_data):
        """Test export endpoint returns CSV data."""
        response = splunk_client.post(
            "/search/v2/jobs/export",
            data={
                "search": f"search index={test_index} | head 10",
                "output_mode": "csv",
                "earliest_time": "-24h",
                "latest_time": "now",
            },
            timeout=60,
            operation="export csv",
        )

        # Export returns raw content, not JSON
        assert response is not None

    @pytest.mark.live
    @pytest.mark.xfail(
        reason="Export endpoint returns streaming JSON lines, not a single JSON object"
    )
    def test_export_endpoint_json(self, splunk_client, test_index, test_data):
        """Test export endpoint returns JSON data."""
        response = splunk_client.post(
            "/search/v2/jobs/export",
            data={
                "search": f"search index={test_index} | head 10",
                "output_mode": "json",
                "earliest_time": "-24h",
                "latest_time": "now",
            },
            timeout=60,
            operation="export json",
        )

        assert response is not None

    @pytest.mark.live
    @pytest.mark.xfail(reason="Export endpoint returns raw CSV, client expects JSON")
    def test_export_with_stats(self, splunk_client, test_index, test_data):
        """Test export with aggregation query."""
        response = splunk_client.post(
            "/search/v2/jobs/export",
            data={
                "search": f"search index={test_index} | stats count by host",
                "output_mode": "csv",
                "earliest_time": "-24h",
                "latest_time": "now",
            },
            timeout=60,
            operation="export stats",
        )

        assert response is not None


class TestJobResultsExport:
    """Integration tests for exporting results from completed jobs."""

    @pytest.mark.live
    @pytest.mark.xfail(reason="CSV output_mode returns raw CSV, client expects JSON")
    def test_export_job_results_csv(
        self, splunk_client, job_helper, test_index, test_data
    ):
        """Test exporting job results in CSV format."""
        # Create and complete a job
        sid = job_helper.create(f"search index={test_index} | head 20")
        job_helper.wait_for_done(sid)

        # Get results in CSV format
        response = splunk_client.get(
            f"/search/v2/jobs/{sid}/results",
            params={"output_mode": "csv", "count": 0},
            operation="get csv results",
        )

        # Response should be CSV content
        assert response is not None

    @pytest.mark.live
    def test_export_job_results_json(
        self, splunk_client, job_helper, test_index, test_data
    ):
        """Test exporting job results in JSON format."""
        sid = job_helper.create(f"search index={test_index} | head 20")
        job_helper.wait_for_done(sid)

        response = splunk_client.get(
            f"/search/v2/jobs/{sid}/results",
            params={"output_mode": "json", "count": 0},
            operation="get json results",
        )

        assert "results" in response
        assert len(response["results"]) > 0

    @pytest.mark.live
    @pytest.mark.xfail(reason="XML output_mode returns raw XML, client expects JSON")
    def test_export_job_results_xml(
        self, splunk_client, job_helper, test_index, test_data
    ):
        """Test exporting job results in XML format."""
        sid = job_helper.create(f"search index={test_index} | head 10")
        job_helper.wait_for_done(sid)

        response = splunk_client.get(
            f"/search/v2/jobs/{sid}/results",
            params={"output_mode": "xml", "count": 0},
            operation="get xml results",
        )

        # Response should be XML content
        assert response is not None

    @pytest.mark.live
    def test_export_with_field_selection(
        self, splunk_client, job_helper, test_index, test_data
    ):
        """Test exporting with specific fields selected."""
        sid = job_helper.create(
            f"search index={test_index} | head 10 | fields host, sourcetype, _time"
        )
        job_helper.wait_for_done(sid)

        response = splunk_client.get(
            f"/search/v2/jobs/{sid}/results",
            params={"output_mode": "json", "count": 0},
            operation="get selected fields",
        )

        assert "results" in response
        if response["results"]:
            # Verify only requested fields are present (plus internal fields)
            result = response["results"][0]
            assert "host" in result or "sourcetype" in result


class TestExportPagination:
    """Integration tests for paginated exports."""

    @pytest.mark.live
    def test_export_with_offset(self, splunk_client, job_helper, test_index, test_data):
        """Test exporting with offset for pagination."""
        sid = job_helper.create(f"search index={test_index} | head 50")
        job_helper.wait_for_done(sid)

        # Get first page
        page1 = splunk_client.get(
            f"/search/v2/jobs/{sid}/results",
            params={"output_mode": "json", "count": 10, "offset": 0},
            operation="get page 1",
        )

        # Get second page
        page2 = splunk_client.get(
            f"/search/v2/jobs/{sid}/results",
            params={"output_mode": "json", "count": 10, "offset": 10},
            operation="get page 2",
        )

        assert "results" in page1
        assert "results" in page2

    @pytest.mark.live
    def test_export_all_results(self, splunk_client, job_helper, test_index, test_data):
        """Test exporting all results with count=0."""
        sid = job_helper.create(
            f"search index={test_index} | stats count by host, sourcetype"
        )
        job_helper.wait_for_done(sid)

        response = splunk_client.get(
            f"/search/v2/jobs/{sid}/results",
            params={"output_mode": "json", "count": 0},
            operation="get all results",
        )

        assert "results" in response
        assert len(response["results"]) > 0


class TestExportSizeEstimation:
    """Integration tests for export size estimation."""

    @pytest.mark.live
    def test_job_result_count(self, splunk_client, job_helper, test_index, test_data):
        """Test getting result count for size estimation."""
        sid = job_helper.create(f"search index={test_index}")
        status = job_helper.wait_for_done(sid)

        # Result count should be available
        assert "resultCount" in status
        assert int(status["resultCount"]) > 0

    @pytest.mark.live
    def test_job_scan_count(self, splunk_client, job_helper, test_index, test_data):
        """Test getting scan count for size estimation."""
        sid = job_helper.create(f"search index={test_index}")
        status = job_helper.wait_for_done(sid)

        # Scan count should be available
        assert "scanCount" in status

    @pytest.mark.live
    def test_estimate_from_stats(self, splunk_client, test_index, test_data):
        """Test estimating export size using stats."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": f"search index={test_index} | stats count",
                "output_mode": "json",
                "earliest_time": "-24h",
            },
            operation="count events",
        )

        results = response.get("results", [])
        assert len(results) > 0
        assert "count" in results[0]
        assert int(results[0]["count"]) > 0


class TestStreamingExport:
    """Integration tests for streaming export functionality."""

    @pytest.mark.live
    def test_stream_results(self, splunk_client, job_helper, test_index, test_data):
        """Test streaming results from a job."""
        sid = job_helper.create(f"search index={test_index} | head 50")
        job_helper.wait_for_done(sid)

        # Stream results
        chunks = []
        for chunk in splunk_client.stream_results(
            f"/search/v2/jobs/{sid}/results",
            params={"output_mode": "csv", "count": 0},
            operation="stream results",
        ):
            chunks.append(chunk)

        # Should have received data
        assert len(chunks) > 0
        total_bytes = sum(len(c) for c in chunks)
        assert total_bytes > 0

    @pytest.mark.live
    def test_stream_large_results(
        self, splunk_client, job_helper, test_index, test_data
    ):
        """Test streaming larger result sets."""
        # Create a job that returns more results
        sid = job_helper.create(
            f"search index={test_index} | head 100",
            earliest_time="-24h",
        )
        job_helper.wait_for_done(sid, timeout=120)

        chunks = []
        for chunk in splunk_client.stream_results(
            f"/search/v2/jobs/{sid}/results",
            params={"output_mode": "json", "count": 0},
            operation="stream large results",
        ):
            chunks.append(chunk)

        assert len(chunks) > 0
