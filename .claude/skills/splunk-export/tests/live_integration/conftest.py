#!/usr/bin/env python3
"""Pytest configuration for splunk-export live integration tests."""

import os
import sys
import logging
import tempfile
from pathlib import Path

import pytest

logging.basicConfig(level=logging.INFO)
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add shared lib to path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
lib_path = shared_path / "scripts" / "lib"

if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

# Import splunk_container module directly
sys.path.insert(0, str(shared_path / "tests" / "live_integration"))
from splunk_container import (
    SplunkContainer,
    ExternalSplunkConnection,
    get_splunk_connection,
)
from test_utils import generate_test_events, wait_for_indexing


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "live: marks tests as requiring live Splunk connection"
    )
    config.addinivalue_line(
        "markers", "destructive: marks tests that modify Splunk configuration"
    )


@pytest.fixture(scope="session")
def splunk_connection():
    connection = get_splunk_connection()
    if isinstance(connection, SplunkContainer):
        connection.start()
        yield connection
        connection.stop()
    else:
        yield connection


@pytest.fixture(scope="session")
def splunk_client(splunk_connection):
    yield splunk_connection.get_client()


@pytest.fixture(scope="session")
def test_index_name() -> str:
    return os.environ.get("SPLUNK_TEST_INDEX", "splunk_skills_test")


@pytest.fixture(scope="session")
def test_index(splunk_connection, test_index_name):
    created = splunk_connection.create_test_index(test_index_name)
    if not created:
        logging.warning(
            f"Could not create test index {test_index_name}, may already exist"
        )
    yield test_index_name


@pytest.fixture(scope="session")
def test_data(splunk_connection, test_index):
    """Generate test data for export tests."""
    event_types = [
        {
            "name": "export_test",
            "count": 100,
            "fields": {
                "sourcetype": "export_test",
                "host": ["host1", "host2", "host3"],
                "level": ["INFO", "WARN", "ERROR"],
                "message": ["Test message 1", "Test message 2", "Test message 3"],
            },
        },
    ]

    total_events = 0
    for event_type in event_types:
        count = generate_test_events(
            splunk_connection,
            index=test_index,
            count=event_type["count"],
            fields=event_type["fields"],
        )
        total_events += count

    wait_for_indexing(splunk_connection, test_index, min_events=total_events)

    return {
        "index": test_index,
        "total_events": total_events,
    }


@pytest.fixture
def job_helper(splunk_client):
    """Helper for managing search jobs in tests."""
    import time

    class JobHelper:
        def __init__(self, client):
            self.client = client
            self.created_jobs = []

        def create(self, spl: str, **kwargs) -> str:
            """Create a search job and return SID."""
            response = self.client.post(
                "/search/v2/jobs",
                data={
                    "search": spl,
                    "exec_mode": kwargs.get("exec_mode", "normal"),
                    "earliest_time": kwargs.get("earliest_time", "-24h"),
                    "latest_time": kwargs.get("latest_time", "now"),
                },
                operation="create test job",
            )
            sid = response.get("sid")
            if not sid and "entry" in response:
                sid = response["entry"][0].get("name")
            self.created_jobs.append(sid)
            return sid

        def wait_for_done(self, sid: str, timeout: int = 60) -> dict:
            """Wait for job to complete."""
            start = time.time()
            while time.time() - start < timeout:
                response = self.client.get(f"/search/v2/jobs/{sid}")
                if "entry" in response and response["entry"]:
                    content = response["entry"][0].get("content", {})
                    if content.get("isDone"):
                        return content
                time.sleep(1)
            raise TimeoutError(f"Job {sid} did not complete in {timeout}s")

        def cleanup(self):
            for sid in self.created_jobs:
                try:
                    self.client.post(
                        f"/search/v2/jobs/{sid}/control", data={"action": "cancel"}
                    )
                except Exception:
                    pass
            self.created_jobs.clear()

    helper = JobHelper(splunk_client)
    yield helper
    helper.cleanup()


@pytest.fixture
def temp_output_file():
    """Provide a temporary file for export tests."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    try:
        os.unlink(temp_path)
    except Exception:
        pass
