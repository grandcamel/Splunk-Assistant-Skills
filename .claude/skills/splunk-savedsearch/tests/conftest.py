#!/usr/bin/env python3
"""Pytest fixtures for splunk-savedsearch tests."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)


@pytest.fixture
def mock_splunk_client():
    """Create a mock SplunkClient for testing."""
    client = Mock()
    client.base_url = "https://splunk.example.com:8089/services"
    client.auth_method = "bearer"
    client.timeout = 30
    client.get.return_value = {"entry": []}
    client.post.return_value = {}
    client.delete.return_value = {}
    return client


@pytest.fixture
def sample_savedsearches_response():
    """Sample saved searches list response."""
    return {
        "entry": [
            {
                "name": "Daily Error Report",
                "content": {
                    "search": "index=main level=ERROR | stats count by host",
                    "description": "Daily summary of errors",
                    "is_scheduled": True,
                    "cron_schedule": "0 6 * * *",
                    "disabled": False,
                },
            },
            {
                "name": "Weekly Summary",
                "content": {
                    "search": "index=main | timechart count",
                    "description": "Weekly event summary",
                    "is_scheduled": True,
                    "cron_schedule": "0 0 * * 0",
                    "disabled": False,
                },
            },
        ]
    }


@pytest.fixture
def sample_single_savedsearch():
    """Sample single saved search response."""
    return {
        "entry": [
            {
                "name": "Daily Error Report",
                "content": {
                    "search": "index=main level=ERROR | stats count by host",
                    "description": "Daily summary of errors",
                    "is_scheduled": True,
                    "cron_schedule": "0 6 * * *",
                    "disabled": False,
                    "next_scheduled_time": "2024-01-01T06:00:00",
                    "dispatch.earliest_time": "-24h",
                    "dispatch.latest_time": "now",
                },
            }
        ]
    }


@pytest.fixture
def sample_dispatch_response():
    """Sample dispatch (run) response."""
    return {"sid": "1703779200.12345"}
