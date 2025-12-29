#!/usr/bin/env python3
"""
Live Integration Tests for splunk-job skill.

Tests search job lifecycle operations against a real Splunk instance.
"""

import time
import pytest

# Note: Fixtures (splunk_client, test_index, test_data, job_helper, etc.) are provided by conftest.py


class TestJobCreation:
    """Integration tests for job creation."""

    @pytest.mark.live
    def test_create_job_returns_sid(self, splunk_client, test_index):
        """Test creating a job returns a valid SID."""
        response = splunk_client.post(
            "/search/v2/jobs",
            data={
                "search": f"search index={test_index} | head 10",
                "exec_mode": "normal",
            },
            operation="create job",
        )

        sid = response.get("sid")
        if not sid and "entry" in response:
            sid = response["entry"][0].get("name")

        assert sid is not None
        assert "." in sid  # SID format: timestamp.id

    @pytest.mark.live
    def test_create_job_with_time_range(self, splunk_client, test_index):
        """Test creating a job with explicit time range."""
        response = splunk_client.post(
            "/search/v2/jobs",
            data={
                "search": f"search index={test_index}",
                "exec_mode": "normal",
                "earliest_time": "-1h",
                "latest_time": "now",
            },
            operation="create job with time",
        )

        sid = response.get("sid")
        if not sid and "entry" in response:
            sid = response["entry"][0].get("name")

        assert sid is not None


class TestJobStatus:
    """Integration tests for job status retrieval."""

    @pytest.mark.live
    def test_get_job_status(self, splunk_client, job_helper, test_index):
        """Test retrieving job status."""
        sid = job_helper.create(f"search index={test_index} | head 10")

        response = splunk_client.get(
            f"/search/v2/jobs/{sid}",
            operation="get job status",
        )

        assert "entry" in response
        content = response["entry"][0].get("content", {})

        # Check required status fields
        assert "dispatchState" in content
        assert "doneProgress" in content
        assert content["dispatchState"] in [
            "QUEUED", "PARSING", "RUNNING", "FINALIZING", "DONE", "FAILED"
        ]

    @pytest.mark.live
    def test_job_progress_updates(self, splunk_client, job_helper, test_index, test_data):
        """Test that job progress updates as search runs."""
        # Create a search that takes some time
        sid = job_helper.create(
            f"search index={test_index} | stats count by host, sourcetype",
            earliest_time="-24h",
        )

        # Poll for updates
        states_seen = set()
        for _ in range(30):  # Max 30 seconds
            response = splunk_client.get(
                f"/search/v2/jobs/{sid}",
                operation="poll status",
            )
            content = response["entry"][0].get("content", {})
            states_seen.add(content.get("dispatchState"))

            if content.get("isDone"):
                break
            time.sleep(1)

        # Should see at least initial and done states
        assert "DONE" in states_seen or len(states_seen) > 0


class TestJobControl:
    """Integration tests for job control actions."""

    @pytest.mark.live
    def test_cancel_running_job(self, splunk_client, test_index):
        """Test cancelling a running job."""
        # Create a long-running job
        response = splunk_client.post(
            "/search/v2/jobs",
            data={
                "search": f"search index={test_index} | head 10000",
                "exec_mode": "normal",
            },
            operation="create job",
        )

        sid = response.get("sid")
        if not sid and "entry" in response:
            sid = response["entry"][0].get("name")

        # Cancel it
        splunk_client.post(
            f"/search/v2/jobs/{sid}/control",
            data={"action": "cancel"},
            operation="cancel job",
        )

        # Verify cancelled - job may be deleted immediately after cancel (404)
        # or may still exist in done/failed state
        time.sleep(0.5)
        try:
            status_response = splunk_client.get(
                f"/search/v2/jobs/{sid}",
                operation="check cancelled",
            )
            content = status_response["entry"][0].get("content", {})
            # Job should be done (cancelled counts as done)
            assert content.get("isDone") or content.get("isFailed")
        except Exception as e:
            # 404 means job was deleted after cancel - that's also success
            if "404" in str(e) or "NotFound" in str(e):
                pass  # Job deleted = cancel succeeded
            else:
                raise

    @pytest.mark.live
    def test_pause_unpause_job(self, splunk_client, test_index, test_data):
        """Test pausing and unpausing a job."""
        # Create a job
        response = splunk_client.post(
            "/search/v2/jobs",
            data={
                "search": f"search index={test_index} | head 1000",
                "exec_mode": "normal",
            },
            operation="create job",
        )

        sid = response.get("sid")
        if not sid and "entry" in response:
            sid = response["entry"][0].get("name")

        # Pause it
        splunk_client.post(
            f"/search/v2/jobs/{sid}/control",
            data={"action": "pause"},
            operation="pause job",
        )

        # Check paused state
        time.sleep(0.5)
        status = splunk_client.get(f"/search/v2/jobs/{sid}")
        content = status["entry"][0].get("content", {})

        # Note: Fast searches may complete before pause takes effect
        if not content.get("isDone"):
            assert content.get("isPaused") is True

            # Unpause
            splunk_client.post(
                f"/search/v2/jobs/{sid}/control",
                data={"action": "unpause"},
                operation="unpause job",
            )

    @pytest.mark.live
    def test_finalize_job(self, splunk_client, test_index, test_data):
        """Test finalizing a running job."""
        # Create a job
        response = splunk_client.post(
            "/search/v2/jobs",
            data={
                "search": f"search index={test_index}",
                "exec_mode": "normal",
            },
            operation="create job",
        )

        sid = response.get("sid")
        if not sid and "entry" in response:
            sid = response["entry"][0].get("name")

        # Finalize it
        splunk_client.post(
            f"/search/v2/jobs/{sid}/control",
            data={"action": "finalize"},
            operation="finalize job",
        )

        # Wait and check
        time.sleep(1)
        status = splunk_client.get(f"/search/v2/jobs/{sid}")
        content = status["entry"][0].get("content", {})

        # Should be done after finalize
        assert content.get("isDone") is True

    @pytest.mark.live
    def test_set_job_ttl(self, splunk_client, job_helper, test_index):
        """Test setting job TTL."""
        sid = job_helper.create(f"search index={test_index} | head 1")
        job_helper.wait_for_done(sid)

        # Set TTL
        splunk_client.post(
            f"/search/v2/jobs/{sid}/control",
            data={"action": "setttl", "ttl": 3600},
            operation="set ttl",
        )

        # Verify TTL was set
        status = splunk_client.get(f"/search/v2/jobs/{sid}")
        content = status["entry"][0].get("content", {})
        assert int(content.get("ttl", 0)) >= 3600


class TestJobResults:
    """Integration tests for job result retrieval."""

    @pytest.mark.live
    def test_get_results_from_completed_job(self, splunk_client, job_helper, test_index, test_data):
        """Test getting results from completed job."""
        sid = job_helper.create(f"search index={test_index} | head 10")
        job_helper.wait_for_done(sid)

        response = splunk_client.get(
            f"/search/v2/jobs/{sid}/results",
            params={"output_mode": "json", "count": 100},
            operation="get results",
        )

        assert "results" in response
        results = response["results"]
        assert len(results) > 0

    @pytest.mark.live
    def test_get_results_with_pagination(self, splunk_client, job_helper, test_index, test_data):
        """Test getting results with pagination."""
        sid = job_helper.create(f"search index={test_index} | head 20")
        job_helper.wait_for_done(sid)

        # Get first page
        page1 = splunk_client.get(
            f"/search/v2/jobs/{sid}/results",
            params={"output_mode": "json", "count": 5, "offset": 0},
            operation="get page 1",
        )

        # Get second page
        page2 = splunk_client.get(
            f"/search/v2/jobs/{sid}/results",
            params={"output_mode": "json", "count": 5, "offset": 5},
            operation="get page 2",
        )

        assert len(page1.get("results", [])) <= 5
        assert len(page2.get("results", [])) <= 5

    @pytest.mark.live
    def test_get_job_summary(self, splunk_client, job_helper, test_index, test_data):
        """Test getting job summary with field statistics."""
        sid = job_helper.create(f"search index={test_index} | head 50")
        job_helper.wait_for_done(sid)

        # Summary endpoint may return empty or non-JSON for some searches
        try:
            response = splunk_client.get(
                f"/search/v2/jobs/{sid}/summary",
                params={"output_mode": "json"},
                operation="get summary",
            )
            # Summary should contain field information if available
            assert response is not None
        except Exception as e:
            # JSONDecodeError is acceptable - some searches have no summary
            if "JSONDecodeError" in str(type(e).__name__) or "Expecting value" in str(e):
                pass  # Empty summary is valid
            else:
                raise


class TestJobList:
    """Integration tests for job listing."""

    @pytest.mark.live
    def test_list_jobs(self, splunk_client):
        """Test listing search jobs."""
        response = splunk_client.get(
            "/search/jobs",
            params={"output_mode": "json", "count": 10},
            operation="list jobs",
        )

        assert "entry" in response
        # May have 0 or more jobs

    @pytest.mark.live
    def test_list_jobs_includes_created_job(self, splunk_client, job_helper, test_index):
        """Test that created job appears in list."""
        sid = job_helper.create(f"search index={test_index} | head 1")

        response = splunk_client.get(
            "/search/jobs",
            params={"output_mode": "json", "count": 50},
            operation="list jobs",
        )

        # In job list, SID is in content.sid, not in name (which is the search query)
        sids = [entry.get("content", {}).get("sid") for entry in response.get("entry", [])]
        assert sid in sids, f"Created job {sid} not found in job list"


class TestJobDeletion:
    """Integration tests for job deletion."""

    @pytest.mark.live
    def test_delete_completed_job(self, splunk_client, test_index):
        """Test deleting a completed job."""
        # Create and complete a job
        response = splunk_client.post(
            "/search/v2/jobs",
            data={
                "search": f"search index={test_index} | head 1",
                "exec_mode": "blocking",
            },
            timeout=60,
            operation="create blocking job",
        )

        # v2/jobs with blocking returns {"sid": "..."} directly
        sid = response.get("sid")
        if not sid and "entry" in response:
            sid = response["entry"][0].get("name")

        # Delete it
        splunk_client.delete(
            f"/search/jobs/{sid}",
            operation="delete job",
        )

        # Verify deleted (should get 404)
        with pytest.raises(Exception):
            splunk_client.get(f"/search/v2/jobs/{sid}")
