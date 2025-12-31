#!/usr/bin/env python3
"""Unit tests for security operations."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestGetCurrentUser:
    """Tests for get_current_user script."""

    @patch("get_current_user.get_splunk_client")
    @patch("get_current_user.format_table")
    @patch("get_current_user.print_success")
    def test_get_current_user_text_output(
        self,
        mock_print,
        mock_format,
        mock_get_client,
        mock_splunk_client,
        sample_current_user_response,
    ):
        """Test getting current user with text output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_current_user_response
        mock_format.return_value = "formatted table"

        from get_current_user import main

        with patch("sys.argv", ["get_current_user.py"]):
            main()

        mock_splunk_client.get.assert_called_once()
        assert "current-context" in mock_splunk_client.get.call_args[0][0]

    @patch("get_current_user.get_splunk_client")
    @patch("get_current_user.format_json")
    def test_get_current_user_json_output(
        self,
        mock_format_json,
        mock_get_client,
        mock_splunk_client,
        sample_current_user_response,
    ):
        """Test getting current user with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_current_user_response
        mock_format_json.return_value = "{}"

        from get_current_user import main

        with patch("sys.argv", ["get_current_user.py", "--output", "json"]):
            main()

        mock_format_json.assert_called_once()


class TestListUsers:
    """Tests for list_users script."""

    @patch("list_users.get_splunk_client")
    @patch("list_users.format_table")
    @patch("list_users.print_success")
    def test_list_users_text_output(
        self,
        mock_print,
        mock_format,
        mock_get_client,
        mock_splunk_client,
        sample_users_response,
    ):
        """Test listing users with text output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_users_response
        mock_format.return_value = "formatted table"

        from list_users import main

        with patch("sys.argv", ["list_users.py"]):
            main()

        mock_splunk_client.get.assert_called_once()
        assert "authentication/users" in mock_splunk_client.get.call_args[0][0]

    @patch("list_users.get_splunk_client")
    @patch("list_users.format_json")
    def test_list_users_json_output(
        self,
        mock_format_json,
        mock_get_client,
        mock_splunk_client,
        sample_users_response,
    ):
        """Test listing users with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_users_response
        mock_format_json.return_value = "[]"

        from list_users import main

        with patch("sys.argv", ["list_users.py", "--output", "json"]):
            main()

        mock_format_json.assert_called_once()

    @patch("list_users.get_splunk_client")
    @patch("list_users.format_table")
    @patch("list_users.print_success")
    def test_list_users_with_count(
        self,
        mock_print,
        mock_format,
        mock_get_client,
        mock_splunk_client,
        sample_users_response,
    ):
        """Test listing users with count limit."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_users_response
        mock_format.return_value = "formatted table"

        from list_users import main

        with patch("sys.argv", ["list_users.py", "--count", "50"]):
            main()

        call_args = mock_splunk_client.get.call_args
        params = call_args[1].get("params", {})
        assert params.get("count") == 50


class TestListRoles:
    """Tests for list_roles script."""

    @patch("list_roles.get_splunk_client")
    @patch("list_roles.format_table")
    @patch("list_roles.print_success")
    def test_list_roles_text_output(
        self,
        mock_print,
        mock_format,
        mock_get_client,
        mock_splunk_client,
        sample_roles_response,
    ):
        """Test listing roles with text output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_roles_response
        mock_format.return_value = "formatted table"

        from list_roles import main

        with patch("sys.argv", ["list_roles.py"]):
            main()

        mock_splunk_client.get.assert_called_once()
        assert "authorization/roles" in mock_splunk_client.get.call_args[0][0]

    @patch("list_roles.get_splunk_client")
    @patch("list_roles.format_json")
    def test_list_roles_json_output(
        self,
        mock_format_json,
        mock_get_client,
        mock_splunk_client,
        sample_roles_response,
    ):
        """Test listing roles with JSON output."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = sample_roles_response
        mock_format_json.return_value = "[]"

        from list_roles import main

        with patch("sys.argv", ["list_roles.py", "--output", "json"]):
            main()

        mock_format_json.assert_called_once()

    @patch("list_roles.get_splunk_client")
    @patch("list_roles.print_success")
    def test_list_roles_empty(self, mock_print, mock_get_client, mock_splunk_client):
        """Test listing when no roles exist."""
        mock_get_client.return_value = mock_splunk_client
        mock_splunk_client.get.return_value = {"entry": []}

        from list_roles import main

        with patch("sys.argv", ["list_roles.py"]):
            main()

        mock_splunk_client.get.assert_called_once()
