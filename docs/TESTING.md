# Testing Guide

This document covers the testing strategy, configuration, and best practices for Splunk Assistant Skills.

## Test Configuration

Tests are configured via `pytest.ini` at the project root:
- Uses `--import-mode=importlib` to avoid module name conflicts
- Excludes `live_integration` directories by default (require extra dependencies)
- Defines markers: `live`, `destructive`, `slow`, `integration`, `docker_required`

## Test Coverage Summary

| Category | Tests | Status |
|----------|-------|--------|
| Unit Tests (shared library) | 73 | Passing |
| Live Integration Tests | ~175 | Requires `testcontainers` |

## Unit Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run all unit tests (live_integration excluded by default via pytest.ini)
pytest plugins/splunk-assistant-skills/skills/*/tests/ -v

# Run tests for specific skill
pytest plugins/splunk-assistant-skills/skills/splunk-search/tests/ -v

# Run shared library tests only
pytest plugins/splunk-assistant-skills/skills/shared/tests/ -v
```

## Live Integration Tests

Live integration tests require a running Splunk instance and extra dependencies (`testcontainers`).
These tests are excluded by default via `pytest.ini` and must be run explicitly.

### Environment Variables

```bash
# Required for live tests
export SPLUNK_TEST_URL="https://localhost:8089"
export SPLUNK_TEST_USERNAME="admin"
export SPLUNK_TEST_PASSWORD="your-password"
```

### Running Tests

```bash
# Install extra dependencies for live tests
pip install testcontainers docker

# Run all integration tests for a skill (must specify path explicitly)
pytest plugins/splunk-assistant-skills/skills/splunk-search/tests/live_integration/ -v

# Run with specific markers
pytest plugins/splunk-assistant-skills/skills/*/tests/live_integration/ -m "live" -v           # All live tests
pytest plugins/splunk-assistant-skills/skills/*/tests/live_integration/ -m "not destructive" -v # Skip destructive tests

# Run single test class
pytest plugins/splunk-assistant-skills/skills/splunk-job/tests/live_integration/test_job_integration.py::TestJobLifecycle -v
```

## Docker-Based Testing

Use the Splunk Docker container for local testing:

```bash
# Start Splunk container (note: both license flags are required as of 2024+)
docker run -d --name splunk-dev \
  -p 8089:8089 -p 8000:8000 -p 8088:8088 \
  -e SPLUNK_START_ARGS="--accept-license" \
  -e SPLUNK_GENERAL_TERMS="--accept-sgt-current-at-splunk-com" \
  -e SPLUNK_PASSWORD="Admin123!" \
  -e SPLUNK_LICENSE_URI="Free" \
  splunk/splunk:latest

# Wait for Splunk to be ready (about 2-3 minutes)
docker logs -f splunk-dev

# Set environment and run tests
export SPLUNK_TEST_URL="https://localhost:8089"
export SPLUNK_TEST_USERNAME="admin"
export SPLUNK_TEST_PASSWORD="Admin123!"

pytest plugins/splunk-assistant-skills/skills/splunk-metadata/tests/live_integration/ -v
```

### Splunk Docker Gotchas

| Issue | Solution |
|-------|----------|
| License not accepted error | Add both `SPLUNK_START_ARGS="--accept-license"` AND `SPLUNK_GENERAL_TERMS="--accept-sgt-current-at-splunk-com"` |
| Image version not found | Use `splunk/splunk:latest` instead of specific versions like `9.1.0` |
| Volume mount permission errors | Don't use `:ro` flag on app directories - Splunk needs to chown them |
| Health check failures | Use `http://localhost:8000/en-US/account/login` instead of management API with auth |
| Port conflicts | Common ports (8080, 6379, 3000, 4317/4318) are often in use - use alternatives like 18080, 16379, etc. |

## Test Markers

```python
import pytest

@pytest.mark.live
def test_requires_connection():
    """Requires live Splunk connection."""
    pass

@pytest.mark.destructive
def test_modifies_data():
    """Creates/modifies/deletes Splunk objects."""
    pass

@pytest.mark.slow
def test_takes_long():
    """Long-running test (>30s)."""
    pass
```

## CI/CD Integration

The project includes GitHub Actions workflow (`.github/workflows/ci.yml`):

- Runs unit tests on every push/PR
- Live integration tests require Splunk credentials in GitHub Secrets
- Use `-m "not destructive"` for CI environments

## Known Test Limitations

Some tests are marked `xfail` due to known limitations:

| Test | Reason |
|------|--------|
| `test_export_endpoint_csv` | Export endpoint returns raw CSV, client expects JSON |
| `test_export_endpoint_json` | Export returns streaming JSON lines, not single object |
| `test_upload_and_get_lookup` | Lookup upload requires multipart form handling |

## Test Framework Architecture

The live integration test framework uses several patterns to ensure thread-safe, efficient testing:

### Singleton Pattern with Double-Checked Locking

Docker containers and external connections use a thread-safe singleton pattern to support parallel test execution with `pytest-xdist`:

```python
# In splunk_container.py
_shared_container = None
_container_lock = threading.Lock()

def get_splunk_connection():
    global _shared_container
    if _shared_container is None:
        with _container_lock:
            if _shared_container is None:  # Double-check inside lock
                _shared_container = SplunkContainer()
    return _shared_container
```

### Reference Counting for Container Lifecycle

`SplunkContainer` uses reference counting to share a single container across multiple test sessions:

```python
class SplunkContainer:
    def start(self):
        with self._lock:
            self._ref_count += 1
            if self._is_started:
                return self  # Reuse existing container
            # ... start container

    def stop(self):
        with self._lock:
            self._ref_count -= 1
            if self._ref_count > 0:
                return  # Keep running for other sessions
            # ... stop container
```

### Dual-Phase Health Check

Container startup uses a two-phase approach:
1. Wait for "Ansible playbook complete" log message
2. Verify management API responds at `/services/server/info`

This handles variations across Splunk versions where log messages may differ.

## Test Fixture Reference

### Unit Test Fixtures (Root conftest.py)

| Fixture | Scope | Description |
|---------|-------|-------------|
| `mock_splunk_client` | function | Mock `SplunkClient` with common methods |
| `mock_config` | function | Mock configuration dictionary |
| `sample_job_response` | function | Sample search job API response |
| `sample_search_results` | function | Sample search results list |
| `sample_index_list` | function | Sample index metadata |
| `temp_path` | function | Temporary file path (auto-cleanup) |
| `temp_dir` | function | Temporary directory (auto-cleanup) |
| `splunk_profile` | function | Splunk connection profile dict |

### Live Integration Fixtures (fixtures.py)

| Fixture | Scope | Description |
|---------|-------|-------------|
| `splunk_connection` | session | Docker container or external connection |
| `splunk_client` | session | Configured `SplunkClient` instance |
| `splunk_info` | session | Server info dictionary |
| `test_index` | session | Dedicated test index (auto-created/cleaned) |
| `test_index_name` | session | Test index name string |
| `test_data` | session | 350 synthetic events across 3 sourcetypes |
| `fresh_test_data` | function | 10 isolated events per test |
| `search_helper` | function | Simplified search interface |
| `job_helper` | function | Job management with auto-cleanup |

### Fixture Scope Guidelines

- **session**: Shared across all tests (fastest, less isolated)
- **module**: Fresh per test file (moderate isolation)
- **function**: Fresh per test (slowest, full isolation)

Use `fresh_test_data` when tests modify data. Use `test_data` for read-only searches.

## Test Data Generation

The `test_utils.py` module provides utilities for generating synthetic test data:

### Generate Events with SPL

```python
from test_utils import generate_test_events, wait_for_indexing

# Generate 100 events with random field values
count = generate_test_events(
    connection,
    index="test_index",
    count=100,
    fields={
        "sourcetype": "access_combined",
        "host": ["web01", "web02", "web03"],  # Random selection
        "status": [200, 200, 200, 404, 500],  # Weighted random
    },
)

# Wait for indexing with exponential backoff
wait_for_indexing(connection, "test_index", min_events=100, timeout=60)
```

### EventBuilder Fluent API

```python
from test_utils import EventBuilder

spl = (EventBuilder()
    .with_count(100)
    .with_index("test")
    .with_sourcetype("metrics")
    .with_field("host", ["server01", "server02"])
    .with_field("metric", ["cpu", "mem", "disk"])
    .with_timestamp_spread(3600)  # Spread over 1 hour
    .build())
```

### Assertion Helpers

```python
from test_utils import assert_search_returns_results, assert_search_returns_empty

# Assert minimum results
results = assert_search_returns_results(
    connection,
    "search index=test | head 10",
    min_count=5,
)

# Assert no results
assert_search_returns_empty(connection, "search index=test status=999")
```

### Version-Specific Tests

```python
from test_utils import get_splunk_version, skip_if_version_below

version = get_splunk_version(connection)  # Returns (9, 1, 0)
skip_if_version_below(connection, (9, 0, 0), "Requires Splunk 9.0+")
```

## Pytest Configuration Details

### pythonpath Configuration

`pytest.ini` includes the shared live integration directory in `pythonpath`:

```ini
pythonpath = . plugins/splunk-assistant-skills/skills/shared/tests/live_integration
```

This enables importing shared fixtures without relative imports:

```python
# In any skill's live_integration/conftest.py
pytest_plugins = ["fixtures"]  # Imports from shared fixtures.py
```

### Test Discovery

```ini
testpaths = plugins/splunk-assistant-skills/skills
norecursedirs = live_integration .* __pycache__ node_modules
```

- Unit tests are discovered automatically
- Live integration tests require explicit paths (excluded by `norecursedirs`)

### Import Mode

```ini
addopts = --import-mode=importlib
```

Uses `importlib` mode to avoid module name conflicts when multiple skills have `tests/` directories.

### Container Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SPLUNK_TEST_IMAGE` | `splunk/splunk:latest` | Docker image |
| `SPLUNK_TEST_PASSWORD` | `testpassword123` | Admin password |
| `SPLUNK_TEST_HEC_TOKEN` | `test-hec-token-12345` | HEC token |
| `SPLUNK_TEST_STARTUP_TIMEOUT` | `300` | Max startup wait (seconds) |
| `SPLUNK_TEST_HEALTH_INTERVAL` | `5` | Health check interval (seconds) |
| `SPLUNK_TEST_MEM_LIMIT` | `4g` | Container memory limit |
| `SPLUNK_TEST_URL` | (none) | External Splunk URL (skips Docker) |
| `SPLUNK_TEST_TOKEN` | (none) | Bearer token for external |
| `SPLUNK_TEST_USERNAME` | (none) | Username for external |
| `SPLUNK_TEST_INDEX` | `splunk_skills_test` | Test index name |

### Auto-Skip Fixtures

Tests are automatically skipped based on environment:

```python
@pytest.mark.docker_required
def test_container_specific():
    """Skipped if SPLUNK_TEST_URL is set (external Splunk)."""
    pass

@pytest.mark.external_splunk
def test_external_only():
    """Skipped if using Docker container."""
    pass
```

## E2E Tests

End-to-end tests validate the plugin with the Claude Code CLI.

```bash
# Requires ANTHROPIC_API_KEY or OAuth authentication
./scripts/run-e2e-tests.sh           # Docker
./scripts/run-e2e-tests.sh --local   # Local
./scripts/run-e2e-tests.sh --verbose # Verbose
```

See [tests/e2e/README.md](../tests/e2e/README.md) for details.
