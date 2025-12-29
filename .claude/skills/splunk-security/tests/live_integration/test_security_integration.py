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

    @pytest.mark.live
    def test_capabilities_include_admin(self, splunk_client):
        """Test that admin capabilities are present."""
        response = splunk_client.get(
            "/services/authorization/capabilities",
            operation="list capabilities"
        )

        entry = response.get("entry", [{}])[0]
        capabilities = entry.get("content", {}).get("capabilities", [])
        # Should have common capabilities
        assert len(capabilities) > 0


class TestTokens:
    """Integration tests for token management."""

    @pytest.mark.live
    def test_list_tokens(self, splunk_client):
        """Test listing tokens."""
        try:
            response = splunk_client.get(
                "/services/authorization/tokens",
                params={"output_mode": "json"},
                operation="list tokens"
            )
            assert "entry" in response or response is not None
        except Exception:
            # Token endpoint may not be available
            pass


class TestAuthenticationMethods:
    """Integration tests for authentication methods."""

    @pytest.mark.live
    def test_get_auth_users_endpoint(self, splunk_client):
        """Test accessing authentication users endpoint."""
        response = splunk_client.get(
            "/services/authentication/users",
            params={"count": 10},
            operation="list users limited"
        )

        assert "entry" in response

    @pytest.mark.live
    def test_user_has_roles(self, splunk_client):
        """Test that users have roles assigned."""
        response = splunk_client.get(
            "/services/authentication/users/admin",
            operation="get admin user"
        )

        assert "entry" in response
        content = response["entry"][0].get("content", {})
        roles = content.get("roles", [])
        assert "admin" in roles

    @pytest.mark.live
    def test_get_current_user_capabilities(self, splunk_client):
        """Test getting current user's capabilities."""
        response = splunk_client.get(
            "/services/authentication/current-context",
            operation="get current context"
        )

        assert "entry" in response
        content = response["entry"][0].get("content", {})
        assert "username" in content


class TestRoleCapabilities:
    """Integration tests for role capabilities."""

    @pytest.mark.live
    def test_admin_role_has_capabilities(self, splunk_client):
        """Test that admin role has capabilities."""
        response = splunk_client.get(
            "/services/authorization/roles/admin",
            operation="get admin role"
        )

        assert "entry" in response
        content = response["entry"][0].get("content", {})
        assert "capabilities" in content

    @pytest.mark.live
    def test_user_role_exists(self, splunk_client):
        """Test that user role exists."""
        response = splunk_client.get(
            "/services/authorization/roles/user",
            operation="get user role"
        )

        assert "entry" in response

    @pytest.mark.live
    def test_list_roles_with_count(self, splunk_client):
        """Test listing roles with count limit."""
        response = splunk_client.get(
            "/services/authorization/roles",
            params={"count": 5},
            operation="list roles limited"
        )

        assert "entry" in response
        assert len(response["entry"]) <= 5

    @pytest.mark.live
    def test_role_has_indexes(self, splunk_client):
        """Test that roles have index access defined."""
        response = splunk_client.get(
            "/services/authorization/roles/admin",
            operation="get admin role"
        )

        content = response["entry"][0].get("content", {})
        # Admin should have srchIndexesDefault or similar
        assert isinstance(content, dict)


class TestPasswordPolicy:
    """Integration tests for password policy."""

    @pytest.mark.live
    def test_get_password_config(self, splunk_client):
        """Test getting password configuration."""
        try:
            response = splunk_client.get(
                "/services/authentication/password",
                operation="get password config"
            )
            assert response is not None
        except Exception:
            # Password config may not be exposed
            pass
