# Splunk Assistant Skills

A modular, production-ready Claude Code skills framework for Splunk REST API automation.

## Project Overview

This project provides 14 specialized skills for interacting with Splunk via natural language:

| Skill | Purpose |
|-------|---------|
| `splunk-assistant` | Hub/router with 3-level progressive disclosure |
| `splunk-job` | Search job lifecycle orchestration |
| `splunk-search` | SPL query execution (oneshot/normal/blocking) |
| `splunk-export` | High-volume streaming data extraction |
| `splunk-metadata` | Index, source, sourcetype discovery |
| `splunk-lookup` | CSV and lookup file management |
| `splunk-tag` | Knowledge object tagging |
| `splunk-savedsearch` | Reports and scheduled searches |
| `splunk-rest-admin` | REST API configuration access |
| `splunk-security` | Token management and RBAC |
| `splunk-metrics` | Real-time metrics (mstats, mcatalog) |
| `splunk-alert` | Alert triggering and monitoring |
| `splunk-app` | Application management |
| `splunk-kvstore` | App Key Value Store |

## Architecture

### Directory Structure

```
.claude-plugin/
└── plugin.json                # Plugin manifest

.claude/
├── settings.example.json      # Example config (copy to settings.local.json)
└── settings.local.json        # Personal credentials (gitignored)

skills/
├── splunk-assistant/          # Hub router
├── splunk-job/                # Job lifecycle
├── splunk-search/             # SPL execution
├── splunk-export/             # Data extraction
├── splunk-metadata/           # Discovery
├── splunk-lookup/             # Lookups
├── splunk-tag/                # Tags
├── splunk-savedsearch/        # Saved searches
├── splunk-rest-admin/         # REST admin
├── splunk-security/           # Security
├── splunk-metrics/            # Metrics
├── splunk-alert/              # Alerts
├── splunk-app/                # Apps
├── splunk-kvstore/            # KV Store
└── shared/                    # Shared library
    ├── scripts/lib/
    └── config/
```

### Shared Library Pattern

All scripts import from the [splunk-assistant-skills-lib](https://pypi.org/project/splunk-assistant-skills-lib/) PyPI package:

```python
from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_error,
    validate_spl,
    print_success,
    format_search_results,
)
```

### Shared Library Components

The `splunk-assistant-skills-lib` package provides:

| Module | Purpose |
|--------|---------|
| `splunk_client` | HTTP client with retry and dual auth |
| `config_manager` | Multi-source configuration |
| `error_handler` | Exception hierarchy |
| `validators` | Input validation |
| `formatters` | Output formatting |
| `spl_helper` | SPL query building/parsing |
| `job_poller` | Async job polling |
| `time_utils` | Time modifier handling |

## Configuration System

### Priority Order

1. Environment variables (highest)
2. `.claude/settings.local.json` (personal, gitignored)
3. Built-in defaults (lowest)

### Environment Variables

```bash
# Authentication (choose one method)
export SPLUNK_TOKEN="your-jwt-token"           # Bearer token (preferred)
export SPLUNK_USERNAME="admin"                  # Basic Auth
export SPLUNK_PASSWORD="changeme"               # Basic Auth

# Connection
export SPLUNK_SITE_URL="https://splunk.example.com"
export SPLUNK_MANAGEMENT_PORT="8089"
export SPLUNK_PROFILE="production"
export SPLUNK_VERIFY_SSL="true"

# Defaults
export SPLUNK_DEFAULT_APP="search"
export SPLUNK_DEFAULT_INDEX="main"
```

### Profile Support

Configure multiple Splunk instances:

```json
{
  "splunk": {
    "default_profile": "production",
    "profiles": {
      "production": {
        "url": "https://splunk.company.com",
        "port": 8089,
        "auth_method": "bearer"
      },
      "cloud": {
        "url": "https://deployment.splunkcloud.com",
        "port": 8089,
        "auth_method": "bearer"
      },
      "development": {
        "url": "https://splunk-dev.company.com",
        "port": 8089,
        "auth_method": "basic"
      }
    }
  }
}
```

Use profiles:
```bash
python search_oneshot.py "index=main | head 10" --profile development
```

## Authentication

### JWT Bearer Token (Preferred)

1. Create token in Splunk Web: Settings > Tokens
2. Set via environment or config:
   ```bash
   export SPLUNK_TOKEN="eyJraWQiOi..."
   ```

### Basic Auth (Legacy)

For on-prem environments:
```bash
export SPLUNK_USERNAME="admin"
export SPLUNK_PASSWORD="changeme"
```

Auto-detection: Token present = Bearer, otherwise Basic Auth.

## Error Handling Strategy

### 4-Layer Approach

1. **Validation Layer**: Input validation before API calls
2. **HTTP Layer**: Retry on transient failures (429, 5xx)
3. **API Layer**: Parse Splunk error responses
4. **Application Layer**: User-friendly error messages

### Exception Hierarchy

```
SplunkError (base)
├── AuthenticationError (401)
├── AuthorizationError (403)
├── ValidationError (400)
├── NotFoundError (404)
├── RateLimitError (429)
├── SearchQuotaError (503)
├── JobFailedError
└── ServerError (5xx)
```

### Using the Error Decorator

```python
from error_handler import handle_errors

@handle_errors
def main():
    client = get_splunk_client()
    # Operations that might fail
    result = client.post('/search/jobs/oneshot', data={'search': spl})
```

## SPL Query Patterns

### Always Include Time Bounds

```spl
# Good - explicit time bounds
index=main earliest=-1h latest=now | head 100

# Bad - scans all time
index=main | head 100
```

### Field Extraction Optimization

```spl
# Good - limit fields early
index=main | fields host, status, uri | head 1000

# Bad - returns all fields
index=main | head 1000
```

### Common Patterns

```spl
# Statistics and aggregation
index=main | stats count by status | sort -count

# Time-based analysis
index=main | timechart span=1h count by sourcetype

# Subsearch
index=main [search index=alerts | fields src_ip | head 1000]

# Transaction
index=main | transaction host maxspan=5m | stats avg(duration)

# Metrics (mstats)
| mstats avg(cpu.percent) WHERE index=metrics BY host span=1h

# Metadata discovery
| metadata type=sourcetypes index=main | table sourcetype, totalCount

# REST API access
| rest /services/server/info | table splunk_server, version, build

# Lookup enrichment
index=main | lookup users.csv username OUTPUT department
```

## Search Modes

### Oneshot Mode (Ad-hoc)

Best for: Quick queries, results < 50,000 rows

```python
# Results returned inline, no job created
response = client.post(
    '/services/search/jobs/oneshot',
    data={
        'search': 'index=main | head 100',
        'output_mode': 'json',
        'earliest_time': '-1h',
        'latest_time': 'now',
    },
)
results = response['results']
```

### Normal Mode (Async)

Best for: Long-running searches, monitoring progress

```python
# Create job (returns SID immediately)
response = client.post(
    '/services/search/v2/jobs',
    data={'search': spl, 'exec_mode': 'normal'},
)
sid = response['sid']

# Poll for completion
from job_poller import poll_job_status
job = poll_job_status(client, sid, timeout=300)

# Get results
results = client.get(f'/services/search/v2/jobs/{sid}/results')
```

### Blocking Mode (Sync)

Best for: Simple queries, scripted automation

```python
# Waits for completion
response = client.post(
    '/services/search/v2/jobs',
    data={'search': spl, 'exec_mode': 'blocking'},
    timeout=300,
)
sid = response['entry'][0]['name']
results = client.get(f'/services/search/v2/jobs/{sid}/results')
```

### Export Mode (Streaming)

Best for: Large data extraction, ETL pipelines

```python
# Stream results to file
for chunk in client.stream_results(
    f'/services/search/v2/jobs/{sid}/results',
    params={'output_mode': 'csv', 'count': 0},
):
    output_file.write(chunk)
```

## Job Lifecycle

### State Flow

```
QUEUED → PARSING → RUNNING → FINALIZING → DONE
                                        → FAILED
                 → PAUSED (on pause)
```

### Job Control Actions

```python
from job_poller import cancel_job, pause_job, unpause_job, finalize_job, set_job_ttl

# Cancel running job
cancel_job(client, sid)

# Pause/resume
pause_job(client, sid)
unpause_job(client, sid)

# Finalize (return current results)
finalize_job(client, sid)

# Extend TTL
set_job_ttl(client, sid, ttl=3600)
```

### Polling Best Practices

```python
from job_poller import poll_job_status

# With progress callback
def on_progress(progress):
    print(f"Progress: {progress.progress_percent:.0f}%")

job = poll_job_status(
    client, sid,
    timeout=300,
    poll_interval=1.0,
    progress_callback=on_progress,
)
```

## Progressive Disclosure (3 Levels)

### Level 1: Essential Connection

- Verify Search Head connection on port 8089
- Validate authentication (Bearer/Basic)
- Detect deployment type (Cloud vs on-prem)
- Route to appropriate skill

### Level 2: Execution Mode Strategy

- **Oneshot**: Ad-hoc queries (minimal disk I/O)
- **Export**: ETL/large transfers (streaming)
- **Normal + Polling**: Long searches with progress
- **Blocking**: Simple, fast queries

### Level 3: Advanced Optimization

- **Time Bounds**: Enforce `earliest_time`/`latest_time`
- **Field Reduction**: Add `fields` command
- **Resource Cleanup**: Cancel jobs after use
- **Error Handling**: Use `strict=true` mode

## Testing

### Test Coverage Summary

| Category | Tests | Status |
|----------|-------|--------|
| Unit Tests (shared library) | 73 | ✅ Passing |
| Live Integration Tests | 175 | 168 passing, 7 xfailed |
| **Total** | **248** | |

### Unit Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run all unit tests
pytest skills/*/tests/ -v --ignore=skills/*/tests/live_integration

# Run tests for specific skill
pytest skills/splunk-search/tests/ -v

# Run shared library tests only
pytest skills/shared/tests/ -v
```

### Live Integration Tests

Live integration tests require a running Splunk instance.

#### Environment Variables

```bash
# Required for live tests
export SPLUNK_TEST_URL="https://localhost:8089"
export SPLUNK_TEST_USERNAME="admin"
export SPLUNK_TEST_PASSWORD="your-password"
```

#### Running Tests

```bash
# Run all integration tests for a skill
pytest skills/splunk-search/tests/live_integration/ -v

# Run with specific markers
pytest -m "live" -v                    # All live tests
pytest -m "not destructive" -v         # Skip tests that modify data

# Run single test class
pytest skills/splunk-job/tests/live_integration/test_job_integration.py::TestJobLifecycle -v
```

### Docker-Based Testing

Use the Splunk Docker container for local testing:

```bash
# Start Splunk container
docker run -d --name splunk-dev \
  -p 8089:8089 -p 8000:8000 \
  -e SPLUNK_START_ARGS="--accept-license" \
  -e SPLUNK_PASSWORD="Admin123!" \
  splunk/splunk:latest

# Wait for Splunk to be ready (about 2-3 minutes)
docker logs -f splunk-dev

# Set environment and run tests
export SPLUNK_TEST_URL="https://localhost:8089"
export SPLUNK_TEST_USERNAME="admin"
export SPLUNK_TEST_PASSWORD="Admin123!"

pytest skills/splunk-metadata/tests/live_integration/ -v
```

### Test Markers

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

### CI/CD Integration

The project includes GitHub Actions workflow (`.github/workflows/ci.yml`):

- Runs unit tests on every push/PR
- Live integration tests require Splunk credentials in GitHub Secrets
- Use `-m "not destructive"` for CI environments

### Known Test Limitations

Some tests are marked `xfail` due to known limitations:

| Test | Reason |
|------|--------|
| `test_export_endpoint_csv` | Export endpoint returns raw CSV, client expects JSON |
| `test_export_endpoint_json` | Export returns streaming JSON lines, not single object |
| `test_upload_and_get_lookup` | Lookup upload requires multipart form handling |

## Adding New Scripts

### Step-by-Step

1. Create script in `{skill}/scripts/`:

```python
#!/usr/bin/env python3
"""Brief description."""

import argparse

from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_success,
    validate_spl,
)

@handle_errors
def main():
    parser = argparse.ArgumentParser(description='Script description')
    parser.add_argument('--profile', '-p', help='Splunk profile')
    args = parser.parse_args()

    client = get_splunk_client(profile=args.profile)
    # Implementation
    print_success("Operation completed")

if __name__ == '__main__':
    main()
```

2. Create test in `{skill}/tests/test_{script}.py`:

```python
import pytest
from unittest.mock import Mock, patch

def test_script_function():
    # Test implementation
    pass
```

3. Update `SKILL.md` with usage examples

## Adding New Skills

### Required Files

```
skills/new-skill/
├── SKILL.md           # Skill documentation
├── scripts/           # Python scripts
│   └── ...
├── tests/             # Unit tests
│   ├── conftest.py
│   └── test_*.py
├── tests/live_integration/  # Integration tests
│   └── test_*.py
└── references/        # API docs, examples
```

### SKILL.md Template

```markdown
# splunk-new-skill

Brief description.

## Triggers

Keywords that activate this skill.

## Scripts

- `script_name.py` - Description

## Examples

\`\`\`bash
python script_name.py --help
\`\`\`

## API Endpoints

- `GET /services/endpoint` - Description
```

## Configuration Changes

### Schema Validation

Configuration follows `config.schema.json`. Key sections:

```json
{
  "splunk": {
    "profiles": {},      // Connection profiles
    "api": {},           // API behavior
    "search_defaults": {} // Search parameters
  }
}
```

### Adding New Settings

1. Update `config.schema.json`
2. Update `config.example.json`
3. Update `config_manager.py` if needed
4. Document in `CLAUDE.md`

## Credentials Security

### DO

- Use environment variables for sensitive data
- Store tokens in `.claude/settings.local.json` (gitignored)
- Use profiles for different environments
- Rotate tokens regularly

### DON'T

- Commit tokens or passwords to git
- Log sensitive values
- Share settings.local.json
- Use Basic Auth in production (prefer Bearer)

## Git Commit Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(skill): add new capability
fix(client): handle timeout errors
docs: update configuration guide
test(search): add integration tests
refactor(validators): simplify logic
chore: update dependencies
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `perf`: Performance
- `chore`: Maintenance

## Common Issues

### Connection Errors

```
ConnectionError: Failed to connect to splunk.example.com:8089
```

Solutions:
- Verify URL and port in configuration
- Check network/firewall access
- Ensure Splunk management port is accessible

### Authentication Failures

```
AuthenticationError: 401 Unauthorized
```

Solutions:
- Verify token is valid and not expired
- Check username/password for Basic Auth
- Ensure proper permissions/capabilities

### Search Quota Exceeded

```
SearchQuotaError: No available search slots
```

Solutions:
- Cancel unused search jobs
- Wait for running searches to complete
- Increase search quota in Splunk

### Timeout Errors

```
TimeoutError: Request timed out after 30 seconds
```

Solutions:
- Increase timeout for long searches
- Use async mode with polling
- Optimize SPL query


### Run E2E Tests

```bash
# Requires ANTHROPIC_API_KEY
./scripts/run-e2e-tests.sh           # Docker
./scripts/run-e2e-tests.sh --local   # Local
./scripts/run-e2e-tests.sh --verbose # Verbose
```
