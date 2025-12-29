#!/usr/bin/env python3
"""Pytest fixtures for splunk-alert tests."""

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
    client.delete.return_value = {}
    return client


@pytest.fixture
def sample_alerts_response():
    """Sample fired alerts list response."""
    return {
        "entry": [
            {
                "name": "Alert_1",
                "content": {
                    "severity": 4,
                    "triggered_alert_count": 5,
                    "savedsearch_name": "High Error Rate",
                },
            },
            {
                "name": "Alert_2",
                "content": {
                    "severity": 3,
                    "triggered_alert_count": 2,
                    "savedsearch_name": "Login Failures",
                },
            },
        ]
    }


@pytest.fixture
def sample_single_alert():
    """Sample single alert response."""
    return {
        "entry": [
            {
                "name": "Alert_1",
                "content": {
                    "savedsearch_name": "High Error Rate",
                    "severity": 4,
                    "trigger_time": "2024-01-15T10:30:00",
                    "triggered_alert_count": 5,
                    "expiration_time": "2024-01-15T11:30:00",
                    "digest_mode": False,
                },
            }
        ]
    }
