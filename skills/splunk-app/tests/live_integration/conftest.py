#!/usr/bin/env python3
"""
Pytest configuration for splunk-app live integration tests.

Fixtures are automatically loaded from shared/tests/live_integration/fixtures.py
via pytest_plugins. The shared path is configured in pytest.ini's pythonpath.
"""

# Load all shared fixtures (splunk_connection, splunk_client, test_index, etc.)
pytest_plugins = ["fixtures"]
