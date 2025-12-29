#!/usr/bin/env python3
"""Pytest fixtures for splunk-kvstore tests."""

import sys
from pathlib import Path
from unittest.mock import Mock
import pytest

# Add shared lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))


@pytest.fixture
def mock_splunk_client():
    """Create a mock SplunkClient for testing."""
    client = Mock()
    client.base_url = 'https://splunk.example.com:8089/services'
    client.auth_method = 'bearer'
    client.timeout = 30
    client.get.return_value = {'entry': []}
    client.post.return_value = {}
    client.delete.return_value = {}
    return client


@pytest.fixture
def sample_collections_response():
    """Sample KV Store collections list response."""
    return {
        'entry': [
            {
                'name': 'kv_users',
                'content': {
                    'field.username': 'string',
                    'field.email': 'string',
                    'field.role': 'string',
                }
            },
            {
                'name': 'kv_assets',
                'content': {
                    'field.hostname': 'string',
                    'field.ip': 'string',
                }
            },
        ]
    }


@pytest.fixture
def sample_records_response():
    """Sample KV Store records response."""
    return [
        {'_key': 'user1', 'username': 'admin', 'email': 'admin@example.com'},
        {'_key': 'user2', 'username': 'user', 'email': 'user@example.com'},
    ]


@pytest.fixture
def sample_single_record():
    """Sample single KV Store record."""
    return {'_key': 'user1', 'username': 'admin', 'email': 'admin@example.com', 'role': 'admin'}
