# Architecture

This document covers the architecture of Splunk Assistant Skills, including directory structure and the shared library pattern.

## Directory Structure

```
.claude-plugin/
├── plugin.json                # Plugin manifest
└── marketplace.json           # Marketplace metadata

.claude/
├── settings.example.json      # Example config (copy to settings.local.json)
└── settings.local.json        # Personal credentials (gitignored)

commands/                      # Slash commands (at project root)
skills/                        # 14 skills (autodiscovered)
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
└── shared/                    # Shared config and tests
    ├── config/
    └── tests/

docs/
├── ARCHITECTURE.md            # This document
├── CLI_REFERENCE.md           # CLI commands
├── CONFIGURATION.md           # Configuration guide
├── DEVELOPMENT.md             # Development guide
├── SPL_PATTERNS.md            # SPL patterns
├── TESTING.md                 # Testing guide
├── TROUBLESHOOTING.md         # Common issues
└── ASSISTANT_SKILLS_ALIGNMENT.md # Cross-project alignment
```

## Skills Overview

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

---

## Shared Library Pattern

All scripts import from the [splunk-as](https://pypi.org/project/splunk-as/) PyPI package:

```python
from splunk_as import (
    get_splunk_client,
    handle_errors,
    print_error,
    validate_spl,
    print_success,
    format_search_results,
)
```

### Library Components

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

### Base Library Inheritance

The `splunk-as` inherits from `assistant-skills-lib>=0.3.0`, which provides:

- Shared validators (email, URL, file path)
- Base exception hierarchy
- Common formatters (table, JSON, colors)
- Config manager base class
- Retry logic utilities

---

## Component Architecture

### Skill Structure

Each skill follows this structure:

```
skills/{skill-name}/
├── SKILL.md           # Skill documentation
├── scripts/           # CLI implementation scripts
│   └── ...
├── tests/             # Unit tests
│   ├── conftest.py    # Skill-specific fixtures
│   └── test_*.py
├── tests/live_integration/  # Integration tests
│   ├── conftest.py    # Live test fixtures
│   └── test_*.py
└── references/        # API docs, examples
```

### Plugin Manifest

The `.claude-plugin/plugin.json` defines the plugin structure. Skills are autodiscovered via `skills/*/SKILL.md`:

```json
{
  "name": "splunk-assistant-skills",
  "version": "2.0.0",
  "description": "14 specialized skills for natural language Splunk automation",
  "commands": [
    "./commands/*.md"
  ]
}
```

---

## Splunk Demo Environment

A companion demo project provides a fully-configured Splunk environment for testing.

### Location

The demo is in a separate repository: `splunk-demo/`

### Quick Start

```bash
cd /path/to/splunk-demo
make dev   # Start in development mode
```

### Access Points (Development Mode)

| Service | URL | Credentials |
|---------|-----|-------------|
| Splunk Web | http://localhost:8000 | admin / DemoPass123! |
| Landing Page | http://localhost:18080 | Invite token |
| Grafana | http://localhost:13000 | admin / admin |
| Webhooks | http://localhost:8081 | - |

### Demo Data Indexes

| Index | Purpose | Sourcetypes |
|-------|---------|-------------|
| `demo_devops` | CI/CD, containers | cicd:pipeline, container:docker, deploy:events |
| `demo_sre` | Errors, latency | app:errors, metrics:latency, health:checks |
| `demo_support` | Sessions, tickets | session:trace, error:user, feature:usage |
| `demo_business` | KPIs, compliance | kpi:revenue, compliance:audit, capacity:metrics |
| `demo_main` | General logs | app:logs |

### Sample Queries

```spl
# DevOps: Failed pipelines
index=demo_devops sourcetype=cicd:pipeline status=failure
| stats count by repository | sort -count

# SRE: P99 latency by endpoint
index=demo_sre sourcetype=metrics:latency
| stats perc99(duration_ms) as p99 by endpoint
| where p99 > 500

# Support: Customer session trace
index=demo_support sourcetype=session:trace user_id="cust_456"
| sort _time | table _time page action duration_ms

# Business: Daily revenue by region
index=demo_business sourcetype=kpi:revenue
| timechart span=1d sum(value) as revenue by region
```

### Demo Architecture

```
splunk-demo/
├── docker-compose.yml      # Main orchestration
├── docker-compose.dev.yml  # Development overrides (different ports)
├── Makefile                # Build/run commands
├── demo-container/         # Interactive Claude terminal
├── log-generator/          # Real-time event generation
├── seed-data/              # Historical data seeder
├── queue-manager/          # Session management
├── splunk/apps/demo_app/   # Splunk indexes, inputs, saved searches
└── observability/          # LGTM stack (Grafana, Loki, Tempo, Mimir)
```
