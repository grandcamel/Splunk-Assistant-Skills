# splunk-savedsearch

CRUD for reports and scheduled searches in Splunk.

## Purpose

Create, read, update, delete saved searches, reports, and scheduled searches.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| List saved searches | - | Read-only |
| Get saved search | - | Read-only |
| Run saved search | - | Read-only execution |
| Create saved search | ⚠️ | Can be deleted |
| Update saved search | ⚠️ | Previous version lost |
| Enable/disable schedule | ⚠️ | Easily reversible |
| Delete saved search | ⚠️⚠️ | May be recoverable from backup |

## Triggers

- "saved search", "report", "schedule"
- "scheduled search", "alert"

## CLI Commands

Commands provided by the `splunk-as` package (`pip install splunk-as`):

| Command | Description |
|---------|-------------|
| `savedsearch list` | List saved searches in app |
| `savedsearch get` | Get saved search details |
| `savedsearch create` | Create saved search/report |
| `savedsearch update` | Modify saved search |
| `savedsearch run` | Execute saved search on-demand |
| `savedsearch history` | Get saved search execution history |
| `savedsearch enable` | Enable scheduled execution |
| `savedsearch disable` | Disable scheduling |
| `savedsearch delete` | Delete saved search |

## Examples

```bash
# List saved searches
splunk-as savedsearch list --app search

# Get saved search details
splunk-as savedsearch get "My Report"

# Create saved search (use --name and --search options)
splunk-as savedsearch create --name "My Report" --search "index=main | stats count" --app search

# Update saved search
splunk-as savedsearch update "My Report" --search "index=main | stats count by host"

# Run saved search (--wait/--no-wait controls blocking)
splunk-as savedsearch run "My Report" --wait
splunk-as savedsearch run "My Report" --no-wait

# Get execution history (default shows 10 entries)
splunk-as savedsearch history "My Report"
splunk-as savedsearch history "My Report" -c 20

# Enable scheduling
splunk-as savedsearch enable "My Report"

# Disable scheduling
splunk-as savedsearch disable "My Report"

# Delete saved search
splunk-as savedsearch delete "My Report"
```

## API Endpoints

- `GET/POST /services/saved/searches` - CRUD
- `POST /services/saved/searches/{name}/dispatch` - Run
- `GET /services/saved/searches/{name}/history` - History
