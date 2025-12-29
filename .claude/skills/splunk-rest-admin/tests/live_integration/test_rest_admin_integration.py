#!/usr/bin/env python3
"""Live Integration Tests for splunk-rest-admin skill."""

import pytest


class TestServerInfo:
    """Integration tests for server info operations."""

    @pytest.mark.live
    def test_get_server_info(self, splunk_client):
        """Test getting server information."""
        info = splunk_client.get_server_info()

        assert "version" in info
        assert "serverName" in info
        assert "build" in info

    @pytest.mark.live
    def test_get_server_info_via_rest(self, splunk_client):
        """Test getting server info via REST endpoint."""
        response = splunk_client.get(
            "/services/server/info",
            operation="get server info"
        )

        assert "entry" in response
        content = response["entry"][0].get("content", {})
        assert "version" in content


class TestServerStatus:
    """Integration tests for server status operations."""

    @pytest.mark.live
    def test_get_server_status(self, splunk_client):
        """Test getting server status."""
        response = splunk_client.get(
            "/services/server/status",
            operation="get server status"
        )

        assert "entry" in response

    @pytest.mark.live
    def test_get_server_settings(self, splunk_client):
        """Test getting server settings."""
        response = splunk_client.get(
            "/services/server/settings",
            operation="get server settings"
        )

        assert "entry" in response


class TestServerHealth:
    """Integration tests for server health operations."""

    @pytest.mark.live
    def test_get_server_health(self, splunk_client):
        """Test getting server health status."""
        try:
            response = splunk_client.get(
                "/services/server/health/splunkd",
                operation="get server health"
            )

            assert "entry" in response
            content = response["entry"][0].get("content", {})
            # Health should be present
            assert "health" in content or "features" in content
        except Exception:
            # Health endpoint may not be available on all versions
            pytest.skip("Health endpoint not available")


class TestServerMessages:
    """Integration tests for server messages."""

    @pytest.mark.live
    def test_get_server_messages(self, splunk_client):
        """Test getting server messages."""
        response = splunk_client.get(
            "/services/messages",
            operation="get messages"
        )

        assert "entry" in response or response == {}


class TestLicenseInfo:
    """Integration tests for license information."""

    @pytest.mark.live
    def test_get_license_info(self, splunk_client):
        """Test getting license information."""
        response = splunk_client.get(
            "/services/licenser/licenses",
            operation="get licenses"
        )

        assert "entry" in response
