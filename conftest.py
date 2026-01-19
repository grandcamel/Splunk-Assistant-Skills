#!/usr/bin/env python3
"""
Shared pytest fixtures for all Splunk Assistant Skills tests.

This root conftest.py provides common fixtures used across multiple skill tests.
Skill-specific fixtures remain in their respective conftest.py files.

Fixture Categories:
- Temporary directories: temp_path, temp_dir
- Mock Splunk client: mock_splunk_client, mock_config
- Sample responses: sample_job_response, sample_search_results, sample_index_list
- Test configuration: splunk_profile
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest


# =============================================================================
# TEMPORARY DIRECTORY FIXTURES
# =============================================================================


@pytest.fixture
def temp_path():
    """Create a temporary directory as Path object.

    Preferred fixture for new tests. Automatically cleaned up.
    Resolves symlinks to avoid macOS /var -> /private/var issues.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir).resolve()


@pytest.fixture
def temp_dir(temp_path):
    """Create a temporary directory as string.

    Legacy compatibility. Prefer temp_path for new tests.
    """
    return str(temp_path)


# =============================================================================
# MOCK SPLUNK CLIENT FIXTURES
# =============================================================================


@pytest.fixture
def mock_splunk_client():
    """Create a mock SplunkClient for testing.

    Provides a standard mock with common attributes and default responses.
    Skill-specific tests can override return values as needed.
    """
    client = Mock()
    client.base_url = "https://splunk.example.com:8089/services"
    client.auth_method = "bearer"
    client.timeout = 30
    client.DEFAULT_SEARCH_TIMEOUT = 300

    # Default responses for HTTP methods
    client.get.return_value = {"entry": []}
    client.post.return_value = {"sid": "1703779200.12345"}
    client.put.return_value = {}
    client.delete.return_value = {}

    return client


@pytest.fixture
def mock_config():
    """Create mock configuration for Splunk connection."""
    return {
        "splunk": {
            "default_profile": "test",
            "profiles": {
                "test": {
                    "url": "https://splunk.example.com",
                    "port": 8089,
                    "token": "test-token",
                    "auth_method": "bearer",
                }
            },
            "api": {
                "timeout": 30,
                "search_timeout": 300,
            },
            "search_defaults": {
                "earliest_time": "-24h",
                "latest_time": "now",
                "max_count": 50000,
            },
        }
    }


# =============================================================================
# SAMPLE RESPONSE FIXTURES
# =============================================================================


@pytest.fixture
def sample_job_response():
    """Sample search job response for testing job lifecycle."""
    return {
        "sid": "1703779200.12345",
        "entry": [
            {
                "name": "1703779200.12345",
                "content": {
                    "sid": "1703779200.12345",
                    "dispatchState": "DONE",
                    "doneProgress": 1.0,
                    "eventCount": 1000,
                    "resultCount": 100,
                    "scanCount": 5000,
                    "runDuration": 2.5,
                    "isDone": True,
                    "isFailed": False,
                    "isPaused": False,
                },
            }
        ],
    }


@pytest.fixture
def sample_search_results():
    """Sample search results for testing result parsing."""
    return {
        "results": [
            {"host": "server1", "status": "200", "count": "100"},
            {"host": "server2", "status": "200", "count": "150"},
            {"host": "server3", "status": "404", "count": "25"},
        ]
    }


@pytest.fixture
def sample_index_list():
    """Sample index list response for testing metadata operations."""
    return {
        "entry": [
            {
                "name": "main",
                "content": {
                    "totalEventCount": 1000000,
                    "currentDBSizeMB": 1024,
                    "maxDataSizeMB": 500000,
                    "disabled": False,
                },
            },
            {
                "name": "_internal",
                "content": {
                    "totalEventCount": 500000,
                    "currentDBSizeMB": 256,
                    "maxDataSizeMB": 500000,
                    "disabled": False,
                },
            },
        ]
    }


# =============================================================================
# PROJECT STRUCTURE FIXTURES
# =============================================================================


@pytest.fixture
def claude_project_structure(temp_path):
    """Create a standard .claude project structure for testing."""
    project = temp_path / "Test-Project"
    project.mkdir()

    claude_dir = project / ".claude"
    skills_dir = claude_dir / "skills"
    shared_lib = skills_dir / "shared" / "scripts" / "lib"
    shared_lib.mkdir(parents=True)

    settings = claude_dir / "settings.json"
    settings.write_text("{}")

    return {
        "root": project,
        "claude_dir": claude_dir,
        "skills_dir": skills_dir,
        "shared_lib": shared_lib,
        "settings": settings,
    }


@pytest.fixture
def sample_skill_md():
    """Return sample SKILL.md content for testing."""
    return '''---
name: sample-skill
description: A sample skill for testing.
---

# Sample Skill

## Quick Start

```bash
echo "Hello"
```
'''


# =============================================================================
# TEST CONFIGURATION FIXTURES
# =============================================================================


@pytest.fixture
def splunk_profile(request):
    """Get Splunk profile from command line or environment.

    Used for integration tests that need to connect to a real Splunk instance.
    """
    profile = request.config.getoption("--profile", default=None)
    if not profile:
        profile = os.environ.get("SPLUNK_PROFILE")
    return profile


# =============================================================================
# PYTEST HOOKS
# =============================================================================


def pytest_addoption(parser):
    """Add custom command line options for all tests."""
    # Splunk profile option for integration tests
    parser.addoption(
        "--profile",
        action="store",
        default=None,
        help="Splunk profile for live integration tests",
    )


def pytest_configure(config):
    """Configure pytest with custom markers.

    Note: Markers are also defined in pytest.ini for IDE support.
    This hook ensures they're registered programmatically.
    """
    # Speed markers
    config.addinivalue_line("markers", "slow: marks tests as slow (>30s)")
    config.addinivalue_line("markers", "fast: marks tests as fast (<1s)")
    config.addinivalue_line("markers", "slow_integration: marks slow integration tests")

    # Environment markers
    config.addinivalue_line("markers", "live: marks tests requiring live API access")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks unit tests (no external dependencies)")
    config.addinivalue_line("markers", "docker_required: marks tests that require Docker")
    config.addinivalue_line("markers", "external_splunk: marks tests for external Splunk only")
    config.addinivalue_line("markers", "cloud_only: marks tests for Splunk Cloud only")
    config.addinivalue_line("markers", "onprem_only: marks tests for on-premises Splunk only")

    # Risk/modification markers
    config.addinivalue_line("markers", "destructive: marks tests that modify Splunk data")
    config.addinivalue_line("markers", "readonly: marks tests that only read data")
    config.addinivalue_line("markers", "creates_data: marks tests that create new resources")
    config.addinivalue_line("markers", "deletes_data: marks tests that delete resources")
    config.addinivalue_line("markers", "modifies_config: marks tests that change configuration")

    # Feature area markers
    config.addinivalue_line("markers", "search: marks tests for search operations")
    config.addinivalue_line("markers", "job: marks tests for job lifecycle")
    config.addinivalue_line("markers", "metadata: marks tests for metadata discovery")
    config.addinivalue_line("markers", "export: marks tests for data export")
    config.addinivalue_line("markers", "lookup: marks tests for lookup management")
    config.addinivalue_line("markers", "savedsearch: marks tests for saved search CRUD")
    config.addinivalue_line("markers", "alert: marks tests for alert management")
    config.addinivalue_line("markers", "security: marks tests for token/RBAC/ACL")
    config.addinivalue_line("markers", "kvstore: marks tests for KV store operations")
    config.addinivalue_line("markers", "app: marks tests for app management")
    config.addinivalue_line("markers", "admin: marks tests for admin/REST operations")
    config.addinivalue_line("markers", "metrics: marks tests for metrics (mstats/mcatalog)")
    config.addinivalue_line("markers", "tag: marks tests for tag operations")

    # Authentication markers
    config.addinivalue_line("markers", "bearer_auth: marks tests using bearer token auth")
    config.addinivalue_line("markers", "basic_auth: marks tests using basic auth")
    config.addinivalue_line("markers", "requires_admin: marks tests requiring admin privileges")
    config.addinivalue_line("markers", "requires_power: marks tests requiring power user role")

    # Resource markers
    config.addinivalue_line("markers", "requires_index: marks tests requiring specific index")
    config.addinivalue_line("markers", "requires_lookup: marks tests requiring lookup file")
    config.addinivalue_line("markers", "requires_kvstore: marks tests requiring KV store")
    config.addinivalue_line("markers", "requires_savedsearch: marks tests requiring saved search")

    # Stability markers
    config.addinivalue_line("markers", "flaky: marks tests that may be flaky/unstable")
    config.addinivalue_line("markers", "smoke: marks smoke tests for quick validation")
    config.addinivalue_line("markers", "regression: marks regression tests")
    config.addinivalue_line("markers", "xfail_known: marks expected failures with known issues")

    # Parallel execution markers
    config.addinivalue_line("markers", "serial: marks tests that must run serially")
    config.addinivalue_line("markers", "parallel_safe: marks tests safe for parallel execution")
