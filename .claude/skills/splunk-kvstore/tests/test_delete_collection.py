#!/usr/bin/env python3
"""Unit tests for delete_collection.py."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)


class TestDeleteCollection:
    """Tests for delete_collection script."""

    @patch("delete_collection.get_splunk_client")
    @patch("delete_collection.print_success")
    def test_delete_collection_with_force(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test deleting a collection with force flag."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.delete.return_value = {}

        from delete_collection import main

        with patch("sys.argv", ["delete_collection.py", "test_collection", "--force"]):
            main()

        mock_splunk_client.delete.assert_called_once()
        assert "test_collection" in mock_splunk_client.delete.call_args[0][0]

    @patch("delete_collection.get_splunk_client")
    @patch("delete_collection.print_warning")
    @patch("builtins.input", return_value="DELETE")
    @patch("delete_collection.print_success")
    def test_delete_collection_with_confirmation(
        self, mock_print, mock_input, mock_warn, mock_get_client, mock_splunk_client
    ):
        """Test deleting a collection with confirmation."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.delete.return_value = {}

        from delete_collection import main

        with patch("sys.argv", ["delete_collection.py", "test_collection"]):
            main()

        mock_splunk_client.delete.assert_called_once()

    @patch("delete_collection.get_splunk_client")
    @patch("delete_collection.print_warning")
    @patch("builtins.input", return_value="NO")
    def test_delete_collection_cancelled(
        self, mock_input, mock_warn, mock_get_client, mock_splunk_client
    ):
        """Test cancelling collection deletion."""
        mock_get_client.return_value = mock_splunk_client

        from delete_collection import main

        with patch("sys.argv", ["delete_collection.py", "test_collection"]):
            main()

        mock_splunk_client.delete.assert_not_called()

    @patch("delete_collection.get_splunk_client")
    @patch("delete_collection.print_success")
    def test_delete_collection_specific_app(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test deleting a collection from specific app."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.delete.return_value = {}

        from delete_collection import main

        with patch(
            "sys.argv",
            ["delete_collection.py", "test_collection", "--app", "myapp", "--force"],
        ):
            main()

        call_args = mock_splunk_client.delete.call_args
        assert "myapp" in call_args[0][0]
