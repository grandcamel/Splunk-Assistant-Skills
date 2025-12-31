# splunk-savedsearch

CRUD for reports and scheduled searches in Splunk.

## Purpose

Create, read, update, delete saved searches, reports, and scheduled searches.

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
splunk-skill savedsearch list --app search

# Get saved search details
splunk-skill savedsearch get "My Report"

# Create saved search
splunk-skill savedsearch create "My Report" "index=main | stats count" --app search

# Update saved search
splunk-skill savedsearch update "My Report" --search "index=main | stats count by host"

# Run saved search
splunk-skill savedsearch run "My Report" --wait

# Enable scheduling
splunk-skill savedsearch enable "My Report"

# Disable scheduling
splunk-skill savedsearch disable "My Report"

# Delete saved search
splunk-skill savedsearch delete "My Report"
```

## API Endpoints

- `GET/POST /services/saved/searches` - CRUD
- `POST /services/saved/searches/{name}/dispatch` - Run
- `GET /services/saved/searches/{name}/history` - History
