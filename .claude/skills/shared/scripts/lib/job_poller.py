#!/usr/bin/env python3
"""
Search Job State Polling

Provides utilities for monitoring and managing Splunk search job lifecycle.
Handles async job state transitions and provides blocking wait functionality.

Job States (dispatchState):
    QUEUED -> PARSING -> RUNNING -> FINALIZING -> DONE
    FAILED (on error)
    PAUSED (on pause)
"""

import time
from enum import Enum
from typing import Any, Callable, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .splunk_client import SplunkClient


class JobState(Enum):
    """Splunk search job states."""

    QUEUED = "QUEUED"
    PARSING = "PARSING"
    RUNNING = "RUNNING"
    FINALIZING = "FINALIZING"
    DONE = "DONE"
    FAILED = "FAILED"
    PAUSED = "PAUSED"

    @property
    def is_active(self) -> bool:
        """Check if job is still active (not terminal)."""
        return self in (
            JobState.QUEUED,
            JobState.PARSING,
            JobState.RUNNING,
            JobState.FINALIZING,
        )

    @property
    def is_terminal(self) -> bool:
        """Check if job is in terminal state."""
        return self in (JobState.DONE, JobState.FAILED)

    @property
    def is_success(self) -> bool:
        """Check if job completed successfully."""
        return self == JobState.DONE


class JobProgress:
    """Represents search job progress information."""

    def __init__(self, data: Dict[str, Any]):
        """
        Initialize from job status response.

        Args:
            data: Job status content dictionary
        """
        self.data = data
        self.sid = data.get("sid", "")
        self.state = JobState(data.get("dispatchState", "QUEUED"))
        self.done_progress = float(data.get("doneProgress", 0))
        self.event_count = int(data.get("eventCount", 0))
        self.result_count = int(data.get("resultCount", 0))
        self.scan_count = int(data.get("scanCount", 0))
        self.run_duration = float(data.get("runDuration", 0))
        self.is_done = data.get("isDone", False)
        self.is_failed = data.get("isFailed", False)
        self.is_paused = data.get("isPaused", False)
        self.messages = data.get("messages", [])

    @property
    def progress_percent(self) -> float:
        """Get progress as percentage."""
        return self.done_progress * 100

    @property
    def error_message(self) -> Optional[str]:
        """Get error message if job failed."""
        if self.is_failed and self.messages:
            for msg in self.messages:
                if msg.get("type") == "ERROR":
                    return msg.get("text")
        return None

    def __repr__(self) -> str:
        return (
            f"JobProgress(sid={self.sid!r}, state={self.state.value}, "
            f"progress={self.progress_percent:.1f}%, results={self.result_count})"
        )


def get_dispatch_state(client: "SplunkClient", sid: str) -> JobProgress:
    """
    Get current job dispatch state.

    Args:
        client: SplunkClient instance
        sid: Search job ID

    Returns:
        JobProgress object with current state

    Raises:
        NotFoundError: If job doesn't exist
    """
    response = client.get(
        f"/search/v2/jobs/{sid}",
        operation=f"get job status {sid}",
    )

    if "entry" in response and response["entry"]:
        content = response["entry"][0].get("content", {})
        content["sid"] = sid
        return JobProgress(content)

    raise ValueError(f"Invalid job status response for {sid}")


def poll_job_status(
    client: "SplunkClient",
    sid: str,
    timeout: int = 300,
    poll_interval: float = 1.0,
    max_poll_interval: float = 5.0,
    progress_callback: Optional[Callable[[JobProgress], None]] = None,
) -> JobProgress:
    """
    Poll job status until completion or timeout.

    Uses exponential backoff for polling interval to reduce API calls.

    Args:
        client: SplunkClient instance
        sid: Search job ID
        timeout: Maximum time to wait in seconds (default: 300)
        poll_interval: Initial polling interval in seconds (default: 1.0)
        max_poll_interval: Maximum polling interval (default: 5.0)
        progress_callback: Optional callback for progress updates

    Returns:
        Final JobProgress when job completes

    Raises:
        TimeoutError: If job doesn't complete within timeout
        JobFailedError: If job fails
    """
    try:
        from .error_handler import JobFailedError
    except ImportError:
        from error_handler import JobFailedError

    start_time = time.time()
    current_interval = poll_interval

    while True:
        elapsed = time.time() - start_time
        if elapsed >= timeout:
            raise TimeoutError(f"Job {sid} did not complete within {timeout} seconds")

        progress = get_dispatch_state(client, sid)

        # Call progress callback if provided
        if progress_callback:
            try:
                progress_callback(progress)
            except Exception:
                pass  # Don't fail on callback errors

        # Check terminal states
        if progress.state.is_terminal:
            if progress.is_failed:
                error_msg = progress.error_message or "Unknown error"
                raise JobFailedError(
                    message=error_msg,
                    sid=sid,
                    dispatch_state=progress.state.value,
                )
            return progress

        # Check pause state
        if progress.is_paused:
            # Job is paused, return current state
            return progress

        # Wait before next poll
        time.sleep(current_interval)

        # Increase interval with exponential backoff
        current_interval = min(current_interval * 1.5, max_poll_interval)


def wait_for_job(
    client: "SplunkClient",
    sid: str,
    timeout: int = 300,
    show_progress: bool = False,
) -> JobProgress:
    """
    Wait for job completion with optional progress display.

    Args:
        client: SplunkClient instance
        sid: Search job ID
        timeout: Maximum wait time in seconds
        show_progress: Print progress updates

    Returns:
        Final JobProgress

    Raises:
        TimeoutError: If job doesn't complete
        JobFailedError: If job fails
    """

    def progress_callback(progress: JobProgress) -> None:
        if show_progress:
            print(
                f"\rJob {progress.sid}: {progress.state.value} "
                f"({progress.progress_percent:.0f}%) "
                f"- {progress.result_count:,} results",
                end="",
                flush=True,
            )

    try:
        result = poll_job_status(
            client, sid, timeout=timeout, progress_callback=progress_callback
        )
        if show_progress:
            print()  # New line after progress
        return result
    except Exception:
        if show_progress:
            print()  # New line on error
        raise


def cancel_job(client: "SplunkClient", sid: str) -> bool:
    """
    Cancel a running search job.

    Args:
        client: SplunkClient instance
        sid: Search job ID

    Returns:
        True if cancellation was successful

    Raises:
        SplunkError: On API errors
    """
    response = client.post(
        f"/search/v2/jobs/{sid}/control",
        data={"action": "cancel"},
        operation=f"cancel job {sid}",
    )
    return True


def pause_job(client: "SplunkClient", sid: str) -> bool:
    """
    Pause a running search job.

    Args:
        client: SplunkClient instance
        sid: Search job ID

    Returns:
        True if pause was successful
    """
    response = client.post(
        f"/search/v2/jobs/{sid}/control",
        data={"action": "pause"},
        operation=f"pause job {sid}",
    )
    return True


def unpause_job(client: "SplunkClient", sid: str) -> bool:
    """
    Resume a paused search job.

    Args:
        client: SplunkClient instance
        sid: Search job ID

    Returns:
        True if unpause was successful
    """
    response = client.post(
        f"/search/v2/jobs/{sid}/control",
        data={"action": "unpause"},
        operation=f"unpause job {sid}",
    )
    return True


def finalize_job(client: "SplunkClient", sid: str) -> bool:
    """
    Finalize a search job (stop streaming, return current results).

    Args:
        client: SplunkClient instance
        sid: Search job ID

    Returns:
        True if finalization was successful
    """
    response = client.post(
        f"/search/v2/jobs/{sid}/control",
        data={"action": "finalize"},
        operation=f"finalize job {sid}",
    )
    return True


def set_job_ttl(client: "SplunkClient", sid: str, ttl: int) -> bool:
    """
    Set job time-to-live to extend retention.

    Args:
        client: SplunkClient instance
        sid: Search job ID
        ttl: Time-to-live in seconds

    Returns:
        True if TTL was set successfully
    """
    response = client.post(
        f"/search/v2/jobs/{sid}/control",
        data={"action": "setttl", "ttl": ttl},
        operation=f"set TTL for job {sid}",
    )
    return True


def touch_job(client: "SplunkClient", sid: str) -> bool:
    """
    Touch a job to extend its TTL.

    Args:
        client: SplunkClient instance
        sid: Search job ID

    Returns:
        True if touch was successful
    """
    response = client.post(
        f"/search/v2/jobs/{sid}/control",
        data={"action": "touch"},
        operation=f"touch job {sid}",
    )
    return True


def get_job_summary(client: "SplunkClient", sid: str) -> Dict[str, Any]:
    """
    Get job summary with field statistics.

    Args:
        client: SplunkClient instance
        sid: Search job ID

    Returns:
        Summary dictionary with field information
    """
    response = client.get(
        f"/search/v2/jobs/{sid}/summary",
        operation=f"get job summary {sid}",
    )
    return response


def list_jobs(
    client: "SplunkClient",
    count: int = 50,
    offset: int = 0,
) -> list:
    """
    List current search jobs.

    Args:
        client: SplunkClient instance
        count: Maximum number of jobs to return
        offset: Offset for pagination

    Returns:
        List of job information dictionaries
    """
    response = client.get(
        "/search/jobs",
        params={"count": count, "offset": offset},
        operation="list jobs",
    )

    jobs = []
    for entry in response.get("entry", []):
        job_data = entry.get("content", {})
        job_data["sid"] = entry.get("name", "")
        jobs.append(job_data)

    return jobs


def delete_job(client: "SplunkClient", sid: str) -> bool:
    """
    Delete a search job.

    Args:
        client: SplunkClient instance
        sid: Search job ID

    Returns:
        True if deletion was successful
    """
    response = client.delete(
        f"/search/jobs/{sid}",
        operation=f"delete job {sid}",
    )
    return True
