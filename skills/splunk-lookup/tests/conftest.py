#!/usr/bin/env python3
"""
Pytest fixtures for splunk-lookup tests.

Note: Common fixtures (mock_splunk_client, mock_config, temp_path, temp_dir)
are provided by the root conftest.py.
"""

import pytest


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
