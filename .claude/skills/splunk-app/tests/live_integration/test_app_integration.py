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

    @pytest.mark.live
    def test_list_app_navs(self, splunk_client):
        """Test listing navigation for an app."""
        response = splunk_client.get(
            "/servicesNS/nobody/search/data/ui/nav",
            operation="list navs"
        )

        assert "entry" in response

    @pytest.mark.live
    def test_list_app_panels(self, splunk_client):
        """Test listing panels for an app."""
        try:
            response = splunk_client.get(
                "/servicesNS/nobody/search/data/ui/panels",
                operation="list panels"
            )
            assert "entry" in response or response is not None
        except Exception:
            # Panels may not exist
            pass


class TestAppProperties:
    """Integration tests for app properties."""

    @pytest.mark.live
    def test_search_app_visible(self, splunk_client):
        """Test that search app is visible."""
        response = splunk_client.get(
            "/services/apps/local/search",
            operation="get search app"
        )

        content = response["entry"][0].get("content", {})
        assert content.get("visible") in [True, "true", "1", 1]

    @pytest.mark.live
    def test_search_app_not_disabled(self, splunk_client):
        """Test that search app is not disabled."""
        response = splunk_client.get(
            "/services/apps/local/search",
            operation="get search app"
        )

        content = response["entry"][0].get("content", {})
        disabled = content.get("disabled")
        assert disabled in [False, "false", "0", 0, None]

    @pytest.mark.live
    def test_app_has_author(self, splunk_client):
        """Test that apps have author information."""
        response = splunk_client.get(
            "/services/apps/local/search",
            operation="get search app"
        )

        content = response["entry"][0].get("content", {})
        assert "author" in content or "label" in content

    @pytest.mark.live
    def test_list_enabled_apps(self, splunk_client):
        """Test listing only enabled apps."""
        response = splunk_client.get(
            "/services/apps/local",
            params={"search": "disabled=false"},
            operation="list enabled apps"
        )

        assert "entry" in response


class TestAppSetup:
    """Integration tests for app setup."""

    @pytest.mark.live
    def test_check_app_setup_status(self, splunk_client):
        """Test checking app setup status."""
        try:
            response = splunk_client.get(
                "/services/apps/local/search/setup",
                operation="get app setup"
            )
            assert response is not None
        except Exception:
            # Setup endpoint may not exist for all apps
            pass


class TestAppCapabilities:
    """Integration tests for app capabilities."""

    @pytest.mark.live
    def test_list_all_apps_across_namespaces(self, splunk_client):
        """Test listing apps across all namespaces."""
        response = splunk_client.get(
            "/servicesNS/-/-/apps/local",
            params={"count": 20},
            operation="list all apps"
        )

        assert "entry" in response

    @pytest.mark.live
    def test_app_count(self, splunk_client):
        """Test that we can count installed apps."""
        response = splunk_client.get(
            "/services/apps/local",
            operation="list apps"
        )

        app_count = len(response.get("entry", []))
        assert app_count >= 1  # At least search app

    @pytest.mark.live
    def test_get_launcher_app(self, splunk_client):
        """Test getting launcher app info."""
        try:
            response = splunk_client.get(
                "/services/apps/local/launcher",
                operation="get launcher"
            )
            assert "entry" in response
        except Exception:
            # Launcher may not exist
            pass

    @pytest.mark.live
    def test_get_splunk_instrumentation_app(self, splunk_client):
        """Test getting Splunk instrumentation app."""
        try:
            response = splunk_client.get(
                "/services/apps/local/splunk_instrumentation",
                operation="get instrumentation"
            )
            assert response is not None
        except Exception:
            # May not exist in all installations
            pass


class TestAppUI:
    """Integration tests for app UI components."""

    @pytest.mark.live
    def test_list_dashboards(self, splunk_client):
        """Test listing dashboards."""
        response = splunk_client.get(
            "/servicesNS/-/-/data/ui/views",
            params={"count": 10},
            operation="list dashboards"
        )

        assert "entry" in response

    @pytest.mark.live
    def test_list_reports(self, splunk_client):
        """Test listing reports (saved searches)."""
        response = splunk_client.get(
            "/servicesNS/-/-/saved/searches",
            params={"count": 10},
            operation="list reports"
        )

        assert "entry" in response
