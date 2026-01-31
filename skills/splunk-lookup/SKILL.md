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
| Delete lookup | ⚠️⚠️ | May be recoverable from backup |

## Triggers

- "lookup", "CSV", "upload"
- "lookup table", "enrichment"

## CLI Commands

| Command | Description |
|---------|-------------|
| `lookup list` | List lookup files |
| `lookup get` | Get contents of a lookup file |
| `lookup upload` | Upload CSV lookup file |
| `lookup download` | Download lookup file |
| `lookup delete` | Remove lookup file |

## Help Reference

```bash
splunk-as lookup --help
splunk-as lookup upload --help
```

## App Context

The `--app` option specifies the Splunk app context:

- **Optional for listing**: Filter results to a specific app
- **Required for upload**: Specifies where to store the lookup
- **Recommended for get/download/delete**: Ensures you target the correct lookup file

Default behavior varies by command. When multiple apps have lookups with the same name, always specify `--app`.

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
