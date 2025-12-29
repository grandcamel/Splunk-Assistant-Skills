#!/usr/bin/env python3
"""
Pytest configuration for splunk-search live integration tests.

Imports fixtures from the shared live_integration module.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Generator

import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Suppress urllib3 warnings about self-signed certs
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add paths to sys.path for imports
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
lib_path = shared_path / "scripts" / "lib"
tests_path = shared_path / "tests" / "live_integration"

for p in [str(lib_path), str(tests_path), str(shared_path / "tests")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Now import from the shared modules
from splunk_container import SplunkContainer, ExternalSplunkConnection, get_splunk_connection
from test_utils import generate_test_events, wait_for_indexing


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "live: marks tests as requiring live Splunk connection"
    )
    config.addinivalue_line(
        "markers", "docker_required: marks tests that require Docker"
    )
    config.addinivalue_line(
        "markers", "external_splunk: marks tests for external Splunk only"
    )
    config.addinivalue_line(
        "markers", "slow_integration: marks slow integration tests"
    )
    config.addinivalue_line(
        "markers", "destructive: marks tests that modify Splunk configuration"
    )


# =============================================================================
# Session-Scoped Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def splunk_connection():
    """Session-scoped Splunk connection."""
    connection = get_splunk_connection()

    if isinstance(connection, SplunkContainer):
        connection.start()
        yield connection
        connection.stop()
    else:
        yield connection


@pytest.fixture(scope="session")
def splunk_client(splunk_connection):
    """Session-scoped SplunkClient instance."""
    client = splunk_connection.get_client()
    yield client


@pytest.fixture(scope="session")
def splunk_info(splunk_client) -> dict:
    """Get Splunk server information."""
    return splunk_client.get_server_info()


@pytest.fixture(scope="session")
def test_index_name() -> str:
    """Get the test index name."""
    return os.environ.get("SPLUNK_TEST_INDEX", "splunk_skills_test")


@pytest.fixture(scope="session")
def test_index(splunk_connection, test_index_name: str) -> Generator[str, None, None]:
    """Session-scoped test index."""
    created = splunk_connection.create_test_index(test_index_name)
    if not created:
        logging.warning(f"Could not create test index {test_index_name}, may already exist")

    yield test_index_name

    if isinstance(splunk_connection, SplunkContainer):
        splunk_connection.delete_test_index(test_index_name)


@pytest.fixture(scope="session")
def test_data(splunk_connection, test_index: str) -> dict:
    """Generate synthetic test data using SPL."""
    event_types = [
        {
            "name": "web_access",
            "count": 100,
            "fields": {
                "sourcetype": "access_combined",
                "host": ["web01", "web02", "web03"],
                "status": [200, 200, 200, 200, 404, 500],
                "uri": ["/api/users", "/api/orders", "/health", "/login"],
            },
        },
        {
            "name": "application_logs",
            "count": 50,
            "fields": {
                "sourcetype": "app_logs",
                "host": ["app01", "app02"],
                "level": ["INFO", "INFO", "INFO", "WARN", "ERROR"],
                "component": ["auth", "api", "db", "cache"],
            },
        },
        {
            "name": "metrics",
            "count": 200,
            "fields": {
                "sourcetype": "metrics",
                "host": ["server01", "server02", "server03"],
                "metric_name": ["cpu.percent", "mem.percent", "disk.percent"],
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
        logging.info(f"Generated {count} {event_type['name']} events")

    wait_for_indexing(splunk_connection, test_index, min_events=total_events)

    return {
        "index": test_index,
        "total_events": total_events,
        "event_types": event_types,
    }


# =============================================================================
# Helper Fixtures
# =============================================================================

@pytest.fixture
def search_helper(splunk_client):
    """Helper for executing searches in tests."""

    class SearchHelper:
        def __init__(self, client):
            self.client = client

        def oneshot(self, spl: str, **kwargs) -> list:
            """Execute oneshot search and return results."""
            response = self.client.post(
                "/search/jobs/oneshot",
                data={
                    "search": spl,
                    "output_mode": "json",
                    "earliest_time": kwargs.get("earliest_time", "-24h"),
                    "latest_time": kwargs.get("latest_time", "now"),
                    "count": kwargs.get("count", 1000),
                },
                timeout=kwargs.get("timeout", 60),
                operation="test search",
            )
            return response.get("results", [])

        def count(self, spl: str, **kwargs) -> int:
            """Execute search and return result count."""
            results = self.oneshot(f"{spl} | stats count", **kwargs)
            if results:
                return int(results[0].get("count", 0))
            return 0

        def exists(self, spl: str, **kwargs) -> bool:
            """Check if search returns any results."""
            return self.count(spl, **kwargs) > 0

    return SearchHelper(splunk_client)


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

        def get_status(self, sid: str) -> dict:
            """Get job status."""
            response = self.client.get(
                f"/search/v2/jobs/{sid}",
                operation="get job status",
            )
            if "entry" in response and response["entry"]:
                return response["entry"][0].get("content", {})
            return {}

        def wait_for_done(self, sid: str, timeout: int = 60) -> dict:
            """Wait for job to complete."""
            start = time.time()
            while time.time() - start < timeout:
                status = self.get_status(sid)
                if status.get("isDone"):
                    return status
                time.sleep(1)
            raise TimeoutError(f"Job {sid} did not complete in {timeout}s")

        def cleanup(self):
            """Cancel and delete all created jobs."""
            for sid in self.created_jobs:
                try:
                    self.client.post(
                        f"/search/v2/jobs/{sid}/control",
                        data={"action": "cancel"},
                    )
                except Exception:
                    pass
            self.created_jobs.clear()

    helper = JobHelper(splunk_client)
    yield helper
    helper.cleanup()
