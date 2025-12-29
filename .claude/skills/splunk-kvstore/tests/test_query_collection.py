#!/usr/bin/env python3
"""Unit tests for query_collection.py."""

import sys
from pathlib import Path
from unittest.mock import patch, Mock
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))


class TestQueryCollection:
    """Tests for query_collection script."""

    @patch('query_collection.get_splunk_client')
    @patch('query_collection.print_success')
    @patch('query_collection.format_table')
    def test_query_collection_no_filter(self, mock_format, mock_print, mock_get_client,
                                         mock_splunk_client, sample_records_response):
        """Test querying collection without filter."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_records_response
        mock_format.return_value = "formatted table"

        from query_collection import main

        with patch('sys.argv', ['query_collection.py', 'test_collection']):
            main()

        mock_splunk_client.get.assert_called_once()

    @patch('query_collection.get_splunk_client')
    @patch('query_collection.format_json')
    def test_query_collection_json_output(self, mock_format_json, mock_get_client,
                                           mock_splunk_client, sample_records_response):
        """Test querying collection with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_records_response
        mock_format_json.return_value = '[]'

        from query_collection import main

        with patch('sys.argv', ['query_collection.py', 'test_collection', '--output', 'json']):
            main()

        mock_format_json.assert_called_once()

    @patch('query_collection.get_splunk_client')
    @patch('query_collection.print_success')
    def test_query_collection_with_filter(self, mock_print, mock_get_client, mock_splunk_client):
        """Test querying collection with query filter."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = []

        from query_collection import main

        with patch('sys.argv', ['query_collection.py', 'test_collection',
                                '--filter', '{"username": "admin"}']):
            main()

        call_args = mock_splunk_client.get.call_args
        assert 'query' in call_args[1].get('params', {})

    @patch('query_collection.get_splunk_client')
    @patch('query_collection.print_success')
    def test_query_collection_with_limit(self, mock_print, mock_get_client, mock_splunk_client):
        """Test querying collection with limit."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = []

        from query_collection import main

        with patch('sys.argv', ['query_collection.py', 'test_collection', '--limit', '10']):
            main()

        call_args = mock_splunk_client.get.call_args
        params = call_args[1].get('params', {})
        assert params.get('limit') == 10

    @patch('query_collection.get_splunk_client')
    @patch('query_collection.print_success')
    def test_query_collection_with_fields(self, mock_print, mock_get_client, mock_splunk_client):
        """Test querying collection with specific fields."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = []

        from query_collection import main

        with patch('sys.argv', ['query_collection.py', 'test_collection',
                                '--fields', 'username,email']):
            main()

        mock_splunk_client.get.assert_called_once()
