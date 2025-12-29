#!/usr/bin/env python3
"""Pytest fixtures for splunk-lookup tests."""

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
def sample_lookups_response():
    """Sample lookups list response."""
    return {
        "entry": [
            {
                "name": "users.csv",
                "content": {
                    "eai:appName": "search",
                    "eai:data": "/opt/splunk/etc/apps/search/lookups/users.csv",
                },
            },
            {
                "name": "assets.csv",
                "content": {
                    "eai:appName": "search",
                    "eai:data": "/opt/splunk/etc/apps/search/lookups/assets.csv",
                },
            },
        ]
    }


@pytest.fixture
def sample_single_lookup():
    """Sample single lookup response."""
    return {
        "entry": [
            {
                "name": "users.csv",
                "author": "admin",
                "content": {
                    "eai:appName": "search",
                    "eai:data": "/opt/splunk/etc/apps/search/lookups/users.csv",
                },
            }
        ]
    }
