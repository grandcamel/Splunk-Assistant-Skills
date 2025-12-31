#!/usr/bin/env python3
"""Pytest configuration for live integration tests."""

import logging
import sys
from pathlib import Path

import pytest
import urllib3

logging.basicConfig(level=logging.INFO)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add shared test utilities to path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path / "tests" / "live_integration"))

from splunk_container import (
    ExternalSplunkConnection,
    SplunkContainer,
    get_splunk_connection,
)


# Note: pytest markers (live, destructive, etc.) are defined in root conftest.py


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
