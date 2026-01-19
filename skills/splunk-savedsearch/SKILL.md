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

## Scripts

| Script | Description |
|--------|-------------|
| `create_savedsearch.py` | Create saved search/report |
| `get_savedsearch.py` | Get saved search details |
| `update_savedsearch.py` | Modify saved search |
| `delete_savedsearch.py` | Delete saved search |
| `list_savedsearches.py` | List saved searches in app |
| `run_savedsearch.py` | Execute saved search on-demand |
| `enable_schedule.py` | Enable scheduled execution |
| `disable_schedule.py` | Disable scheduling |

## Examples

```bash
# List saved searches
splunk-as savedsearch list --app search

# Get saved search details
splunk-as savedsearch get "My Report"

# Create saved search
splunk-as savedsearch create "My Report" "index=main | stats count" --app search

# Update saved search
splunk-as savedsearch update "My Report" --search "index=main | stats count by host"

# Run saved search
splunk-as savedsearch run "My Report" --wait

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
