# splunk-kvstore

Interaction with App Key Value Store for persistent metadata.

## Purpose

Create and manage KV store collections and records for persistent data storage.

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
splunk-skill kvstore list --app search

# Create collection
splunk-skill kvstore create my_collection --app search

# Insert record
splunk-skill kvstore insert my_collection '{"name": "test", "value": 123}'

# Get record
splunk-skill kvstore get my_collection abc123

# Query collection
splunk-skill kvstore query my_collection --filter '{"name": "test"}'

# Update record
splunk-skill kvstore update my_collection abc123 '{"name": "updated"}'

# Delete record
splunk-skill kvstore delete-record my_collection abc123

# Delete collection
splunk-skill kvstore delete my_collection --app search
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
