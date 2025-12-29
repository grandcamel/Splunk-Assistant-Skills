# splunk-lookup

CSV and lookup file management for Splunk.

## Purpose

Upload, download, and manage CSV lookup files and lookup definitions.

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
python upload_lookup.py users.csv --app search
python download_lookup.py users.csv --output ./users.csv
python list_lookups.py --app search
```

## API Endpoints

- `POST /services/data/lookup-table-files` - Upload
- `GET /services/data/lookup-table-files` - List
- `GET/DELETE /services/data/lookup-table-files/{name}` - Get/Delete
