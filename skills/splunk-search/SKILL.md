# splunk-search

SPL query execution in multiple modes for Splunk.

## Purpose

Execute SPL (Search Processing Language) queries using various execution modes:
oneshot (inline results), normal (async with polling), and blocking (sync wait).

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| Execute search (read) | - | Read-only query |
| Get results | - | Read-only |
| Validate SPL | - | Read-only |
| Execute search (write) | ⚠️⚠️ | SPL with `| outputlookup` or `| collect` modifies data |

## Triggers

- "search", "SPL", "query", "find"
- "oneshot", "blocking", "async"
- "execute", "run search"

## Search Modes

| Mode | Use Case | Returns SID | Wait for Results |
|------|----------|-------------|------------------|
| Oneshot | Ad-hoc queries < 50K rows | No | Inline |
| Normal | Long-running searches | Yes | Async (poll) |
| Blocking | Simple queries | Yes | Sync (waits) |

## CLI Commands

| Command | Description |
|---------|-------------|
| `search oneshot` | Execute oneshot search (results inline) |
| `search normal` | Execute normal search (returns SID) |
| `search blocking` | Execute blocking search (waits) |
| `search results` | Get results from completed job |
| `search preview` | Get partial results during search |
| `search validate` | Validate SPL syntax |

## Examples

### Oneshot Search (Recommended for Ad-hoc)

```bash
# Simple search
splunk-as search oneshot "index=main | stats count by sourcetype"

# With time range
splunk-as search oneshot "index=main | head 100" --earliest -1h --latest now

# Output as JSON
splunk-as search oneshot "index=main | top host" --output json

# With count limit and specific fields
splunk-as search oneshot "index=main" --count 100 --fields host,status

# Output to file
splunk-as search oneshot "index=main | head 1000" --output-file results.csv

# Using short flags (-e earliest, -l latest, -c count, -f fields, -o output-file)
splunk-as search oneshot "index=main" -e -1h -l now -c 100 -f host,status -o results.csv
```

### Normal Search (Async)

```bash
# Create job and poll
splunk-as search normal "index=main | stats count" --wait

# Create job only (returns SID)
splunk-as search normal "index=main | stats count"
# Then use: splunk-as search results <SID>
```

### Blocking Search (Sync)

```bash
# Wait for completion and return results
splunk-as search blocking "index=main | head 10" --timeout 60
```

### Get Results

```bash
# From completed job
splunk-as search results 1703779200.12345

# With pagination
splunk-as search results 1703779200.12345 --count 100 --offset 0

# Specific fields only
splunk-as search results 1703779200.12345 --fields host,status,uri
```

### Validate SPL

```bash
# Validate SPL syntax
splunk-as search validate "index=main | stats count"

# Validate with suggestions for fixes
splunk-as search validate "index=main | stats count" --suggestions
```

## API Endpoints

| Endpoint | Mode | Description |
|----------|------|-------------|
| `POST /services/search/jobs/oneshot` | Oneshot | Inline results |
| `POST /services/search/v2/jobs` | Normal | Create async job |
| `POST /services/search/v2/jobs` + `exec_mode=blocking` | Blocking | Sync wait |
| `GET /services/search/v2/jobs/{sid}/results` | - | Get results |
| `GET /services/search/v2/jobs/{sid}/results_preview` | - | Get preview |

## Request Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `search` | SPL query | Required |
| `earliest_time` | Start time | -24h |
| `latest_time` | End time | now |
| `exec_mode` | normal/blocking | normal |
| `max_count` | Max results | 50000 |
| `output_mode` | json/csv/xml | json |

## Best Practices

1. **Always include time bounds** - Prevents full index scans
2. **Use oneshot for ad-hoc** - Minimal resource usage
3. **Add fields command** - Reduce data transfer
4. **Validate SPL first** - Catch syntax errors early
5. **Handle pagination** - Use count/offset for large results

## SPL Quick Reference

```spl
# Basic search with time
index=main earliest=-1h | head 100

# Statistics
index=main | stats count by status | sort -count

# Time chart
index=main | timechart span=1h count by sourcetype

# Field extraction
index=main | fields host, status, uri | table host status uri

# Filtering
index=main status>=400 | stats count by status

# Subsearch
index=main [search index=alerts | fields src_ip | head 100]
```

## Related Skills

- [splunk-job](../splunk-job/SKILL.md) - Job lifecycle
- [splunk-export](../splunk-export/SKILL.md) - Large exports
- [splunk-metadata](../splunk-metadata/SKILL.md) - Field discovery
