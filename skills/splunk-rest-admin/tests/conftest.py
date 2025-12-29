#!/usr/bin/env python3
"""Pytest fixtures for splunk-rest-admin tests."""

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
    return client


@pytest.fixture
def sample_server_info_response():
    """Sample server info response."""
    return {
        "entry": [
            {
                "name": "server-info",
                "content": {
                    "build": "12345",
                    "version": "9.1.2",
                    "serverName": "splunk-server",
                    "os_name": "Linux",
                    "cpu_arch": "x86_64",
                },
            }
        ]
    }


@pytest.fixture
def sample_server_status_response():
    """Sample server status response."""
    return {
        "entry": [
            {
                "name": "status",
                "content": {
                    "state": "running",
                    "license_state": "OK",
                },
            }
        ]
    }


@pytest.fixture
def sample_server_health_response():
    """Sample server health response."""
    return {
        "entry": [
            {
                "name": "splunkd",
                "content": {
                    "health": "green",
                    "features": {
                        "File Monitor Input": {"health": "green"},
                        "Index Processor": {"health": "green"},
                        "Search Scheduler": {"health": "yellow"},
                    },
                },
            }
        ]
    }
