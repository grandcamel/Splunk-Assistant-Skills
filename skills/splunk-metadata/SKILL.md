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

## Options

| Option | Commands | Description |
|--------|----------|-------------|
| `-f`, `--filter` | indexes | Filter indexes by name pattern |
| `-o`, `--output` | indexes, sources, sourcetypes, search, fields | Output format (text, json) |
| `-i`, `--index` | sources, sourcetypes, search | Filter by index |
| `-e`, `--earliest` | search, fields | Earliest time |
| `-s`, `--sourcetype` | fields | Filter by sourcetype |

## Examples

```bash
# List all indexes (with filter and output options)
splunk-as metadata indexes
splunk-as metadata indexes -f "main*" -o json

# Get index details
splunk-as metadata index-info main

# List sourcetypes (with output format)
splunk-as metadata sourcetypes -i main
splunk-as metadata sourcetypes -i main -o json

# List sources
splunk-as metadata sources -i main
splunk-as metadata sources -i main -o json

# Field summary (with earliest time)
splunk-as metadata fields main -s access_combined
splunk-as metadata fields main -s access_combined -e -24h -o json

# Metadata search (with time range)
splunk-as metadata search sourcetypes -i main
splunk-as metadata search hosts -i main -e -7d
splunk-as metadata search sources -i main -o json
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
