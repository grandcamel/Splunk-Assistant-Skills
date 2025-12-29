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
python list_savedsearches.py --app search
python get_savedsearch.py "My Report"
python run_savedsearch.py "My Report" --wait
```

## API Endpoints

- `GET/POST /services/saved/searches` - CRUD
- `POST /services/saved/searches/{name}/dispatch` - Run
- `GET /services/saved/searches/{name}/history` - History
