#!/usr/bin/env python3
"""Live Integration Tests for splunk-app skill."""

import pytest


class TestAppOperations:
    """Integration tests for app operations."""

    @pytest.mark.live
    def test_list_apps(self, splunk_client):
        """Test listing installed apps."""
        response = splunk_client.get(
            "/services/apps/local",
            operation="list apps"
        )

        assert "entry" in response
        # Should have at least the search app
        app_names = [e.get("name") for e in response.get("entry", [])]
        assert "search" in app_names

    @pytest.mark.live
    def test_get_app_details(self, splunk_client):
        """Test getting app details."""
        response = splunk_client.get(
            "/services/apps/local/search",
            operation="get app"
        )

        assert "entry" in response
        content = response["entry"][0].get("content", {})
        assert "label" in content
        assert "version" in content

    @pytest.mark.live
    def test_list_apps_with_details(self, splunk_client):
        """Test listing apps with full details."""
        response = splunk_client.get(
            "/services/apps/local",
            params={"count": 50},
            operation="list apps"
        )

        assert "entry" in response
        for entry in response.get("entry", []):
            assert "name" in entry
            content = entry.get("content", {})
            # Apps should have these properties
            assert "visible" in content or "disabled" in content


class TestAppMetadata:
    """Integration tests for app metadata."""

    @pytest.mark.live
    def test_get_app_templates(self, splunk_client):
        """Test getting app templates."""
        response = splunk_client.get(
            "/services/apps/apptemplates",
            operation="list templates"
        )

        # May or may not have templates
        assert "entry" in response or response == {}

    @pytest.mark.live
    def test_get_deployment_info(self, splunk_client):
        """Test getting deployment server info."""
        try:
            response = splunk_client.get(
                "/services/deployment/server",
                operation="get deployment info"
            )
            assert "entry" in response or response == {}
        except Exception:
            # Deployment server may not be configured
            pytest.skip("Deployment server not configured")


class TestAppConfiguration:
    """Integration tests for app configuration."""

    @pytest.mark.live
    def test_list_app_confs(self, splunk_client):
        """Test listing configuration files for an app."""
        response = splunk_client.get(
            "/servicesNS/nobody/search/configs/conf-props",
            operation="list props conf"
        )

        assert "entry" in response or response == {}

    @pytest.mark.live
    def test_list_app_views(self, splunk_client):
        """Test listing views for an app."""
        response = splunk_client.get(
            "/servicesNS/nobody/search/data/ui/views",
            operation="list views"
        )

        assert "entry" in response
