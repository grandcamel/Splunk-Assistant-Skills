#!/usr/bin/env python3
"""
Pytest fixtures for splunk-security tests.

Note: Common fixtures (mock_splunk_client, mock_config, temp_path, temp_dir)
are provided by the root conftest.py.
"""

import pytest


@pytest.fixture
def sample_current_user_response():
    """Sample current user context response."""
    return {
        "entry": [
            {
                "content": {
                    "username": "admin",
                    "realname": "Administrator",
                    "email": "admin@example.com",
                    "roles": ["admin", "power", "user"],
                    "capabilities": ["admin_all_objects", "change_own_password"],
                    "defaultApp": "search",
                }
            }
        ]
    }


@pytest.fixture
def sample_users_response():
    """Sample users list response."""
    return {
        "entry": [
            {
                "name": "admin",
                "content": {
                    "realname": "Administrator",
                    "email": "admin@example.com",
                    "roles": ["admin"],
                    "defaultApp": "search",
                },
            },
            {
                "name": "analyst",
                "content": {
                    "realname": "Security Analyst",
                    "email": "analyst@example.com",
                    "roles": ["user"],
                    "defaultApp": "search",
                },
            },
        ]
    }


@pytest.fixture
def sample_roles_response():
    """Sample roles list response."""
    return {
        "entry": [
            {
                "name": "admin",
                "content": {
                    "capabilities": ["admin_all_objects", "change_own_password"],
                    "imported_roles": ["power", "user"],
                    "srchFilter": None,
                },
            },
            {
                "name": "user",
                "content": {
                    "capabilities": ["change_own_password", "search"],
                    "imported_roles": [],
                    "srchFilter": "index=main",
                },
            },
        ]
    }
