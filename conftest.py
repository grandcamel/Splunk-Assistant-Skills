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
    config.addinivalue_line(
        "markers", "live: marks tests as requiring live Splunk connection"
    )
    config.addinivalue_line("markers", "destructive: marks tests that modify data")
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "integration: marks integration tests")
    config.addinivalue_line("markers", "docker_required: marks tests that require Docker")
    config.addinivalue_line(
        "markers", "external_splunk: marks tests for external Splunk only"
    )
    config.addinivalue_line(
        "markers", "slow_integration: marks slow integration tests"
    )
