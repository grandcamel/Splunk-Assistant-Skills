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
| `lookup transforms` | List lookup transforms/definitions |

## Options

| Option | Commands | Description |
|--------|----------|-------------|
| `-a`, `--app` | all | App context (defaults to "search" for most commands) |
| `-o`, `--output` | list, get, transforms | Output format (text, json; get also supports csv) |
| `-c`, `--count` | get | Maximum rows to show |
| `-n`, `--name` | upload | Lookup name (defaults to filename) |
| `-f`, `--force` | delete | Skip confirmation |
| `--output-file` | download | Output file path |

## App Context

The `-a/--app` option specifies the Splunk app context:

- **Optional for listing**: Filter results to a specific app
- **Required for upload**: Specifies where to store the lookup
- **Recommended for get/download/delete**: Ensures you target the correct lookup file

Default behavior varies by command. When multiple apps have lookups with the same name, always specify `--app`.

## Examples

```bash
# List lookups (with output format)
splunk-as lookup list -a search
splunk-as lookup list -a search -o json

# Get lookup contents (with count limit)
splunk-as lookup get users.csv -a search
splunk-as lookup get users.csv -a search -c 100 -o csv

# Upload lookup (with custom name)
splunk-as lookup upload users.csv -a search
splunk-as lookup upload /path/to/data.csv -a search -n custom_lookup

# Download lookup
splunk-as lookup download users.csv --output-file ./users.csv

# Delete lookup (with force flag)
splunk-as lookup delete old_users.csv -a search
splunk-as lookup delete old_users.csv -a search -f

# List lookup transforms/definitions
splunk-as lookup transforms -a search
splunk-as lookup transforms -a search -o json
```

## API Endpoints

- `POST /services/data/lookup-table-files` - Upload
- `GET /services/data/lookup-table-files` - List
- `GET/DELETE /services/data/lookup-table-files/{name}` - Get/Delete
