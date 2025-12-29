#!/usr/bin/env python3
"""Unit tests for create_collection.py."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts" / "lib")
)


class TestCreateCollection:
    """Tests for create_collection script."""

    @patch("create_collection.get_splunk_client")
    @patch("create_collection.print_success")
    def test_create_collection_basic(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test creating a basic collection."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {}

        from create_collection import main

        with patch("sys.argv", ["create_collection.py", "test_collection"]):
            main()

        mock_splunk_client.post.assert_called_once()
        call_args = mock_splunk_client.post.call_args
        assert "test_collection" in str(call_args)

    @patch("create_collection.get_splunk_client")
    @patch("create_collection.print_success")
    def test_create_collection_with_app(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test creating a collection in specific app."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {}

        from create_collection import main

        with patch(
            "sys.argv", ["create_collection.py", "test_collection", "--app", "myapp"]
        ):
            main()

        call_args = mock_splunk_client.post.call_args
        assert "myapp" in call_args[0][0]

    @patch("create_collection.get_splunk_client")
    @patch("create_collection.print_success")
    def test_create_collection_with_fields(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test creating a collection with field definitions."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {}

        from create_collection import main

        with patch(
            "sys.argv",
            [
                "create_collection.py",
                "test_collection",
                "--fields",
                '{"name": "string", "count": "number"}',
            ],
        ):
            main()

        mock_splunk_client.post.assert_called()
        call_args = mock_splunk_client.post.call_args
        data = call_args[1].get("data", {})
        assert data.get("field.name") == "string"

    @patch("create_collection.get_splunk_client")
    @patch("create_collection.print_success")
    def test_create_collection_with_accelerated_fields(
        self, mock_print, mock_get_client, mock_splunk_client
    ):
        """Test creating a collection with accelerated fields."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.post.return_value = {}

        from create_collection import main

        with patch(
            "sys.argv",
            [
                "create_collection.py",
                "test_collection",
                "--accelerated-fields",
                '{"idx1": {"name": 1}}',
            ],
        ):
            main()

        mock_splunk_client.post.assert_called()
