# Testing Guide

This document covers the testing strategy, configuration, and best practices for Splunk Assistant Skills.

## Test Configuration

Tests are configured via `pytest.ini` at the project root:
- Uses `--import-mode=importlib` to avoid module name conflicts
- Defines markers: `slow`, `integration`, `unit`

## Unit Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run all unit tests
pytest skills/*/tests/ -v

# Run tests for specific skill
pytest skills/splunk-search/tests/ -v

# Run shared library tests only
pytest skills/shared/tests/ -v
```

## Live Integration Tests

Live integration tests have been moved to the [splunk-as](https://github.com/grandcamel/splunk-as) package.

To run live integration tests:

```bash
cd /path/to/splunk-as
pytest tests/live/ --live -v
```

See the splunk-as documentation for details on Docker and external Splunk configuration.

## Test Markers

```python
import pytest

@pytest.mark.slow
def test_takes_long():
    """Long-running test (>30s)."""
    pass

@pytest.mark.unit
def test_no_dependencies():
    """Unit test with no external dependencies."""
    pass
```

## CI/CD Integration

The project includes GitHub Actions workflows:

- `.github/workflows/validate.yml` - Runs unit tests on every push/PR
- `.github/workflows/release.yml` - Runs tests before releases

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

### Fixture Scope Guidelines

- **session**: Shared across all tests (fastest, less isolated)
- **module**: Fresh per test file (moderate isolation)
- **function**: Fresh per test (slowest, full isolation)

## E2E Tests

End-to-end tests validate the plugin with the Claude Code CLI.

```bash
# Requires ANTHROPIC_API_KEY or OAuth authentication
./scripts/run-e2e-tests.sh           # Docker
./scripts/run-e2e-tests.sh --local   # Local
./scripts/run-e2e-tests.sh --verbose # Verbose
```

See [tests/e2e/README.md](../tests/e2e/README.md) for details.
