#!/usr/bin/env python3
"""
Pytest configuration for splunk-export live integration tests.

Shared fixtures are automatically loaded from shared/tests/live_integration/fixtures.py
via pytest_plugins. The shared path is configured in pytest.ini's pythonpath.
"""

import os
import tempfile

import pytest

# Load all shared fixtures (splunk_connection, splunk_client, test_index, etc.)
pytest_plugins = ["fixtures"]


# =============================================================================
# Skill-Specific Fixtures
# =============================================================================


@pytest.fixture
def temp_output_file():
    """Provide a temporary file for export tests."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    try:
        os.unlink(temp_path)
    except Exception:
        pass
