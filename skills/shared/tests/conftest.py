#!/usr/bin/env python3
"""
Pytest fixtures for shared library tests.

Note: Common fixtures (mock_splunk_client, mock_config, sample_job_response,
sample_search_results, sample_index_list, temp_path, temp_dir, splunk_profile)
are provided by the root conftest.py.

This file contains fixtures specific to the shared library tests only.
"""

import pytest
