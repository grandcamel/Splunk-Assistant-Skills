#!/usr/bin/env python3
"""Unit tests for KV Store record operations (insert, get, update, delete)."""

import sys
from pathlib import Path
from unittest.mock import patch, Mock
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)


class TestInsertRecord:
    """Tests for insert_record script."""

    @patch("insert_record.get_splunk_client")
    @patch("insert_record.print_success")
    def test_insert_record_basic(self, mock_print, mock_get_client, mock_splunk_client):
        """Test inserting a basic record."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {"_key": "new_key"}

        from insert_record import main

        with patch(
            "sys.argv",
            [
                "insert_record.py",
                "test_collection",
                '{"username": "test", "email": "test@example.com"}',
            ],
        ):
            main()

        mock_splunk_client.post.assert_called_once()

    @patch("insert_record.get_splunk_client")
    @patch("insert_record.print_success")
    def test_insert_record_with_key(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test inserting a record with specific key."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {"_key": "my_key"}

        from insert_record import main

        with patch(
            "sys.argv",
            [
                "insert_record.py",
                "test_collection",
                '{"username": "test"}',
                "--key",
                "my_key",
            ],
        ):
            main()

        mock_splunk_client.post.assert_called_once()


class TestGetRecord:
    """Tests for get_record script."""

    @patch("get_record.get_splunk_client")
    @patch("get_record.format_json")
    @patch("get_record.print_success")
    def test_get_record_basic(
        self,
        mock_print,
        mock_format_json,
        mock_get_client,
        mock_splunk_client,
        sample_single_record,
    ):
        """Test getting a record."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_single_record
        mock_format_json.return_value = "{}"

        from get_record import main

        with patch("sys.argv", ["get_record.py", "test_collection", "user1"]):
            main()

        mock_splunk_client.get.assert_called_once()
        assert "user1" in mock_splunk_client.get.call_args[0][0]
        mock_format_json.assert_called_once()

    @patch("get_record.get_splunk_client")
    @patch("get_record.format_json")
    @patch("get_record.print_success")
    def test_get_record_specific_app(
        self,
        mock_print,
        mock_format_json,
        mock_get_client,
        mock_splunk_client,
        sample_single_record,
    ):
        """Test getting a record from specific app."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_single_record
        mock_format_json.return_value = "{}"

        from get_record import main

        with patch(
            "sys.argv", ["get_record.py", "test_collection", "user1", "--app", "myapp"]
        ):
            main()

        call_args = mock_splunk_client.get.call_args
        assert "myapp" in call_args[0][0]


class TestUpdateRecord:
    """Tests for update_record script."""

    @patch("update_record.get_splunk_client")
    @patch("update_record.print_success")
    def test_update_record_basic(self, mock_print, mock_get_client, mock_splunk_client):
        """Test updating a record."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {"_key": "user1"}

        from update_record import main

        with patch(
            "sys.argv",
            [
                "update_record.py",
                "test_collection",
                "user1",
                '{"email": "newemail@example.com"}',
            ],
        ):
            main()

        mock_splunk_client.post.assert_called_once()
        assert "user1" in mock_splunk_client.post.call_args[0][0]


class TestDeleteRecord:
    """Tests for delete_record script."""

    @patch("delete_record.get_splunk_client")
    @patch("delete_record.print_success")
    def test_delete_record_basic(self, mock_print, mock_get_client, mock_splunk_client):
        """Test deleting a record."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.delete.return_value = {}

        from delete_record import main

        with patch("sys.argv", ["delete_record.py", "test_collection", "user1"]):
            main()

        mock_splunk_client.delete.assert_called_once()
        assert "user1" in mock_splunk_client.delete.call_args[0][0]

    @patch("delete_record.get_splunk_client")
    @patch("delete_record.print_success")
    def test_delete_record_specific_app(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test deleting a record from specific app."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.delete.return_value = {}

        from delete_record import main

        with patch(
            "sys.argv",
            ["delete_record.py", "test_collection", "user1", "--app", "myapp"],
        ):
            main()

        call_args = mock_splunk_client.delete.call_args
        assert "myapp" in call_args[0][0]

    @patch("delete_record.get_splunk_client")
    @patch("delete_record.print_success")
    def test_delete_record_with_profile(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test deleting a record with profile."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.delete.return_value = {}

        from delete_record import main

        with patch(
            "sys.argv",
            ["delete_record.py", "test_collection", "user1", "--profile", "prod"],
        ):
            main()

        mock_get_client.assert_called_once_with(profile="prod")
