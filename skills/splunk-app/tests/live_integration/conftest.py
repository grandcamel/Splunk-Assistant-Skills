#!/usr/bin/env python3
"""Pytest configuration for live integration tests."""

import logging
import os
import sys
import uuid
from pathlib import Path

import pytest

logging.basicConfig(level=logging.INFO)
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import splunk_container module directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "tests" / "live_integration"))
from splunk_container import (
    ExternalSplunkConnection,
    SplunkContainer,
    get_splunk_connection,
)


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "live: marks tests as requiring live Splunk connection"
    )
    config.addinivalue_line(
        "markers", "destructive: marks tests that modify Splunk configuration"
    )


@pytest.fixture(scope="session")
def splunk_connection():
    connection = get_splunk_connection()
    if isinstance(connection, SplunkContainer):
        connection.start()
        yield connection
        connection.stop()
    else:
        yield connection


@pytest.fixture(scope="session")
def splunk_client(splunk_connection):
    yield splunk_connection.get_client()
