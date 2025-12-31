#!/usr/bin/env python3
"""
Pytest fixtures for splunk-savedsearch tests.

Note: Common fixtures (mock_splunk_client, mock_config, temp_path, temp_dir)
are provided by the root conftest.py.
"""

import pytest


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
