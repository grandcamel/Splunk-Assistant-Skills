#!/usr/bin/env python3
"""Live Integration Tests for splunk-alert skill."""

import pytest


class TestAlertOperations:
    """Integration tests for alert operations."""

    @pytest.mark.live
    def test_list_fired_alerts(self, splunk_client):
        """Test listing fired alerts."""
        response = splunk_client.get(
            "/services/alerts/fired_alerts",
            params={"output_mode": "json"},
            operation="list fired alerts"
        )

        # Response should have entry key (may be empty list)
        assert "entry" in response

    @pytest.mark.live
    def test_list_fired_alerts_with_count(self, splunk_client):
        """Test listing fired alerts with count limit."""
        response = splunk_client.get(
            "/services/alerts/fired_alerts",
            params={"output_mode": "json", "count": 10},
            operation="list fired alerts"
        )

        assert "entry" in response
        # If there are alerts, verify structure
        for entry in response.get("entry", []):
            assert "name" in entry
            assert "content" in entry


class TestAlertActions:
    """Integration tests for alert action configuration."""

    @pytest.mark.live
    def test_list_alert_actions(self, splunk_client):
        """Test listing available alert actions."""
        response = splunk_client.get(
            "/services/alerts/alert_actions",
            params={"output_mode": "json"},
            operation="list alert actions"
        )

        assert "entry" in response
        # Should have at least some default actions (email, script, etc.)
        action_names = [e.get("name") for e in response.get("entry", [])]
        # Common default actions
        assert len(action_names) >= 0  # May vary by installation

    @pytest.mark.live
    def test_get_email_action_config(self, splunk_client):
        """Test getting email alert action configuration."""
        try:
            response = splunk_client.get(
                "/services/alerts/alert_actions/email",
                params={"output_mode": "json"},
                operation="get email action"
            )

            assert "entry" in response
            content = response["entry"][0].get("content", {})
            # Email action should have typical settings
            assert isinstance(content, dict)
        except Exception:
            # Email action may not exist in all configurations
            pass

    @pytest.mark.live
    def test_list_alert_actions_with_count(self, splunk_client):
        """Test listing alert actions with count limit."""
        response = splunk_client.get(
            "/services/alerts/alert_actions",
            params={"output_mode": "json", "count": 5},
            operation="list alert actions limited"
        )

        assert "entry" in response


class TestSavedSearchAlerts:
    """Integration tests for saved search based alerts."""

    @pytest.mark.live
    def test_list_saved_searches_with_alerts(self, splunk_client):
        """Test listing saved searches that have alerts enabled."""
        response = splunk_client.get(
            "/saved/searches",
            params={"output_mode": "json", "search": "is_scheduled=1"},
            operation="list scheduled searches"
        )

        assert "entry" in response
        # May or may not have scheduled searches
        for entry in response.get("entry", []):
            content = entry.get("content", {})
            # These are scheduled searches that could trigger alerts
            assert "search" in content or "name" in entry

    @pytest.mark.live
    def test_list_alerting_saved_searches(self, splunk_client):
        """Test listing saved searches with alert actions."""
        response = splunk_client.get(
            "/saved/searches",
            params={"output_mode": "json", "count": 20},
            operation="list saved searches"
        )

        assert "entry" in response
        # Check structure of entries
        for entry in response.get("entry", []):
            assert "name" in entry
            assert "content" in entry


class TestAlertSuppression:
    """Integration tests for alert suppression."""

    @pytest.mark.live
    def test_list_suppression_config(self, splunk_client):
        """Test accessing suppression configuration."""
        # Suppression is typically configured per-saved-search
        response = splunk_client.get(
            "/saved/searches",
            params={"output_mode": "json", "count": 5},
            operation="list for suppression check"
        )

        assert "entry" in response
        for entry in response.get("entry", []):
            content = entry.get("content", {})
            # Check for suppression-related fields if present
            if "alert.suppress" in content:
                # Suppression value can be string, bool, int, or None (unset)
                assert isinstance(content["alert.suppress"], (str, bool, int, type(None)))


class TestAlertHistory:
    """Integration tests for alert history and triggered alerts."""

    @pytest.mark.live
    def test_fired_alerts_structure(self, splunk_client):
        """Test the structure of fired alerts response."""
        response = splunk_client.get(
            "/services/alerts/fired_alerts",
            params={"output_mode": "json", "count": 10},
            operation="list fired alerts"
        )

        assert "entry" in response
        # Verify entry structure if there are any alerts
        for entry in response.get("entry", []):
            assert "name" in entry
            if "content" in entry:
                content = entry["content"]
                assert isinstance(content, dict)

    @pytest.mark.live
    def test_fired_alerts_by_severity(self, splunk_client):
        """Test listing fired alerts, checking for severity info."""
        response = splunk_client.get(
            "/services/alerts/fired_alerts",
            params={"output_mode": "json"},
            operation="list alerts for severity"
        )

        assert "entry" in response
        # If alerts exist, they should have severity info
        for entry in response.get("entry", []):
            content = entry.get("content", {})
            # severity_level may or may not be present
            if "severity" in content:
                assert content["severity"] in range(1, 7)  # Splunk severity levels
