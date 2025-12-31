#!/usr/bin/env python3
"""
Pytest configuration for live integration tests.

This conftest.py is automatically loaded by pytest for all live_integration tests.
It re-exports the fixtures and configures test markers.
"""

import logging
import os
import sys
from pathlib import Path

import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Suppress urllib3 warnings about self-signed certs
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add this directory to path for absolute imports in fixtures.py
sys.path.insert(0, str(Path(__file__).parent))

# Import and re-export all fixtures
# Import fixtures - pytest discovers these automatically via conftest.py
from .fixtures import *


# Note: pytest markers (live, destructive, etc.) are defined in root conftest.py


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on environment."""
    # Check if we have Splunk connection configured
    has_external = bool(os.environ.get("SPLUNK_TEST_URL"))
    has_docker = _check_docker_available()

    skip_no_splunk = pytest.mark.skip(reason="No Splunk connection available")
    skip_no_docker = pytest.mark.skip(reason="Docker not available")
    skip_no_external = pytest.mark.skip(reason="External Splunk not configured")

    for item in items:
        # Skip all live tests if no connection
        if "live" in item.keywords:
            if not has_external and not has_docker:
                item.add_marker(skip_no_splunk)

        # Skip docker-required tests if no Docker
        if "docker_required" in item.keywords:
            if has_external:
                item.add_marker(
                    pytest.mark.skip(
                        reason="Using external Splunk, skipping Docker test"
                    )
                )
            elif not has_docker:
                item.add_marker(skip_no_docker)

        # Skip external-only tests if no external Splunk
        if "external_splunk" in item.keywords:
            if not has_external:
                item.add_marker(skip_no_external)


def _check_docker_available() -> bool:
    """Check if Docker is available."""
    try:
        import docker

        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--splunk-url",
        action="store",
        default=None,
        help="External Splunk URL (overrides SPLUNK_TEST_URL env var)",
    )
    parser.addoption(
        "--splunk-token",
        action="store",
        default=None,
        help="Splunk token (overrides SPLUNK_TEST_TOKEN env var)",
    )
    parser.addoption(
        "--splunk-image",
        action="store",
        default=None,
        help="Docker image for Splunk (overrides SPLUNK_TEST_IMAGE env var)",
    )
    parser.addoption(
        "--skip-slow",
        action="store_true",
        default=False,
        help="Skip slow integration tests",
    )


@pytest.fixture(scope="session", autouse=True)
def configure_from_options(request):
    """Apply command line options to environment."""
    if request.config.getoption("--splunk-url"):
        os.environ["SPLUNK_TEST_URL"] = request.config.getoption("--splunk-url")
    if request.config.getoption("--splunk-token"):
        os.environ["SPLUNK_TEST_TOKEN"] = request.config.getoption("--splunk-token")
    if request.config.getoption("--splunk-image"):
        os.environ["SPLUNK_TEST_IMAGE"] = request.config.getoption("--splunk-image")


@pytest.fixture(autouse=True)
def skip_slow_tests(request):
    """Skip slow tests if --skip-slow is set."""
    if request.config.getoption("--skip-slow"):
        if request.node.get_closest_marker("slow_integration"):
            pytest.skip("Skipping slow test (--skip-slow)")


# Print connection info at start of session
@pytest.fixture(scope="session", autouse=True)
def print_connection_info(splunk_connection):
    """Print connection information at session start."""
    info = splunk_connection.get_connection_info()
    print("\n" + "=" * 60)
    print("Splunk Integration Test Session")
    print("=" * 60)
    print(f"Management URL: {info.get('management_url', 'N/A')}")
    print(f"Username: {info.get('username', 'N/A')}")
    print("=" * 60 + "\n")
    yield
    print("\n" + "=" * 60)
    print("Integration tests completed")
    print("=" * 60)
