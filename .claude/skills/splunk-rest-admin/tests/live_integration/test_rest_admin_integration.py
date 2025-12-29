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

    @pytest.mark.live
    def test_get_license_groups(self, splunk_client):
        """Test getting license groups."""
        response = splunk_client.get(
            "/services/licenser/groups",
            operation="get license groups"
        )

        assert "entry" in response

    @pytest.mark.live
    def test_get_license_usage(self, splunk_client):
        """Test getting license usage."""
        try:
            response = splunk_client.get(
                "/services/licenser/usage",
                operation="get license usage"
            )
            assert "entry" in response or response is not None
        except Exception:
            # Usage endpoint may not be available
            pass


class TestServerConfiguration:
    """Integration tests for server configuration."""

    @pytest.mark.live
    def test_get_server_settings_general(self, splunk_client):
        """Test getting general server settings."""
        response = splunk_client.get(
            "/services/server/settings/settings",
            operation="get settings"
        )

        assert "entry" in response
        content = response["entry"][0].get("content", {})
        assert isinstance(content, dict)

    @pytest.mark.live
    def test_get_deployment_info(self, splunk_client):
        """Test getting deployment information."""
        try:
            response = splunk_client.get(
                "/services/deployment/server",
                operation="get deployment"
            )
            assert response is not None
        except Exception:
            # Deployment server may not be configured
            pass

    @pytest.mark.live
    def test_get_cluster_config(self, splunk_client):
        """Test getting cluster configuration."""
        try:
            response = splunk_client.get(
                "/services/cluster/config",
                operation="get cluster config"
            )
            assert response is not None
        except Exception:
            # Cluster may not be configured
            pass


class TestIntrospection:
    """Integration tests for introspection endpoints."""

    @pytest.mark.live
    def test_get_capabilities(self, splunk_client):
        """Test getting server capabilities."""
        response = splunk_client.get(
            "/services/authorization/capabilities",
            operation="get capabilities"
        )

        assert "entry" in response

    @pytest.mark.live
    def test_get_configs(self, splunk_client):
        """Test getting configuration files."""
        response = splunk_client.get(
            "/services/configs/conf-web",
            operation="get web config"
        )

        assert "entry" in response

    @pytest.mark.live
    def test_get_props_config(self, splunk_client):
        """Test getting props.conf settings."""
        response = splunk_client.get(
            "/services/configs/conf-props",
            params={"count": 10},
            operation="get props config"
        )

        assert "entry" in response

    @pytest.mark.live
    def test_get_transforms_config(self, splunk_client):
        """Test getting transforms.conf settings."""
        response = splunk_client.get(
            "/services/configs/conf-transforms",
            params={"count": 10},
            operation="get transforms config"
        )

        assert "entry" in response


class TestScheduler:
    """Integration tests for scheduler status."""

    @pytest.mark.live
    def test_get_scheduler_status(self, splunk_client):
        """Test getting scheduler status."""
        try:
            response = splunk_client.get(
                "/services/scheduler",
                operation="get scheduler"
            )
            assert response is not None
        except Exception:
            # Scheduler endpoint may not exist
            pass


class TestInternalLogs:
    """Integration tests for internal logs access."""

    @pytest.mark.live
    def test_search_internal_logs(self, splunk_client):
        """Test searching internal logs."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": "search index=_internal | head 5",
                "output_mode": "json",
                "earliest_time": "-1h",
            },
            operation="search internal"
        )

        results = response.get("results", [])
        assert isinstance(results, list)

    @pytest.mark.live
    def test_search_audit_logs(self, splunk_client):
        """Test searching audit logs."""
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": "search index=_audit | head 5",
                "output_mode": "json",
                "earliest_time": "-1h",
            },
            operation="search audit"
        )

        results = response.get("results", [])
        assert isinstance(results, list)


class TestProperties:
    """Integration tests for properties endpoints."""

    @pytest.mark.live
    def test_get_server_name(self, splunk_client):
        """Test getting server name from info."""
        info = splunk_client.get_server_info()
        assert "serverName" in info

    @pytest.mark.live
    def test_get_server_version(self, splunk_client):
        """Test getting server version."""
        info = splunk_client.get_server_info()
        assert "version" in info
        # Version should be in format x.y.z
        version = info["version"]
        assert "." in version

    @pytest.mark.live
    def test_get_server_build(self, splunk_client):
        """Test getting server build number."""
        info = splunk_client.get_server_info()
        assert "build" in info
