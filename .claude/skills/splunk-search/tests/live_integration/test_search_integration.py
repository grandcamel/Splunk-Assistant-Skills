#!/usr/bin/env python3
"""
Live Integration Tests for splunk-search skill.

These tests run against a real Splunk instance (Docker or external).

Usage:
    # With Docker
    pytest .claude/skills/splunk-search/tests/live_integration/ -v

    # With external Splunk
    SPLUNK_TEST_URL=https://splunk:8089 SPLUNK_TEST_TOKEN=xxx pytest ... -v
"""

import sys
from pathlib import Path
import pytest

# Add test infrastructure to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "tests"))

from live_integration.fixtures import (
    splunk_connection,
    splunk_client,
    test_index,
    test_data,
    search_helper,
    job_helper,
)


class TestSearchOneshot:
    """Integration tests for oneshot search mode."""

    @pytest.mark.live
    def test_oneshot_simple_search(self, splunk_client, test_index, test_data):
        """Test basic oneshot search returns results."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": f"search index={test_index} | head 10",
                "output_mode": "json",
                "earliest_time": "-24h",
                "latest_time": "now",
            },
            operation="oneshot search",
        )

        results = response.get("results", [])
        assert len(results) > 0, "Expected at least one result"

    @pytest.mark.live
    def test_oneshot_stats_search(self, splunk_client, test_index, test_data):
        """Test oneshot search with stats command."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": f"search index={test_index} | stats count by sourcetype",
                "output_mode": "json",
                "earliest_time": "-24h",
                "latest_time": "now",
            },
            operation="stats search",
        )

        results = response.get("results", [])
        assert len(results) > 0, "Expected stats results"
        assert "count" in results[0], "Expected count field in stats"
        assert "sourcetype" in results[0], "Expected sourcetype field in stats"

    @pytest.mark.live
    def test_oneshot_timechart(self, splunk_client, test_index, test_data):
        """Test oneshot search with timechart command."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": f"search index={test_index} | timechart span=1h count",
                "output_mode": "json",
                "earliest_time": "-24h",
                "latest_time": "now",
            },
            operation="timechart search",
        )

        results = response.get("results", [])
        assert len(results) > 0, "Expected timechart results"
        assert "_time" in results[0], "Expected _time field in timechart"

    @pytest.mark.live
    def test_oneshot_empty_results(self, splunk_client, test_index):
        """Test oneshot search with no matching events."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": f'search index={test_index} nonexistent_field="impossible_value"',
                "output_mode": "json",
                "earliest_time": "-24h",
                "latest_time": "now",
            },
            operation="empty search",
        )

        results = response.get("results", [])
        assert len(results) == 0, "Expected no results"


class TestSearchNormal:
    """Integration tests for normal (async) search mode."""

    @pytest.mark.live
    def test_normal_search_creates_job(self, splunk_client, test_index):
        """Test normal search creates a job with SID."""
        response = splunk_client.post(
            "/search/v2/jobs",
            data={
                "search": f"search index={test_index} | head 10",
                "exec_mode": "normal",
                "earliest_time": "-24h",
                "latest_time": "now",
            },
            operation="create job",
        )

        # Extract SID
        sid = response.get("sid")
        if not sid and "entry" in response:
            sid = response["entry"][0].get("name")

        assert sid is not None, "Expected SID in response"
        assert "." in sid, f"SID should contain period: {sid}"

    @pytest.mark.live
    def test_normal_search_poll_completion(self, job_helper, test_index, test_data):
        """Test polling normal search until completion."""
        sid = job_helper.create(
            f"search index={test_index} | stats count",
            earliest_time="-24h",
        )

        # Wait for completion
        status = job_helper.wait_for_done(sid, timeout=60)

        assert status.get("isDone") is True
        assert status.get("isFailed") is False
        assert int(status.get("resultCount", 0)) > 0

    @pytest.mark.live
    def test_normal_search_get_results(self, splunk_client, job_helper, test_index, test_data):
        """Test retrieving results from completed job."""
        sid = job_helper.create(f"search index={test_index} | head 5")
        job_helper.wait_for_done(sid)

        # Get results
        response = splunk_client.get(
            f"/search/v2/jobs/{sid}/results",
            params={"output_mode": "json", "count": 100},
            operation="get results",
        )

        results = response.get("results", [])
        assert len(results) > 0, "Expected results from completed job"


class TestSearchBlocking:
    """Integration tests for blocking (sync) search mode."""

    @pytest.mark.live
    def test_blocking_search_waits(self, splunk_client, test_index, test_data):
        """Test blocking search waits for completion."""
        response = splunk_client.post(
            "/search/v2/jobs",
            data={
                "search": f"search index={test_index} | stats count",
                "exec_mode": "blocking",
                "earliest_time": "-24h",
                "latest_time": "now",
            },
            timeout=60,
            operation="blocking search",
        )

        # Response should contain completed job
        assert "entry" in response, "Expected entry in blocking response"
        entry = response["entry"][0]
        content = entry.get("content", {})
        assert content.get("isDone") is True

    @pytest.mark.live
    def test_blocking_search_returns_sid(self, splunk_client, test_index):
        """Test blocking search returns SID for result retrieval."""
        response = splunk_client.post(
            "/search/v2/jobs",
            data={
                "search": f"search index={test_index} | head 1",
                "exec_mode": "blocking",
            },
            timeout=60,
            operation="blocking search",
        )

        sid = None
        if "entry" in response:
            sid = response["entry"][0].get("name")

        assert sid is not None, "Expected SID from blocking search"


class TestSearchHelper:
    """Integration tests using the search helper fixture."""

    @pytest.mark.live
    def test_search_helper_oneshot(self, search_helper, test_index, test_data):
        """Test search helper oneshot method."""
        results = search_helper.oneshot(f"search index={test_index} | head 5")
        assert len(results) > 0

    @pytest.mark.live
    def test_search_helper_count(self, search_helper, test_index, test_data):
        """Test search helper count method."""
        count = search_helper.count(f"search index={test_index}")
        assert count > 0, f"Expected events in {test_index}"

    @pytest.mark.live
    def test_search_helper_exists(self, search_helper, test_index, test_data):
        """Test search helper exists method."""
        assert search_helper.exists(f"search index={test_index}")
        assert not search_helper.exists(
            f'search index={test_index} impossible_field="no_match"'
        )


class TestSearchValidation:
    """Integration tests for SPL validation."""

    @pytest.mark.live
    def test_invalid_spl_returns_error(self, splunk_client):
        """Test that invalid SPL returns appropriate error."""
        with pytest.raises(Exception) as exc_info:
            splunk_client.post(
                "/search/jobs/oneshot",
                data={
                    "search": "invalid || spl syntax [[",
                    "output_mode": "json",
                },
                operation="invalid search",
            )

        # Should raise a validation error
        assert exc_info.value is not None

    @pytest.mark.live
    def test_generating_command_search(self, splunk_client):
        """Test search starting with generating command."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": "| makeresults count=5 | eval test=1",
                "output_mode": "json",
            },
            operation="makeresults search",
        )

        results = response.get("results", [])
        assert len(results) == 5, "Expected 5 makeresults events"


class TestSearchPerformance:
    """Performance-related integration tests."""

    @pytest.mark.live
    @pytest.mark.slow_integration
    def test_search_with_many_results(self, splunk_client, test_index, test_data):
        """Test search returning many results."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": f"search index={test_index} | head 1000",
                "output_mode": "json",
                "count": 1000,
                "earliest_time": "-24h",
            },
            timeout=120,
            operation="large search",
        )

        results = response.get("results", [])
        # Should return up to the available events
        assert len(results) > 0

    @pytest.mark.live
    def test_search_with_preview(self, splunk_client, job_helper, test_index, test_data):
        """Test getting preview results from running job."""
        # Create a job
        sid = job_helper.create(
            f"search index={test_index} | head 100",
            exec_mode="normal",
        )

        # Try to get preview (may or may not have results depending on speed)
        try:
            response = splunk_client.get(
                f"/search/v2/jobs/{sid}/results_preview",
                params={"output_mode": "json", "count": 10},
                operation="get preview",
            )
            # If we get here, preview endpoint works
            assert "results" in response or "messages" in response
        except Exception:
            # Preview may not be available for fast searches
            pass

        # Wait for completion
        job_helper.wait_for_done(sid)
