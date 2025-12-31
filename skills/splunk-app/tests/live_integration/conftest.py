#!/usr/bin/env python3
"""
Pytest configuration for splunk-app live integration tests.

Imports fixtures from the shared live_integration module to ensure
a single Splunk container is reused across all skills.
"""

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

# Import session-scoped fixtures from shared module
# DO NOT redefine splunk_connection - this ensures a single container is shared
from fixtures import (
    splunk_connection,
    splunk_client,
    splunk_info,
    test_index_name,
    test_index,
    test_data,
    fresh_test_data,
    search_helper,
    job_helper,
)

# Re-export for pytest discovery
__all__ = [
    "splunk_connection",
    "splunk_client",
    "splunk_info",
    "test_index_name",
    "test_index",
    "test_data",
    "fresh_test_data",
    "search_helper",
    "job_helper",
]
