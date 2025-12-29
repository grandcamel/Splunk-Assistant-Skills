#!/usr/bin/env python3
"""Unit tests for list_collections.py."""

import sys
from pathlib import Path
from unittest.mock import patch, Mock
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared' / 'scripts' / 'lib'))


class TestListCollections:
    """Tests for list_collections script."""

    @patch('list_collections.get_splunk_client')
    @patch('list_collections.print_success')
    @patch('list_collections.format_table')
    def test_list_collections_text_output(self, mock_format, mock_print, mock_get_client,
                                           mock_splunk_client, sample_collections_response, capsys):
        """Test listing collections with text output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_collections_response
        mock_format.return_value = "formatted table"

        from list_collections import main

        with patch('sys.argv', ['list_collections.py']):
            main()

        mock_splunk_client.get.assert_called_once()
        assert '/storage/collections/config' in mock_splunk_client.get.call_args[0][0]

    @patch('list_collections.get_splunk_client')
    @patch('list_collections.format_json')
    def test_list_collections_json_output(self, mock_format_json, mock_get_client,
                                           mock_splunk_client, sample_collections_response, capsys):
        """Test listing collections with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_collections_response
        mock_format_json.return_value = '[]'

        from list_collections import main

        with patch('sys.argv', ['list_collections.py', '--output', 'json']):
            main()

        mock_format_json.assert_called_once()

    @patch('list_collections.get_splunk_client')
    def test_list_collections_with_app_filter(self, mock_get_client, mock_splunk_client):
        """Test listing collections filtered by app."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = {'entry': []}

        from list_collections import main

        with patch('sys.argv', ['list_collections.py', '--app', 'myapp']):
            main()

        call_args = mock_splunk_client.get.call_args
        assert 'myapp' in call_args[0][0]

    @patch('list_collections.get_splunk_client')
    def test_list_collections_empty(self, mock_get_client, mock_splunk_client, capsys):
        """Test listing when no collections exist."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = {'entry': []}

        from list_collections import main

        with patch('sys.argv', ['list_collections.py']):
            main()

        mock_splunk_client.get.assert_called_once()
