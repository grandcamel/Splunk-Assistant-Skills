#!/usr/bin/env python3
"""Pytest fixtures for splunk-security tests."""

import sys
from pathlib import Path
from unittest.mock import Mock
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))


@pytest.fixture
def mock_splunk_client():
    """Create a mock SplunkClient for testing."""
    client = Mock()
    client.base_url = 'https://splunk.example.com:8089/services'
    client.auth_method = 'bearer'
    client.timeout = 30
    client.get.return_value = {'entry': []}
    return client


@pytest.fixture
def sample_current_user_response():
    """Sample current user context response."""
    return {
        'entry': [{
            'content': {
                'username': 'admin',
                'realname': 'Administrator',
                'email': 'admin@example.com',
                'roles': ['admin', 'power', 'user'],
                'capabilities': ['admin_all_objects', 'change_own_password'],
                'defaultApp': 'search',
            }
        }]
    }


@pytest.fixture
def sample_users_response():
    """Sample users list response."""
    return {
        'entry': [
            {
                'name': 'admin',
                'content': {
                    'realname': 'Administrator',
                    'email': 'admin@example.com',
                    'roles': ['admin'],
                    'defaultApp': 'search',
                }
            },
            {
                'name': 'analyst',
                'content': {
                    'realname': 'Security Analyst',
                    'email': 'analyst@example.com',
                    'roles': ['user'],
                    'defaultApp': 'search',
                }
            },
        ]
    }


@pytest.fixture
def sample_roles_response():
    """Sample roles list response."""
    return {
        'entry': [
            {
                'name': 'admin',
                'content': {
                    'capabilities': ['admin_all_objects', 'change_own_password'],
                    'imported_roles': ['power', 'user'],
                    'srchFilter': None,
                }
            },
            {
                'name': 'user',
                'content': {
                    'capabilities': ['change_own_password', 'search'],
                    'imported_roles': [],
                    'srchFilter': 'index=main',
                }
            },
        ]
    }
