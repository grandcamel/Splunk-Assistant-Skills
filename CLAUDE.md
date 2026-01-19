# Splunk Assistant Skills

A modular, production-ready Claude Code skills framework for Splunk REST API automation.

## Quick Reference

| Resource | Location |
|----------|----------|
| Architecture | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| CLI Reference | [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md) |
| Configuration | [docs/CONFIGURATION.md](docs/CONFIGURATION.md) |
| SPL Patterns | [docs/SPL_PATTERNS.md](docs/SPL_PATTERNS.md) |
| Testing | [docs/TESTING.md](docs/TESTING.md) |
| Troubleshooting | [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) |
| Development | [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) |

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

## Directory Structure

```
plugins/
└── splunk-assistant-skills/   # Plugin package
    ├── plugin.json            # Plugin manifest
    └── skills/                # 14 skills
        └── shared/            # Shared config and tests

docs/                          # Detailed documentation
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full structure.

## Quick Start

### Installation

```bash
# Via Claude Code plugin system
/assistant-skills-setup

# Or manual installation
pip install splunk-assistant-skills-lib
```

### Configuration

Set environment variables:

```bash
export SPLUNK_SITE_URL="https://splunk.example.com"
export SPLUNK_TOKEN="your-jwt-token"
```

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for all options.

### CLI Usage

```bash
# Search
splunk-as search oneshot "index=main | head 10"

# Job management
splunk-as job list
splunk-as job status <sid>

# Metadata
splunk-as metadata indexes
```

See [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md) for all commands.

## Shared Library

All scripts import from [splunk-assistant-skills-lib](https://pypi.org/project/splunk-assistant-skills-lib/):

```python
from splunk_assistant_skills_lib import (
    get_splunk_client,
    handle_errors,
    print_success,
)

@handle_errors
def main():
    client = get_splunk_client()
    # Your code here
```

## Testing

```bash
# Run unit tests
pytest plugins/splunk-assistant-skills/skills/*/tests/ -v

# Run live integration tests (requires Splunk)
pytest plugins/splunk-assistant-skills/skills/*/tests/live_integration/ -v
```

See [docs/TESTING.md](docs/TESTING.md) for complete testing guide.

## Common Issues

| Issue | Solution |
|-------|----------|
| Connection errors | Check `SPLUNK_SITE_URL` and port 8089 access |
| Auth failures | Verify token/credentials |
| Search quota | Cancel unused jobs |
| Timeouts | Use async mode or increase timeout |

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for detailed solutions.

## Development

### Adding Scripts

1. Create script in `{skill}/scripts/`
2. Add tests in `{skill}/tests/`
3. Update `SKILL.md`

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for templates and guidelines.

### Git Commits

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(skill): add new capability
fix(client): handle timeout errors
docs: update configuration guide
```
