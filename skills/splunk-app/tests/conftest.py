#!/usr/bin/env python3
"""
Pytest fixtures for splunk-app tests.

Note: Common fixtures (mock_splunk_client, mock_config, temp_path, temp_dir)
are provided by the root conftest.py.
"""

import pytest


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
