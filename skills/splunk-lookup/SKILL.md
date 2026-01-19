# splunk-lookup

CSV and lookup file management for Splunk.

## Purpose

Upload, download, and manage CSV lookup files and lookup definitions.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| List lookups | - | Read-only |
| Get lookup info | - | Read-only |
| Download lookup | - | Read-only |
| Upload lookup | ⚠️ | Creates new or overwrites |
| Create lookup definition | ⚠️ | Can be undone |
| Delete lookup | ⚠️⚠️ | May be recoverable from backup |

## Triggers

- "lookup", "CSV", "upload"
- "lookup table", "enrichment"

## Scripts

| Script | Description |
|--------|-------------|
| `upload_lookup.py` | Upload CSV lookup file |
| `download_lookup.py` | Download lookup file |
| `list_lookups.py` | List lookup files in app |
| `delete_lookup.py` | Remove lookup file |
| `create_lookup_definition.py` | Create lookup-table stanza |

## Examples

```bash
# List lookups
splunk-as lookup list --app search

# Get lookup info
splunk-as lookup get users.csv --app search

# Upload lookup
splunk-as lookup upload users.csv --app search

# Download lookup
splunk-as lookup download users.csv --output-file ./users.csv

# Delete lookup
splunk-as lookup delete users.csv --app search
```

## API Endpoints

- `POST /services/data/lookup-table-files` - Upload
- `GET /services/data/lookup-table-files` - List
- `GET/DELETE /services/data/lookup-table-files/{name}` - Get/Delete
