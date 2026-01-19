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

## Scripts

| Script | Description |
|--------|-------------|
| `create_collection.py` | Create KV store collection |
| `delete_collection.py` | Delete collection |
| `list_collections.py` | List collections in app |
| `insert_record.py` | Insert record into collection |
| `get_record.py` | Get record by _key |
| `update_record.py` | Update existing record |
| `delete_record.py` | Delete record |
| `query_collection.py` | Query with filters |

## Examples

```bash
# List collections
splunk-as kvstore list --app search

# Create collection
splunk-as kvstore create my_collection --app search

# Insert record
splunk-as kvstore insert my_collection '{"name": "test", "value": 123}'

# Get record
splunk-as kvstore get my_collection abc123

# Query collection
splunk-as kvstore query my_collection --filter '{"name": "test"}'

# Update record
splunk-as kvstore update my_collection abc123 '{"name": "updated"}'

# Delete record
splunk-as kvstore delete-record my_collection abc123

# Delete collection
splunk-as kvstore delete my_collection --app search
```

## API Endpoints

- `GET/POST/DELETE /services/storage/collections/config` - Collections
- `GET/POST /services/storage/collections/data/{collection}` - Records
- `GET/PUT/DELETE /services/storage/collections/data/{collection}/{key}` - Record

## SPL Patterns

```spl
| inputlookup collection_name
| outputlookup collection_name append=true
```
