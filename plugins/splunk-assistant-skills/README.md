# Splunk Assistant Skills

Natural language Splunk automation for Claude Code - search, job management, exports, and administration.

## Installation

```bash
claude plugin install grandcamel/Splunk-Assistant-Skills
```

## Quick Start

After installation, run the setup wizard:

```
/assistant-skills-setup
```

This configures:
- Python virtual environment with dependencies
- Splunk connection (URL, port, authentication)
- Shell integration for `claude-as` command

## Skills

| Skill | Description |
|-------|-------------|
| splunk-assistant | Hub router with progressive disclosure |
| splunk-search | SPL query execution (oneshot/normal/blocking) |
| splunk-job | Search job lifecycle management |
| splunk-export | High-volume data extraction |
| splunk-metadata | Index, source, sourcetype discovery |
| splunk-lookup | CSV and lookup file management |
| splunk-savedsearch | Reports and scheduled searches |
| splunk-alert | Alert triggering and monitoring |
| splunk-app | Application management |
| splunk-kvstore | App Key Value Store operations |
| splunk-security | Token management and RBAC |
| splunk-rest-admin | REST API configuration |
| splunk-metrics | Real-time metrics (mstats, mcatalog) |
| splunk-tag | Knowledge object tagging |

## Usage Examples

```
# Search
"Run a search for errors in the last hour"
"Show me the top 10 sourcetypes by event count"

# Job Management
"List my running search jobs"
"Cancel job 1703779200.12345"

# Metadata
"What indexes are available?"
"Show sourcetypes in the main index"

# Administration
"Get server health status"
"List all users and their roles"
```

## Authentication

### Bearer Token (Recommended)

1. Create token in Splunk Web: Settings > Tokens
2. Run `/assistant-skills-setup` and select Bearer Token auth

### Basic Auth

For on-prem environments:
1. Run `/assistant-skills-setup` and select Basic Auth
2. Enter username and password

## Requirements

- Python 3.8+
- Splunk Enterprise or Splunk Cloud with REST API access
- Network access to Splunk management port (default: 8089)

## Documentation

Full documentation: [CLAUDE.md](https://github.com/grandcamel/Splunk-Assistant-Skills/blob/main/CLAUDE.md)

## License

MIT
