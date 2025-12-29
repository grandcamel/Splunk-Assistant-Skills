#!/usr/bin/env python3
"""Unit tests for alert operations."""

import sys
from pathlib import Path
from unittest.mock import patch, Mock
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)


class TestListAlerts:
    """Tests for list_alerts script."""

    @patch("list_alerts.get_splunk_client")
    @patch("list_alerts.format_table")
    @patch("list_alerts.print_success")
    def test_list_alerts_text_output(
        self,
        mock_print,
        mock_format,
        mock_get_client,
        mock_splunk_client,
        sample_alerts_response,
    ):
        """Test listing alerts with text output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_alerts_response
        mock_format.return_value = "formatted table"

        from list_alerts import main

        with patch("sys.argv", ["list_alerts.py"]):
            main()

        mock_splunk_client.get.assert_called_once()

    @patch("list_alerts.get_splunk_client")
    @patch("list_alerts.format_json")
    def test_list_alerts_json_output(
        self,
        mock_format_json,
        mock_get_client,
        mock_splunk_client,
        sample_alerts_response,
    ):
        """Test listing alerts with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_alerts_response
        mock_format_json.return_value = "[]"

        from list_alerts import main

        with patch("sys.argv", ["list_alerts.py", "--output", "json"]):
            main()

        mock_format_json.assert_called_once()

    @patch("list_alerts.get_splunk_client")
    @patch("list_alerts.format_table")
    @patch("list_alerts.print_success")
    def test_list_alerts_with_severity_filter(
        self,
        mock_print,
        mock_format,
        mock_get_client,
        mock_splunk_client,
        sample_alerts_response,
    ):
        """Test listing alerts filtered by severity."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_alerts_response
        mock_format.return_value = "formatted table"

        from list_alerts import main

        with patch("sys.argv", ["list_alerts.py", "--severity", "4"]):
            main()

        mock_splunk_client.get.assert_called_once()

    @patch("list_alerts.get_splunk_client")
    @patch("list_alerts.print_success")
    def test_list_alerts_empty(self, mock_print, mock_get_client, mock_splunk_client):
        """Test listing when no alerts exist."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = {"entry": []}

        from list_alerts import main

        with patch("sys.argv", ["list_alerts.py"]):
            main()

        mock_splunk_client.get.assert_called_once()


class TestGetAlert:
    """Tests for get_alert script."""

    @patch("get_alert.get_splunk_client")
    @patch("get_alert.format_table")
    @patch("get_alert.print_success")
    def test_get_alert_text_output(
        self,
        mock_print,
        mock_format,
        mock_get_client,
        mock_splunk_client,
        sample_single_alert,
    ):
        """Test getting an alert with text output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_single_alert
        mock_format.return_value = "formatted table"

        from get_alert import main

        with patch("sys.argv", ["get_alert.py", "Alert_1"]):
            main()

        mock_splunk_client.get.assert_called_once()
        assert "Alert_1" in mock_splunk_client.get.call_args[0][0]

    @patch("get_alert.get_splunk_client")
    @patch("get_alert.format_json")
    def test_get_alert_json_output(
        self, mock_format_json, mock_get_client, mock_splunk_client, sample_single_alert
    ):
        """Test getting an alert with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_single_alert
        mock_format_json.return_value = "{}"

        from get_alert import main

        with patch("sys.argv", ["get_alert.py", "Alert_1", "--output", "json"]):
            main()

        mock_format_json.assert_called_once()


class TestAcknowledgeAlert:
    """Tests for acknowledge_alert script."""

    @patch("acknowledge_alert.get_splunk_client")
    @patch("acknowledge_alert.print_success")
    def test_acknowledge_alert_with_force(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test acknowledging an alert with force flag."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.delete.return_value = {}

        from acknowledge_alert import main

        with patch("sys.argv", ["acknowledge_alert.py", "Alert_1", "--force"]):
            main()

        mock_splunk_client.delete.assert_called_once()
        assert "Alert_1" in mock_splunk_client.delete.call_args[0][0]

    @patch("acknowledge_alert.get_splunk_client")
    @patch("acknowledge_alert.print_warning")
    @patch("builtins.input", return_value="YES")
    @patch("acknowledge_alert.print_success")
    def test_acknowledge_alert_with_confirmation(
        self, mock_print, mock_input, mock_warn, mock_get_client, mock_splunk_client
    ):
        """Test acknowledging an alert with confirmation."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.delete.return_value = {}

        from acknowledge_alert import main

        with patch("sys.argv", ["acknowledge_alert.py", "Alert_1"]):
            main()

        mock_splunk_client.delete.assert_called_once()

    @patch("acknowledge_alert.get_splunk_client")
    @patch("acknowledge_alert.print_warning")
    @patch("builtins.input", return_value="NO")
    def test_acknowledge_alert_cancelled(
        self, mock_input, mock_warn, mock_get_client, mock_splunk_client
    ):
        """Test cancelling alert acknowledgement."""
        mock_get_client.return_value = mock_splunk_client

        from acknowledge_alert import main

        with patch("sys.argv", ["acknowledge_alert.py", "Alert_1"]):
            main()

        mock_splunk_client.delete.assert_not_called()
