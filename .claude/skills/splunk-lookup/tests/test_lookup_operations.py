#!/usr/bin/env python3
"""Unit tests for lookup operations."""

import sys
from pathlib import Path
from unittest.mock import patch, Mock, mock_open
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)


class TestGetLookup:
    """Tests for get_lookup script."""

    @patch("get_lookup.get_splunk_client")
    @patch("get_lookup.format_table")
    @patch("get_lookup.print_success")
    def test_get_lookup_text_output(
        self,
        mock_print,
        mock_format,
        mock_get_client,
        mock_splunk_client,
        sample_single_lookup,
    ):
        """Test getting a lookup with text output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_single_lookup
        mock_format.return_value = "formatted table"

        from get_lookup import main

        with patch("sys.argv", ["get_lookup.py", "users.csv"]):
            main()

        mock_splunk_client.get.assert_called_once()

    @patch("get_lookup.get_splunk_client")
    @patch("get_lookup.format_json")
    def test_get_lookup_json_output(
        self,
        mock_format_json,
        mock_get_client,
        mock_splunk_client,
        sample_single_lookup,
    ):
        """Test getting a lookup with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_single_lookup
        mock_format_json.return_value = "{}"

        from get_lookup import main

        with patch("sys.argv", ["get_lookup.py", "users.csv", "--output", "json"]):
            main()

        mock_format_json.assert_called_once()

    @patch("get_lookup.get_splunk_client")
    @patch("get_lookup.format_table")
    @patch("get_lookup.print_success")
    def test_get_lookup_specific_app(
        self,
        mock_print,
        mock_format,
        mock_get_client,
        mock_splunk_client,
        sample_single_lookup,
    ):
        """Test getting a lookup from specific app."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_single_lookup
        mock_format.return_value = "formatted table"

        from get_lookup import main

        with patch("sys.argv", ["get_lookup.py", "users.csv", "--app", "myapp"]):
            main()

        call_args = mock_splunk_client.get.call_args
        assert "myapp" in call_args[0][0]


class TestUploadLookup:
    """Tests for upload_lookup script."""

    @patch("upload_lookup.get_splunk_client")
    @patch("upload_lookup.print_success")
    @patch(
        "builtins.open", mock_open(read_data="username,email\nadmin,admin@example.com")
    )
    @patch("upload_lookup.Path")
    def test_upload_lookup_basic(
        self, mock_path, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test uploading a lookup file."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {}
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = True
        mock_path_instance.name = "users.csv"
        mock_path.return_value = mock_path_instance

        from upload_lookup import main

        with patch("sys.argv", ["upload_lookup.py", "/path/to/users.csv"]):
            main()

        mock_splunk_client.post.assert_called_once()


class TestDownloadLookup:
    """Tests for download_lookup script."""

    @patch("download_lookup.get_splunk_client")
    @patch("download_lookup.print_success")
    @patch("builtins.open", mock_open())
    def test_download_lookup_basic(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test downloading a lookup file."""
        # Mock the session.get response
        mock_response = Mock()
        mock_response.text = "username,email\nadmin,admin@example.com"
        mock_response.raise_for_status = Mock()
        mock_splunk_client.session = Mock()
        mock_splunk_client.session.get.return_value = mock_response
        mock_splunk_client.base_url = "https://splunk.example.com:8089/services"
        mock_splunk_client.verify_ssl = True
        mock_get_client.return_value = mock_splunk_client

        from download_lookup import main

        with patch(
            "sys.argv",
            ["download_lookup.py", "users.csv", "--output", "/tmp/users.csv"],
        ):
            main()

        mock_splunk_client.session.get.assert_called_once()


class TestDeleteLookup:
    """Tests for delete_lookup script."""

    @patch("delete_lookup.get_splunk_client")
    @patch("delete_lookup.print_success")
    def test_delete_lookup_with_force(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test deleting a lookup with force flag."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.delete.return_value = {}

        from delete_lookup import main

        with patch("sys.argv", ["delete_lookup.py", "users.csv", "--force"]):
            main()

        mock_splunk_client.delete.assert_called_once()

    @patch("delete_lookup.get_splunk_client")
    @patch("delete_lookup.print_warning")
    @patch("builtins.input", return_value="DELETE")
    @patch("delete_lookup.print_success")
    def test_delete_lookup_with_confirmation(
        self, mock_print, mock_input, mock_warn, mock_get_client, mock_splunk_client
    ):
        """Test deleting a lookup with confirmation."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.delete.return_value = {}

        from delete_lookup import main

        with patch("sys.argv", ["delete_lookup.py", "users.csv"]):
            main()

        mock_splunk_client.delete.assert_called_once()

    @patch("delete_lookup.get_splunk_client")
    @patch("delete_lookup.print_warning")
    @patch("builtins.input", return_value="NO")
    def test_delete_lookup_cancelled(
        self, mock_input, mock_warn, mock_get_client, mock_splunk_client
    ):
        """Test cancelling lookup deletion."""
        mock_get_client.return_value = mock_splunk_client

        from delete_lookup import main

        with patch("sys.argv", ["delete_lookup.py", "users.csv"]):
            main()

        mock_splunk_client.delete.assert_not_called()
