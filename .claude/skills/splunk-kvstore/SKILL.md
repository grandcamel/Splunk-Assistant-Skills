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
python list_collections.py --app search
python insert_record.py my_collection '{"name": "test", "value": 123}'
python query_collection.py my_collection --filter '{"name": "test"}'
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
