#!/usr/bin/env python3
"""Pytest fixtures for splunk-metadata tests."""

from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_splunk_client():
    """Create a mock SplunkClient for testing."""
    client = Mock()
    client.base_url = "https://splunk.example.com:8089/services"
    client.auth_method = "bearer"
    client.timeout = 30
    client.get.return_value = {"entry": []}
    client.post.return_value = {}
    return client


@pytest.fixture
def sample_index_response():
    """Sample single index response."""
    return {
        "entry": [
            {
                "name": "main",
                "content": {
                    "datatype": "event",
                    "homePath": "$SPLUNK_DB/main/db",
                    "coldPath": "$SPLUNK_DB/main/colddb",
                    "thawedPath": "$SPLUNK_DB/main/thaweddb",
                    "maxDataSize": "auto_high_volume",
                    "maxTotalDataSizeMB": 500000,
                    "frozenTimePeriodInSecs": 188697600,
                    "totalEventCount": 1000000,
                    "currentDBSizeMB": 1024,
                    "disabled": False,
                },
            }
        ]
    }


@pytest.fixture
def sample_sourcetypes_response():
    """Sample sourcetypes search results."""
    return {
        "results": [
            {
                "sourcetype": "access_combined",
                "totalCount": "10000",
                "firstTime": "2024-01-01T00:00:00",
                "lastTime": "2024-01-15T12:00:00",
            },
            {
                "sourcetype": "syslog",
                "totalCount": "5000",
                "firstTime": "2024-01-01T00:00:00",
                "lastTime": "2024-01-15T12:00:00",
            },
        ]
    }
