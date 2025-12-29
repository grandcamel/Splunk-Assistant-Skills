#!/usr/bin/env python3
"""Unit tests for saved search operations."""

import sys
from pathlib import Path
from unittest.mock import patch, Mock
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)


class TestGetSavedsearch:
    """Tests for get_savedsearch script."""

    @patch("get_savedsearch.get_splunk_client")
    @patch("get_savedsearch.format_table")
    @patch("get_savedsearch.print_success")
    def test_get_savedsearch_text_output(
        self,
        mock_print,
        mock_format,
        mock_get_client,
        mock_splunk_client,
        sample_single_savedsearch,
    ):
        """Test getting a saved search with text output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_single_savedsearch
        mock_format.return_value = "formatted table"

        from get_savedsearch import main

        with patch("sys.argv", ["get_savedsearch.py", "Daily Error Report"]):
            main()

        mock_splunk_client.get.assert_called_once()

    @patch("get_savedsearch.get_splunk_client")
    @patch("get_savedsearch.format_json")
    def test_get_savedsearch_json_output(
        self,
        mock_format_json,
        mock_get_client,
        mock_splunk_client,
        sample_single_savedsearch,
    ):
        """Test getting a saved search with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_single_savedsearch
        mock_format_json.return_value = "{}"

        from get_savedsearch import main

        with patch(
            "sys.argv", ["get_savedsearch.py", "Daily Error Report", "--output", "json"]
        ):
            main()

        mock_format_json.assert_called_once()


class TestCreateSavedsearch:
    """Tests for create_savedsearch script."""

    @patch("create_savedsearch.get_splunk_client")
    @patch("create_savedsearch.print_success")
    def test_create_savedsearch_basic(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test creating a basic saved search."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {}

        from create_savedsearch import main

        with patch(
            "sys.argv", ["create_savedsearch.py", "Test Search", "index=main | head 10"]
        ):
            main()

        mock_splunk_client.post.assert_called_once()

    @patch("create_savedsearch.get_splunk_client")
    @patch("create_savedsearch.print_success")
    def test_create_savedsearch_scheduled(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test creating a scheduled saved search."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {}

        from create_savedsearch import main

        with patch(
            "sys.argv",
            [
                "create_savedsearch.py",
                "Scheduled Search",
                "index=main | stats count",
                "--cron",
                "0 6 * * *",
                "--description",
                "Daily report",
            ],
        ):
            main()

        call_args = mock_splunk_client.post.call_args
        data = call_args[1].get("data", {})
        assert data.get("cron_schedule") == "0 6 * * *"


class TestUpdateSavedsearch:
    """Tests for update_savedsearch script."""

    @patch("update_savedsearch.get_splunk_client")
    @patch("update_savedsearch.print_success")
    def test_update_savedsearch_search(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test updating saved search query."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {}

        from update_savedsearch import main

        with patch(
            "sys.argv",
            [
                "update_savedsearch.py",
                "Test Search",
                "--search",
                "index=main | head 20",
            ],
        ):
            main()

        mock_splunk_client.post.assert_called_once()

    @patch("update_savedsearch.get_splunk_client")
    @patch("update_savedsearch.print_success")
    def test_update_savedsearch_disable(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test disabling a saved search."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {}

        from update_savedsearch import main

        with patch("sys.argv", ["update_savedsearch.py", "Test Search", "--disable"]):
            main()

        call_args = mock_splunk_client.post.call_args
        data = call_args[1].get("data", {})
        assert data.get("disabled") == "1"


class TestDeleteSavedsearch:
    """Tests for delete_savedsearch script."""

    @patch("delete_savedsearch.get_splunk_client")
    @patch("delete_savedsearch.print_success")
    def test_delete_savedsearch_with_force(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test deleting a saved search with force flag."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.delete.return_value = {}

        from delete_savedsearch import main

        with patch("sys.argv", ["delete_savedsearch.py", "Test Search", "--force"]):
            main()

        mock_splunk_client.delete.assert_called_once()

    @patch("delete_savedsearch.get_splunk_client")
    @patch("delete_savedsearch.print_warning")
    @patch("builtins.input", return_value="NO")
    def test_delete_savedsearch_cancelled(
        self, mock_input, mock_warn, mock_get_client, mock_splunk_client
    ):
        """Test cancelling saved search deletion."""
        mock_get_client.return_value = mock_splunk_client

        from delete_savedsearch import main

        with patch("sys.argv", ["delete_savedsearch.py", "Test Search"]):
            main()

        mock_splunk_client.delete.assert_not_called()


class TestRunSavedsearch:
    """Tests for run_savedsearch script."""

    @patch("run_savedsearch.get_splunk_client")
    @patch("run_savedsearch.print_success")
    def test_run_savedsearch_basic(
        self, mock_print, mock_get_client, mock_splunk_client, sample_dispatch_response
    ):
        """Test running a saved search."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = sample_dispatch_response

        from run_savedsearch import main

        with patch("sys.argv", ["run_savedsearch.py", "Daily Error Report"]):
            main()

        mock_splunk_client.post.assert_called_once()
        assert "dispatch" in mock_splunk_client.post.call_args[0][0]

    @patch("run_savedsearch.get_splunk_client")
    @patch("run_savedsearch.print_success")
    def test_run_savedsearch_with_time_range(
        self, mock_print, mock_get_client, mock_splunk_client, sample_dispatch_response
    ):
        """Test running a saved search with custom time range."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = sample_dispatch_response

        from run_savedsearch import main

        with patch(
            "sys.argv",
            [
                "run_savedsearch.py",
                "Daily Error Report",
                "--earliest",
                "-7d",
                "--latest",
                "now",
            ],
        ):
            main()

        call_args = mock_splunk_client.post.call_args
        data = call_args[1].get("data", {})
        assert data.get("dispatch.earliest_time") == "-7d"
