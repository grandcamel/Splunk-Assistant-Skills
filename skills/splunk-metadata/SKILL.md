# splunk-metadata

Query index, source, and sourcetype configurations for Splunk.

## Purpose

Discover and explore metadata about indexes, sources, sourcetypes, and fields.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| List indexes | - | Read-only |
| Get index info | - | Read-only |
| List sources | - | Read-only |
| List sourcetypes | - | Read-only |
| Get field summary | - | Read-only |
| Metadata search | - | Read-only |

## Triggers

- "metadata", "index", "source", "sourcetype"
- "fields", "discovery", "catalog"

## CLI Commands

| Command | Description |
|---------|-------------|
| `metadata indexes` | List available indexes |
| `metadata index-info` | Index size, event count, time range |
| `metadata sources` | Unique sources per index |
| `metadata sourcetypes` | Sourcetypes in use |
| `metadata search` | Execute `\| metadata` search (supports hosts, sources, sourcetypes) |
| `metadata fields` | Field summary for index/sourcetype |

## Examples

```bash
# List all indexes
splunk-as metadata indexes

# Get index details
splunk-as metadata index-info main

# List sourcetypes
splunk-as metadata sourcetypes --index main

# List sources
splunk-as metadata sources --index main

# Field summary (positional argument for index)
splunk-as metadata fields main --sourcetype access_combined

# Metadata search (positional argument for type: hosts, sources, sourcetypes)
splunk-as metadata search sourcetypes --index main
splunk-as metadata search hosts --index main
splunk-as metadata search sources --index main
```

## SPL Patterns

```spl
# Metadata command
| metadata type=sourcetypes index=main

# Metasearch
| metasearch index=* sourcetype=access_combined

# Field summary
| fieldsummary maxvals=100
```

## Related Skills

- [splunk-search](../splunk-search/SKILL.md) - Query execution
