# Splunk Assistant Skills

[![Release](https://img.shields.io/github/v/release/anthropics/splunk-assistant-skills?style=flat-square)](https://github.com/anthropics/splunk-assistant-skills/releases)
[![Tests](https://img.shields.io/github/actions/workflow/status/anthropics/splunk-assistant-skills/release.yml?style=flat-square&label=tests)](https://github.com/anthropics/splunk-assistant-skills/actions)
[![Python](https://img.shields.io/badge/python-3.8+-blue?style=flat-square)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

A modular, production-ready Claude Code skills framework for Splunk REST API automation.

## Features

- **14 Specialized Skills**: Comprehensive coverage of Splunk operations
- **Natural Language Interface**: Interact with Splunk using plain English
- **Dual Authentication**: JWT Bearer token and Basic Auth support
- **Multiple Search Modes**: Oneshot, Normal (async), Blocking, and Export
- **Progressive Disclosure**: 3-level optimization guidance
- **Profile Support**: Manage multiple Splunk environments
- **Robust Error Handling**: Comprehensive exception hierarchy
- **Type-Safe**: Full type annotations and validation

## Skills

| Skill | Purpose |
|-------|---------|
| `splunk-assistant` | Hub/router with progressive disclosure |
| `splunk-job` | Search job lifecycle orchestration |
| `splunk-search` | SPL query execution |
| `splunk-export` | High-volume streaming extraction |
| `splunk-metadata` | Index, source, sourcetype discovery |
| `splunk-lookup` | CSV and lookup file management |
| `splunk-tag` | Knowledge object tagging |
| `splunk-savedsearch` | Reports and scheduled searches |
| `splunk-alert` | Alert triggering and monitoring |
| `splunk-rest-admin` | REST API configuration access |
| `splunk-security` | Token management and RBAC |
| `splunk-metrics` | Real-time metrics (mstats, mcatalog) |
| `splunk-app` | Application management |
| `splunk-kvstore` | App Key Value Store |

## Quick Start

### 1. Installation

Clone the repository:

```bash
git clone https://github.com/anthropics/splunk-assistant-skills.git
cd splunk-assistant-skills
```

Install dependencies:

```bash
pip install -r .claude/skills/shared/scripts/lib/requirements.txt
```

### 2. Configuration

Set environment variables:

```bash
# JWT Bearer Token (preferred)
export SPLUNK_TOKEN="your-jwt-token"
export SPLUNK_SITE_URL="https://splunk.example.com"

# Or Basic Auth
export SPLUNK_USERNAME="admin"
export SPLUNK_PASSWORD="changeme"
export SPLUNK_SITE_URL="https://splunk.example.com"
```

Or create `.claude/settings.local.json`:

```json
{
  "splunk": {
    "profiles": {
      "production": {
        "url": "https://splunk.example.com",
        "port": 8089,
        "token": "your-jwt-token"
      }
    }
  }
}
```

### 3. Usage

Execute a search:

```bash
python .claude/skills/splunk-search/scripts/search_oneshot.py \
  "index=main | stats count by sourcetype" \
  --earliest -1h
```

List indexes:

```bash
python .claude/skills/splunk-metadata/scripts/list_indexes.py
```

With Claude Code:

```
> Search for errors in the main index from the last hour

Claude will use the splunk-search skill to execute:
index=main error | stats count by host | head 10
```

## Architecture

```
.claude/
├── settings.json              # Team configuration
├── settings.local.json        # Personal credentials (gitignored)
└── skills/
    ├── splunk-assistant/      # Hub/router
    ├── splunk-job/            # Job lifecycle
    ├── splunk-search/         # Query execution
    ├── splunk-export/         # Data extraction
    ├── splunk-metadata/       # Discovery
    ├── splunk-lookup/         # Lookups
    ├── splunk-tag/            # Tags
    ├── splunk-savedsearch/    # Saved searches
    ├── splunk-alert/          # Alerts
    ├── splunk-rest-admin/     # REST admin
    ├── splunk-security/       # Security
    ├── splunk-metrics/        # Metrics
    ├── splunk-app/            # Apps
    ├── splunk-kvstore/        # KV Store
    └── shared/                # Shared library
        ├── scripts/lib/       # Core modules
        └── config/            # Configuration schemas
```

## Search Modes

| Mode | Use Case | Characteristics |
|------|----------|-----------------|
| **Oneshot** | Ad-hoc queries | Results inline, no SID |
| **Normal** | Long searches | Returns SID, poll for results |
| **Blocking** | Simple queries | Waits for completion |
| **Export** | Large extracts | Streaming, checkpoint support |

## Configuration Priority

1. Environment variables (highest)
2. `.claude/settings.local.json` (personal)
3. `.claude/settings.json` (team)
4. Built-in defaults (lowest)

## Testing

Run unit tests:

```bash
pytest .claude/skills/*/tests/ -v --ignore=.claude/skills/*/tests/live_integration
```

Run integration tests (requires Splunk access):

```bash
pytest .claude/skills/*/tests/live_integration/ -v --profile production
```

## Documentation

- [CLAUDE.md](CLAUDE.md) - Comprehensive project documentation
- [CHANGELOG.md](CHANGELOG.md) - Version history
- Each skill has its own `SKILL.md` with detailed usage

## API Reference

### Splunk REST API v2 (Primary)

- Jobs: `POST/GET /services/search/v2/jobs`
- Results: `GET /services/search/v2/jobs/{sid}/results`
- Control: `POST /services/search/v2/jobs/{sid}/control`

### Splunk REST API v1 (Fallback)

- Oneshot: `POST /services/search/jobs/oneshot`
- Saved Searches: `GET/POST /services/saved/searches`
- Indexes: `GET /services/data/indexes`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite
5. Submit a pull request

Follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

## Security

- Never commit credentials
- Use environment variables or settings.local.json
- Rotate tokens regularly
- Prefer Bearer authentication over Basic Auth

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- [Issues](https://github.com/anthropics/splunk-assistant-skills/issues)
- [Discussions](https://github.com/anthropics/splunk-assistant-skills/discussions)
