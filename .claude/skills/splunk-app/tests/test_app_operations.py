#!/usr/bin/env python3
"""Unit tests for app operations."""

import sys
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)


class TestListApps:
    """Tests for list_apps script."""

    @patch("list_apps.get_splunk_client")
    @patch("list_apps.format_table")
    @patch("list_apps.print_success")
    def test_list_apps_text_output(
        self,
        mock_print,
        mock_format,
        mock_get_client,
        mock_splunk_client,
        sample_apps_response,
    ):
        """Test listing apps with text output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_apps_response
        mock_format.return_value = "formatted table"

        from list_apps import main

        with patch("sys.argv", ["list_apps.py"]):
            main()

        mock_splunk_client.get.assert_called_once()
        assert "apps/local" in mock_splunk_client.get.call_args[0][0]

    @patch("list_apps.get_splunk_client")
    @patch("list_apps.format_json")
    def test_list_apps_json_output(
        self,
        mock_format_json,
        mock_get_client,
        mock_splunk_client,
        sample_apps_response,
    ):
        """Test listing apps with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_apps_response
        mock_format_json.return_value = "[]"

        from list_apps import main

        with patch("sys.argv", ["list_apps.py", "--output", "json"]):
            main()

        mock_format_json.assert_called_once()


class TestGetApp:
    """Tests for get_app script."""

    @patch("get_app.get_splunk_client")
    @patch("get_app.format_table")
    @patch("get_app.print_success")
    def test_get_app_text_output(
        self,
        mock_print,
        mock_format,
        mock_get_client,
        mock_splunk_client,
        sample_single_app,
    ):
        """Test getting an app with text output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_single_app
        mock_format.return_value = "formatted table"

        from get_app import main

        with patch("sys.argv", ["get_app.py", "search"]):
            main()

        mock_splunk_client.get.assert_called_once()
        assert "search" in mock_splunk_client.get.call_args[0][0]

    @patch("get_app.get_splunk_client")
    @patch("get_app.format_json")
    def test_get_app_json_output(
        self, mock_format_json, mock_get_client, mock_splunk_client, sample_single_app
    ):
        """Test getting an app with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_single_app
        mock_format_json.return_value = "{}"

        from get_app import main

        with patch("sys.argv", ["get_app.py", "search", "--output", "json"]):
            main()

        mock_format_json.assert_called_once()


class TestInstallApp:
    """Tests for install_app script."""

    @patch("install_app.get_splunk_client")
    @patch("install_app.print_success")
    @patch("install_app.Path")
    @patch("builtins.open", mock_open(read_data=b"fake app content"))
    def test_install_app_from_file_with_force(
        self, mock_path, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test installing an app from file with force flag."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {}

        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = True
        mock_path_instance.name = "myapp.tar.gz"
        mock_path_instance.stem = "myapp.tar"
        mock_path.return_value = mock_path_instance

        from install_app import main

        with patch("sys.argv", ["install_app.py", "/path/to/myapp.tar.gz", "--force"]):
            main()

        mock_splunk_client.post.assert_called_once()

    @patch("install_app.get_splunk_client")
    @patch("install_app.print_warning")
    @patch("builtins.input", return_value="NO")
    @patch("install_app.Path")
    def test_install_app_cancelled(
        self, mock_path, mock_input, mock_warn, mock_get_client, mock_splunk_client
    ):
        """Test cancelling app installation."""
        mock_get_client.return_value = mock_splunk_client

        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = True
        mock_path.return_value = mock_path_instance

        from install_app import main

        with patch("sys.argv", ["install_app.py", "/path/to/myapp.tar.gz"]):
            main()

        mock_splunk_client.post.assert_not_called()

    @patch("install_app.get_splunk_client")
    @patch("install_app.print_warning")
    @patch("install_app.Path")
    def test_install_app_invalid_source(
        self, mock_path, mock_warn, mock_get_client, mock_splunk_client
    ):
        """Test installing from invalid source."""
        mock_get_client.return_value = mock_splunk_client

        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        mock_path_instance.is_file.return_value = False
        mock_path.return_value = mock_path_instance

        from install_app import main

        with patch("sys.argv", ["install_app.py", "invalid_source"]):
            main()

        mock_splunk_client.post.assert_not_called()
