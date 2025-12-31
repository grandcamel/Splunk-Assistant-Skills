#!/usr/bin/env python3
"""
Pytest fixtures for splunk-metadata tests.

Note: Common fixtures (mock_splunk_client, mock_config, sample_index_list,
temp_path, temp_dir) are provided by the root conftest.py.
"""

import pytest


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
