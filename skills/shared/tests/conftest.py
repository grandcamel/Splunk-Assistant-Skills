#!/usr/bin/env python3
"""
Shared pytest fixtures for Splunk Assistant Skills tests.
"""

import os
from unittest.mock import MagicMock, Mock

import pytest


@pytest.fixture
def mock_splunk_client():
    """Create a mock SplunkClient for testing."""
    client = Mock()
    client.base_url = "https://splunk.example.com:8089/services"
    client.auth_method = "bearer"
    client.timeout = 30
    client.DEFAULT_SEARCH_TIMEOUT = 300

    # Default responses
    client.get.return_value = {"entry": []}
    client.post.return_value = {"sid": "1703779200.12345"}
    client.put.return_value = {}
    client.delete.return_value = {}

    return client


@pytest.fixture
def mock_config():
    """Create mock configuration."""
    return {
        "splunk": {
            "default_profile": "test",
            "profiles": {
                "test": {
                    "url": "https://splunk.example.com",
                    "port": 8089,
                    "token": "test-token",
                    "auth_method": "bearer",
                }
            },
            "api": {
                "timeout": 30,
                "search_timeout": 300,
            },
            "search_defaults": {
                "earliest_time": "-24h",
                "latest_time": "now",
                "max_count": 50000,
            },
        }
    }


@pytest.fixture
def sample_job_response():
    """Sample search job response."""
    return {
        "sid": "1703779200.12345",
        "entry": [
            {
                "name": "1703779200.12345",
                "content": {
                    "sid": "1703779200.12345",
                    "dispatchState": "DONE",
                    "doneProgress": 1.0,
                    "eventCount": 1000,
                    "resultCount": 100,
                    "scanCount": 5000,
                    "runDuration": 2.5,
                    "isDone": True,
                    "isFailed": False,
                    "isPaused": False,
                },
            }
        ],
    }


@pytest.fixture
def sample_search_results():
    """Sample search results."""
    return {
        "results": [
            {"host": "server1", "status": "200", "count": "100"},
            {"host": "server2", "status": "200", "count": "150"},
            {"host": "server3", "status": "404", "count": "25"},
        ]
    }


@pytest.fixture
def sample_index_list():
    """Sample index list response."""
    return {
        "entry": [
            {
                "name": "main",
                "content": {
                    "totalEventCount": 1000000,
                    "currentDBSizeMB": 1024,
                    "maxDataSizeMB": 500000,
                    "disabled": False,
                },
            },
            {
                "name": "_internal",
                "content": {
                    "totalEventCount": 500000,
                    "currentDBSizeMB": 256,
                    "maxDataSizeMB": 500000,
                    "disabled": False,
                },
            },
        ]
    }


# Pytest configuration
def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--profile",
        action="store",
        default=None,
        help="Splunk profile for live integration tests",
    )


@pytest.fixture
def splunk_profile(request):
    """Get Splunk profile from command line or environment."""
    profile = request.config.getoption("--profile")
    if not profile:
        profile = os.environ.get("SPLUNK_PROFILE")
    return profile


# Markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "live: marks tests as requiring live Splunk connection"
    )
    config.addinivalue_line("markers", "destructive: marks tests that modify data")
    config.addinivalue_line("markers", "slow: marks tests as slow running")
