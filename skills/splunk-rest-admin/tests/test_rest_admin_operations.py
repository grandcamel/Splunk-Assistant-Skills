#!/usr/bin/env python3
"""Unit tests for REST admin operations."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestGetServerInfo:
    """Tests for get_server_info script."""

    @patch("get_server_info.get_splunk_client")
    @patch("get_server_info.print_success")
    def test_get_server_info_text_output(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test getting server info with text output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get_server_info.return_value = {
            "serverName": "splunk-server",
            "version": "9.1.2",
            "build": "12345",
            "os_name": "Linux",
            "os_version": "5.4.0",
            "licenseState": "OK",
            "serverRoles": ["search_head"],
        }

        from get_server_info import main

        with patch("sys.argv", ["get_server_info.py"]):
            main()

        mock_splunk_client.get_server_info.assert_called_once()

    @patch("get_server_info.get_splunk_client")
    @patch("get_server_info.format_json")
    def test_get_server_info_json_output(
        self, mock_format_json, mock_get_client, mock_splunk_client
    ):
        """Test getting server info with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get_server_info.return_value = {
            "serverName": "splunk-server",
            "version": "9.1.2",
        }
        mock_format_json.return_value = "{}"

        from get_server_info import main

        with patch("sys.argv", ["get_server_info.py", "--output", "json"]):
            main()

        mock_format_json.assert_called_once()


class TestGetServerStatus:
    """Tests for get_server_status script."""

    @patch("get_server_status.get_splunk_client")
    @patch("get_server_status.format_table")
    @patch("get_server_status.print_success")
    def test_get_server_status_text_output(
        self,
        mock_print,
        mock_format,
        mock_get_client,
        mock_splunk_client,
        sample_server_status_response,
    ):
        """Test getting server status with text output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_server_status_response
        mock_format.return_value = "formatted table"

        from get_server_status import main

        with patch("sys.argv", ["get_server_status.py"]):
            main()

        mock_splunk_client.get.assert_called_once()
        assert "server/status" in mock_splunk_client.get.call_args[0][0]

    @patch("get_server_status.get_splunk_client")
    @patch("get_server_status.format_json")
    def test_get_server_status_json_output(
        self,
        mock_format_json,
        mock_get_client,
        mock_splunk_client,
        sample_server_status_response,
    ):
        """Test getting server status with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_server_status_response
        mock_format_json.return_value = "{}"

        from get_server_status import main

        with patch("sys.argv", ["get_server_status.py", "--output", "json"]):
            main()

        mock_format_json.assert_called_once()


class TestGetServerHealth:
    """Tests for get_server_health script."""

    @patch("get_server_health.get_splunk_client")
    @patch("get_server_health.format_table")
    @patch("get_server_health.print_success")
    def test_get_server_health_text_output(
        self,
        mock_print,
        mock_format,
        mock_get_client,
        mock_splunk_client,
        sample_server_health_response,
    ):
        """Test getting server health with text output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_server_health_response
        mock_format.return_value = "formatted table"

        from get_server_health import main

        with patch("sys.argv", ["get_server_health.py"]):
            main()

        mock_splunk_client.get.assert_called_once()
        assert "server/health" in mock_splunk_client.get.call_args[0][0]

    @patch("get_server_health.get_splunk_client")
    @patch("get_server_health.format_json")
    def test_get_server_health_json_output(
        self,
        mock_format_json,
        mock_get_client,
        mock_splunk_client,
        sample_server_health_response,
    ):
        """Test getting server health with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_server_health_response
        mock_format_json.return_value = "{}"

        from get_server_health import main

        with patch("sys.argv", ["get_server_health.py", "--output", "json"]):
            main()

        mock_format_json.assert_called_once()

    @patch("get_server_health.get_splunk_client")
    @patch("get_server_health.format_table")
    @patch("get_server_health.print_success")
    def test_get_server_health_with_features(
        self,
        mock_print,
        mock_format,
        mock_get_client,
        mock_splunk_client,
        sample_server_health_response,
    ):
        """Test getting server health shows feature health."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_server_health_response
        mock_format.return_value = "formatted table"

        from get_server_health import main

        with patch("sys.argv", ["get_server_health.py"]):
            main()

        # Verify format_table was called (health features should be formatted)
        mock_format.assert_called_once()
