# Splunk Assistant Skills Quick Reference

One-page cheat sheet for common operations.

## CLI Command Quick Reference

### Search Commands

```bash
# Oneshot (ad-hoc, inline results)
splunk-as search oneshot "index=main | head 10"
splunk-as search oneshot "index=main | stats count" --earliest -1h --latest now

# Normal (async, returns SID)
splunk-as search normal "index=main | stats count" --wait
splunk-as search normal "index=main | stats count"  # Returns SID only

# Blocking (sync, waits)
splunk-as search blocking "index=main | head 10" --timeout 60

# Get results from job
splunk-as search results 1703779200.12345 --count 100

# Validate SPL
splunk-as search validate "index=main | stats count"
```

### Job Management

```bash
splunk-as job list                           # List all jobs
splunk-as job status 1703779200.12345        # Get job status
splunk-as job poll 1703779200.12345          # Wait for completion
splunk-as job cancel 1703779200.12345        # Cancel job
splunk-as job pause 1703779200.12345         # Pause job
splunk-as job unpause 1703779200.12345       # Resume job
splunk-as job delete 1703779200.12345        # Delete job
```

### Metadata Discovery

```bash
splunk-as metadata indexes                    # List indexes
splunk-as metadata sourcetypes --index main   # List sourcetypes
splunk-as metadata sources --index main       # List sources
splunk-as metadata fields --index main        # Field summary
```

### Export

```bash
splunk-as export results SID --output-file data.csv
splunk-as export results SID --format json --output-file data.json
splunk-as export estimate "index=main" --earliest -7d
```

### Saved Searches

```bash
splunk-as savedsearch list --app search
splunk-as savedsearch get "My Report"
splunk-as savedsearch create "Name" "SPL query" --app search
splunk-as savedsearch run "My Report" --wait
splunk-as savedsearch enable "My Report"
splunk-as savedsearch delete "My Report"
```

### Lookups

```bash
splunk-as lookup list --app search
splunk-as lookup download users.csv --output-file ./backup.csv
splunk-as lookup upload users.csv --app search
splunk-as lookup delete users.csv --app search
```

### KV Store

```bash
splunk-as kvstore list --app search
splunk-as kvstore create my_collection --app search
splunk-as kvstore insert my_collection '{"key": "value"}'
splunk-as kvstore query my_collection --filter '{"status": "active"}'
splunk-as kvstore delete my_collection --app search
```

### Alerts

```bash
splunk-as alert list --app search
splunk-as alert triggered --severity 4
splunk-as alert get alert_12345
splunk-as alert acknowledge alert_12345
```

### Security

```bash
splunk-as security whoami
splunk-as security list-tokens
splunk-as security create-token --audience "my-app"
splunk-as security capabilities --user admin
```

### Administration

```bash
splunk-as admin info
splunk-as admin health
splunk-as admin list-users
splunk-as admin rest-get /services/server/info
```

## Common SPL Patterns

### Basic Searches

```spl
# Simple search with time
index=main earliest=-1h | head 100

# Filter by field
index=main status>=400 | stats count by status

# Multiple indexes
index=main OR index=web | stats count by index
```

### Statistics

```spl
# Count by field
index=main | stats count by sourcetype | sort -count

# Multiple aggregations
index=main | stats count, avg(response_time), max(response_time) by host

# Top values
index=main | top 10 uri

# Rare values
index=main | rare status
```

### Time Analysis

```spl
# Time chart
index=main | timechart span=1h count by sourcetype

# Time-based comparison
index=main earliest=-1d@d latest=@d | stats count as today
| appendcols [search index=main earliest=-2d@d latest=-1d@d | stats count as yesterday]

# Bucketing
index=main | bucket _time span=5m | stats count by _time
```

### Field Extraction

```spl
# Limit fields (performance)
index=main | fields host, status, uri | table host status uri

# Field summary
index=main | fieldsummary maxvals=100

# Rex extraction
index=main | rex field=_raw "user=(?<username>\w+)"
```

### Subsearch

```spl
# Basic subsearch
index=main [search index=alerts | fields src_ip | head 100]

# Subsearch with format
index=main [search index=users | fields user_id | format]
```

### Lookup Enrichment

```spl
# Lookup
index=main | lookup users.csv username OUTPUT department

# Automatic lookup (if configured)
index=main | table username, department

# Outputlookup
index=main | stats count by host | outputlookup host_counts.csv
```

### Metrics

```spl
# mstats
| mstats avg(cpu.percent) WHERE index=metrics BY host span=1h

# mcatalog
| mcatalog values(metric_name) WHERE index=metrics

# mpreview
| mpreview index=metrics
```

### Metadata Commands

```spl
# Metadata search
| metadata type=sourcetypes index=main

# Metasearch
| metasearch index=* sourcetype=access_combined

# REST API
| rest /services/server/info
```

## Time Modifier Syntax

| Modifier | Description | Example |
|----------|-------------|---------|
| `-1h` | 1 hour ago | `earliest=-1h` |
| `-1d` | 1 day ago | `earliest=-1d` |
| `-1w` | 1 week ago | `earliest=-1w` |
| `-1mon` | 1 month ago | `earliest=-1mon` |
| `@d` | Snap to day | `earliest=-1d@d` |
| `@h` | Snap to hour | `earliest=-1h@h` |
| `now` | Current time | `latest=now` |

### Common Time Ranges

```
earliest=-1h latest=now          # Last hour
earliest=-24h latest=now         # Last 24 hours
earliest=-7d@d latest=@d         # Last 7 complete days
earliest=-1d@d latest=@d         # Yesterday (complete)
earliest=@d latest=now           # Today so far
earliest=-1mon@mon latest=@mon   # Last complete month
```

## API Endpoint Shortcuts

| Operation | Endpoint |
|-----------|----------|
| Oneshot search | `POST /services/search/jobs/oneshot` |
| Create job | `POST /services/search/v2/jobs` |
| Job status | `GET /services/search/v2/jobs/{sid}` |
| Job results | `GET /services/search/v2/jobs/{sid}/results` |
| Job control | `POST /services/search/v2/jobs/{sid}/control` |
| Saved searches | `GET/POST /services/saved/searches` |
| Lookups | `GET/POST /services/data/lookup-table-files` |
| KV Store | `GET/POST /services/storage/collections/data/{coll}` |
| Tokens | `GET/POST /services/authorization/tokens` |
| Server info | `GET /services/server/info` |
| Indexes | `GET /services/data/indexes` |
| Apps | `GET/POST /services/apps/local` |
| Alerts | `GET /services/alerts/fired_alerts` |

## Error Code Meanings

| HTTP Code | Meaning | Common Cause |
|-----------|---------|--------------|
| 400 | Bad Request | Invalid SPL syntax |
| 401 | Unauthorized | Invalid/expired token |
| 403 | Forbidden | Missing capability |
| 404 | Not Found | Wrong SID or resource name |
| 409 | Conflict | Resource already exists |
| 429 | Too Many Requests | Rate limited |
| 500 | Server Error | Splunk internal error |
| 503 | Service Unavailable | Search quota exceeded |

## Search Modes Comparison

| Mode | Best For | Returns SID | Wait | Max Results |
|------|----------|-------------|------|-------------|
| Oneshot | Ad-hoc, <50K rows | No | Inline | 50,000 |
| Normal | Long-running | Yes | Async | No limit |
| Blocking | Simple, fast | Yes | Sync | No limit |
| Export | Large data, ETL | Yes | Stream | No limit |

## Environment Variables

```bash
# Authentication
SPLUNK_TOKEN=<jwt-token>           # Bearer token (preferred)
SPLUNK_USERNAME=<user>             # Basic auth
SPLUNK_PASSWORD=<pass>             # Basic auth

# Connection
SPLUNK_SITE_URL=https://splunk.example.com
SPLUNK_MANAGEMENT_PORT=8089
SPLUNK_VERIFY_SSL=true

# Defaults
SPLUNK_DEFAULT_APP=search
SPLUNK_DEFAULT_INDEX=main
```
