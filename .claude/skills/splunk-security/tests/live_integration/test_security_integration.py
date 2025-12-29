#!/usr/bin/env python3
"""Live Integration Tests for splunk-security skill."""

import pytest


class TestUserOperations:
    """Integration tests for user operations."""

    @pytest.mark.live
    def test_get_current_user(self, splunk_client):
        """Test getting current user context."""
        response = splunk_client.get(
            "/services/authentication/current-context",
            operation="get current user"
        )

        assert "entry" in response
        content = response["entry"][0].get("content", {})
        assert "username" in content
        assert "roles" in content

    @pytest.mark.live
    def test_list_users(self, splunk_client):
        """Test listing users."""
        response = splunk_client.get(
            "/services/authentication/users",
            params={"output_mode": "json"},
            operation="list users"
        )

        assert "entry" in response
        # Should have at least the admin user
        usernames = [e.get("name") for e in response.get("entry", [])]
        assert "admin" in usernames

    @pytest.mark.live
    def test_get_user_details(self, splunk_client):
        """Test getting specific user details."""
        response = splunk_client.get(
            "/services/authentication/users/admin",
            operation="get user"
        )

        assert "entry" in response
        content = response["entry"][0].get("content", {})
        assert "roles" in content


class TestRoleOperations:
    """Integration tests for role operations."""

    @pytest.mark.live
    def test_list_roles(self, splunk_client):
        """Test listing roles."""
        response = splunk_client.get(
            "/services/authorization/roles",
            params={"output_mode": "json"},
            operation="list roles"
        )

        assert "entry" in response
        # Should have standard roles
        role_names = [e.get("name") for e in response.get("entry", [])]
        assert "admin" in role_names
        assert "user" in role_names

    @pytest.mark.live
    def test_get_role_details(self, splunk_client):
        """Test getting specific role details."""
        response = splunk_client.get(
            "/services/authorization/roles/admin",
            operation="get role"
        )

        assert "entry" in response
        content = response["entry"][0].get("content", {})
        assert "capabilities" in content


class TestCapabilities:
    """Integration tests for capabilities."""

    @pytest.mark.live
    def test_list_capabilities(self, splunk_client):
        """Test listing capabilities."""
        response = splunk_client.get(
            "/services/authorization/capabilities",
            params={"output_mode": "json"},
            operation="list capabilities"
        )

        assert "entry" in response
        # Should have at least one entry with capabilities list
        entry = response.get("entry", [{}])[0]
        capabilities = entry.get("content", {}).get("capabilities", [])
        assert len(capabilities) > 10
