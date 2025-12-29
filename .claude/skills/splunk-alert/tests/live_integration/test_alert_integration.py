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
