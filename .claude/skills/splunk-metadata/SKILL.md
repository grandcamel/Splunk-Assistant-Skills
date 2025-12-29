# splunk-metadata

Query index, source, and sourcetype configurations for Splunk.

## Purpose

Discover and explore metadata about indexes, sources, sourcetypes, and fields.

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
python list_indexes.py

# Get index details
python get_index_info.py main

# List sourcetypes
python list_sourcetypes.py --index main

# Field summary
python get_field_summary.py --index main --sourcetype access_combined
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
