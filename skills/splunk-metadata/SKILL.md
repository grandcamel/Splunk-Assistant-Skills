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

## Scripts

| Script | Description |
|--------|-------------|
| `list_indexes.py` | List available indexes |
| `get_index_info.py` | Index size, event count, time range |
| `list_sources.py` | Unique sources per index |
| `list_sourcetypes.py` | Sourcetypes in use |
| `metadata_search.py` | Execute `\| metadata` search |
| `get_field_summary.py` | Field summary for index/sourcetype |

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

# Field summary
splunk-as metadata fields --index main --sourcetype access_combined

# Metadata search
splunk-as metadata search --type sourcetypes --index main
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
