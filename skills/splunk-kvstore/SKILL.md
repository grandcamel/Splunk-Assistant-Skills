# splunk-kvstore

Interaction with App Key Value Store for persistent metadata.

## Purpose

Create and manage KV store collections and records for persistent data storage.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| List collections | - | Read-only |
| Get record | - | Read-only |
| Query collection | - | Read-only |
| Insert record | ⚠️ | Easily reversible |
| Create collection | ⚠️ | Easily reversible |
| Update record | ⚠️ | Previous value lost |
| Delete record | ⚠️⚠️ | Data loss, may be in backups |
| Delete collection | ⚠️⚠️⚠️ | **IRREVERSIBLE** - all data lost |

## Triggers

- "kvstore", "collection", "key-value"
- "persist", "store"

## CLI Commands

| Command | Description |
|---------|-------------|
| `kvstore list` | List collections in app |
| `kvstore create <name>` | Create KV store collection |
| `kvstore delete <name>` | Delete collection (**IRREVERSIBLE**) |
| `kvstore insert <collection>` | Insert record into collection |
| `kvstore get <collection> <key>` | Get record by _key |
| `kvstore update <collection> <key>` | Update existing record |
| `kvstore delete-record <collection> <key>` | Delete individual record by _key |
| `kvstore query <collection>` | Query with filters |

## Examples

```bash
# Show help
splunk-as kvstore --help

# List collections
splunk-as kvstore list --app search

# Create collection
splunk-as kvstore create my_collection --app search

# Insert record
splunk-as kvstore insert my_collection '{"name": "test", "value": 123}' --app search

# Get record by _key
splunk-as kvstore get my_collection abc123 --app search

# Query collection with filters
splunk-as kvstore query my_collection --filter '{"name": "test"}' --app search

# Update record by _key
splunk-as kvstore update my_collection abc123 '{"name": "updated"}' --app search

# Delete individual record by _key (use delete-record, not delete)
splunk-as kvstore delete-record my_collection abc123 --app search

# Delete collection (IRREVERSIBLE - removes collection and all records)
splunk-as kvstore delete my_collection --app search
```

## Command Terminology

| Command | Target | Description |
|---------|--------|-------------|
| `delete-record` | Single record | Deletes one record by its `_key` |
| `delete` | Collection | Deletes entire collection and all records (**IRREVERSIBLE**) |

## API Endpoints

- `GET/POST/DELETE /services/storage/collections/config` - Collections
- `GET/POST /services/storage/collections/data/{collection}` - Records
- `GET/PUT/DELETE /services/storage/collections/data/{collection}/{key}` - Record

## SPL Patterns

```spl
| inputlookup collection_name
| outputlookup collection_name append=true
```
