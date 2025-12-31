# Live Integration Tests

This directory contains the live integration test framework for testing Splunk skills against a real Splunk instance.

## Overview

The framework supports two modes:
1. **Docker Mode**: Automatically starts a Splunk container using testcontainers
2. **External Mode**: Connects to an existing external Splunk instance

## Prerequisites

### Docker Mode
- Docker installed and running
- Python 3.8+
- Dependencies: `pip install -r requirements.txt`

### External Mode
- Access to a Splunk instance with REST API enabled
- Authentication token or username/password credentials

## Quick Start

### Using Docker (Default)

```bash
# Run all live integration tests
pytest skills/shared/tests/live_integration/ -v -m live

# Run specific skill tests
pytest skills/splunk-search/tests/live_integration/ -v
pytest skills/splunk-job/tests/live_integration/ -v
```

### Using External Splunk

```bash
# Set environment variables
export SPLUNK_TEST_URL=https://your-splunk:8089
export SPLUNK_TEST_TOKEN=your-auth-token

# Or with username/password
export SPLUNK_TEST_URL=https://your-splunk:8089
export SPLUNK_TEST_USERNAME=admin
export SPLUNK_TEST_PASSWORD=changeme

# Run tests
pytest skills/splunk-search/tests/live_integration/ -v
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SPLUNK_TEST_URL` | External Splunk management URL | (Docker auto-configured) |
| `SPLUNK_TEST_TOKEN` | Bearer token for authentication | (Docker auto-generated) |
| `SPLUNK_TEST_USERNAME` | Username for basic auth | `admin` |
| `SPLUNK_TEST_PASSWORD` | Password for basic auth | (Docker: `testpassword123`) |
| `SPLUNK_TEST_IMAGE` | Docker image for Splunk | `splunk/splunk:latest` |
| `SPLUNK_TEST_INDEX` | Test index name | `splunk_skills_test` |

## Command Line Options

```bash
# Override Splunk URL
pytest --splunk-url=https://splunk:8089

# Override token
pytest --splunk-token=your-token

# Skip slow tests
pytest --skip-slow

# Custom Docker image
pytest --splunk-image=splunk/splunk:9.1.0
```

## Test Markers

| Marker | Description |
|--------|-------------|
| `@pytest.mark.live` | Requires live Splunk connection |
| `@pytest.mark.docker_required` | Requires Docker (skipped with external Splunk) |
| `@pytest.mark.external_splunk` | Requires external Splunk (skipped with Docker) |
| `@pytest.mark.slow_integration` | Slow tests (skippable with `--skip-slow`) |
| `@pytest.mark.destructive` | Tests that modify Splunk configuration |

## Architecture

```
live_integration/
├── __init__.py
├── conftest.py          # Pytest configuration and marker registration
├── fixtures.py          # Session-scoped fixtures
├── splunk_container.py  # Docker container management
├── test_utils.py        # Test data generation utilities
└── README.md            # This file
```

## Fixtures

### Connection Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `splunk_connection` | session | SplunkContainer or ExternalSplunkConnection |
| `splunk_client` | session | Configured SplunkClient instance |
| `splunk_info` | session | Server information dict |

### Test Data Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `test_index` | session | Dedicated test index (auto-created/cleaned) |
| `test_index_name` | session | Test index name string |
| `test_data` | session | Synthetic test events (350 events) |
| `fresh_test_data` | function | Fresh events unique to each test |

### Helper Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `search_helper` | function | Simplified search operations |
| `job_helper` | function | Search job management with auto-cleanup |

## Test Data Generation

Test data is generated using SPL `| makeresults` to avoid external file dependencies:

```python
from live_integration.test_utils import generate_test_events

generate_test_events(
    connection,
    index="test_index",
    count=100,
    fields={
        "sourcetype": "access_combined",
        "host": ["web01", "web02", "web03"],
        "status": [200, 404, 500],
    }
)
```

### EventBuilder (Fluent API)

```python
from live_integration.test_utils import EventBuilder

spl = (EventBuilder()
    .with_count(100)
    .with_index("test")
    .with_field("host", ["web01", "web02"])
    .with_field("status", [200, 404, 500])
    .build())
```

## Writing Tests

### Basic Test Example

```python
import pytest
from live_integration.fixtures import splunk_client, test_index, test_data

class TestMyFeature:
    @pytest.mark.live
    def test_basic_search(self, splunk_client, test_index, test_data):
        response = splunk_client.post(
            "/search/jobs/oneshot",
            data={
                "search": f"search index={test_index} | head 10",
                "output_mode": "json",
            },
            operation="test search",
        )

        results = response.get("results", [])
        assert len(results) > 0
```

### Using Search Helper

```python
@pytest.mark.live
def test_with_helper(self, search_helper, test_index, test_data):
    # Oneshot search
    results = search_helper.oneshot(f"search index={test_index} | head 5")
    assert len(results) == 5

    # Count events
    count = search_helper.count(f"search index={test_index}")
    assert count > 0

    # Check existence
    assert search_helper.exists(f"search index={test_index}")
```

### Using Job Helper

```python
@pytest.mark.live
def test_with_job_helper(self, job_helper, test_index, test_data):
    # Create async job
    sid = job_helper.create(f"search index={test_index} | stats count")

    # Wait for completion
    status = job_helper.wait_for_done(sid, timeout=60)

    assert status["isDone"] is True
    assert status["resultCount"] > 0

    # Cleanup is automatic via fixture teardown
```

## Troubleshooting

### Docker Issues

```bash
# Check Docker is running
docker info

# Pull Splunk image manually
docker pull splunk/splunk:latest

# Check container logs (if stuck)
docker logs <container_id>
```

### Connection Issues

```bash
# Test external Splunk connectivity
curl -k https://your-splunk:8089/services/server/info \
  -H "Authorization: Bearer your-token"

# Verify credentials
curl -k https://your-splunk:8089/services/server/info \
  -u admin:password
```

### Common Errors

| Error | Solution |
|-------|----------|
| "Docker not available" | Ensure Docker daemon is running |
| "No Splunk connection" | Set `SPLUNK_TEST_URL` or start Docker |
| "Authentication failed" | Check token/credentials |
| "Index not found" | Index will be auto-created; check permissions |
| "Timeout waiting for events" | Increase `wait_for_indexing` timeout |

## Performance Tips

1. **Use session-scoped fixtures**: Reuses the same Splunk container across all tests
2. **Skip slow tests during development**: `pytest --skip-slow`
3. **Use external Splunk for CI**: Faster than starting Docker each time
4. **Limit test data**: Use `test_data` for shared data, `fresh_test_data` only when isolation is needed

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
jobs:
  integration-tests:
    runs-on: ubuntu-latest
    services:
      splunk:
        image: splunk/splunk:latest
        ports:
          - 8089:8089
        env:
          SPLUNK_START_ARGS: --accept-license
          SPLUNK_PASSWORD: testpassword123
    steps:
      - uses: actions/checkout@v4
      - name: Run integration tests
        env:
          SPLUNK_TEST_URL: https://localhost:8089
          SPLUNK_TEST_USERNAME: admin
          SPLUNK_TEST_PASSWORD: testpassword123
        run: |
          pip install -r requirements.txt
          pytest skills/*/tests/live_integration/ -v -m live
```
