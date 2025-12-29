#!/usr/bin/env python3
"""Pytest fixtures for splunk-app tests."""

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
def sample_apps_response():
    """Sample apps list response."""
    return {
        "entry": [
            {
                "name": "search",
                "content": {
                    "label": "Search & Reporting",
                    "version": "9.1.2",
                    "visible": True,
                    "disabled": False,
                },
            },
            {
                "name": "splunk_httpinput",
                "content": {
                    "label": "Splunk HTTP Input",
                    "version": "1.0.0",
                    "visible": False,
                    "disabled": False,
                },
            },
        ]
    }


@pytest.fixture
def sample_single_app():
    """Sample single app response."""
    return {
        "entry": [
            {
                "name": "search",
                "content": {
                    "label": "Search & Reporting",
                    "version": "9.1.2",
                    "author": "Splunk",
                    "description": "Search and reporting app",
                    "visible": True,
                    "disabled": False,
                    "configured": True,
                    "check_for_updates": True,
                },
            }
        ]
    }
