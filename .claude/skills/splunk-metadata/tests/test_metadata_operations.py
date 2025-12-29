#!/usr/bin/env python3
"""Unit tests for metadata operations."""

import sys
from pathlib import Path
from unittest.mock import patch, Mock
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))


class TestGetIndex:
    """Tests for get_index script."""

    @patch('get_index.get_splunk_client')
    @patch('get_index.format_table')
    @patch('get_index.print_success')
    def test_get_index_text_output(self, mock_print, mock_format, mock_get_client,
                                    mock_splunk_client, sample_index_response):
        """Test getting an index with text output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_index_response
        mock_format.return_value = "formatted table"

        from get_index import main

        with patch('sys.argv', ['get_index.py', 'main']):
            main()

        mock_splunk_client.get.assert_called_once()
        assert 'main' in mock_splunk_client.get.call_args[0][0]

    @patch('get_index.get_splunk_client')
    @patch('get_index.format_json')
    def test_get_index_json_output(self, mock_format_json, mock_get_client,
                                    mock_splunk_client, sample_index_response):
        """Test getting an index with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_index_response
        mock_format_json.return_value = '{}'

        from get_index import main

        with patch('sys.argv', ['get_index.py', 'main', '--output', 'json']):
            main()

        mock_format_json.assert_called_once()


class TestCreateIndex:
    """Tests for create_index script."""

    @patch('create_index.get_splunk_client')
    @patch('create_index.print_success')
    def test_create_index_basic(self, mock_print, mock_get_client, mock_splunk_client):
        """Test creating a basic index."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {}

        from create_index import main

        with patch('sys.argv', ['create_index.py', 'new_index']):
            main()

        mock_splunk_client.post.assert_called_once()
        call_args = mock_splunk_client.post.call_args
        data = call_args[1].get('data', {})
        assert data.get('name') == 'new_index'

    @patch('create_index.get_splunk_client')
    @patch('create_index.print_success')
    def test_create_index_metric(self, mock_print, mock_get_client, mock_splunk_client):
        """Test creating a metric index."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {}

        from create_index import main

        with patch('sys.argv', ['create_index.py', 'metric_index', '--datatype', 'metric']):
            main()

        call_args = mock_splunk_client.post.call_args
        data = call_args[1].get('data', {})
        assert data.get('datatype') == 'metric'

    @patch('create_index.get_splunk_client')
    @patch('create_index.print_success')
    def test_create_index_with_size_limit(self, mock_print, mock_get_client, mock_splunk_client):
        """Test creating an index with size limit."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {}

        from create_index import main

        with patch('sys.argv', ['create_index.py', 'sized_index', '--max-size-mb', '10000']):
            main()

        call_args = mock_splunk_client.post.call_args
        data = call_args[1].get('data', {})
        assert data.get('maxTotalDataSizeMB') == 10000


class TestListSourcetypes:
    """Tests for list_sourcetypes script."""

    @patch('list_sourcetypes.get_splunk_client')
    @patch('list_sourcetypes.format_table')
    @patch('list_sourcetypes.print_success')
    def test_list_sourcetypes_text_output(self, mock_print, mock_format, mock_get_client,
                                           mock_splunk_client, sample_sourcetypes_response):
        """Test listing sourcetypes with text output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = sample_sourcetypes_response
        mock_format.return_value = "formatted table"

        from list_sourcetypes import main

        with patch('sys.argv', ['list_sourcetypes.py']):
            main()

        mock_splunk_client.post.assert_called_once()

    @patch('list_sourcetypes.get_splunk_client')
    @patch('list_sourcetypes.format_json')
    def test_list_sourcetypes_json_output(self, mock_format_json, mock_get_client,
                                           mock_splunk_client, sample_sourcetypes_response):
        """Test listing sourcetypes with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = sample_sourcetypes_response
        mock_format_json.return_value = '[]'

        from list_sourcetypes import main

        with patch('sys.argv', ['list_sourcetypes.py', '--output', 'json']):
            main()

        mock_format_json.assert_called_once()

    @patch('list_sourcetypes.get_splunk_client')
    @patch('list_sourcetypes.format_table')
    @patch('list_sourcetypes.print_success')
    def test_list_sourcetypes_with_index_filter(self, mock_print, mock_format, mock_get_client,
                                                 mock_splunk_client, sample_sourcetypes_response):
        """Test listing sourcetypes filtered by index."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = sample_sourcetypes_response
        mock_format.return_value = "formatted table"

        from list_sourcetypes import main

        with patch('sys.argv', ['list_sourcetypes.py', '--index', 'main']):
            main()

        call_args = mock_splunk_client.post.call_args
        data = call_args[1].get('data', {})
        assert 'index=main' in data.get('search', '')
