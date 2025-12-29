# splunk-tag

Knowledge object tags and field/value associations for Splunk.

## Purpose

Add, remove, and manage tags associated with field values for easier searching.

## Triggers

- "tag", "label", "classify"
- "tag field", "add tag"

## Scripts

| Script | Description |
|--------|-------------|
| `add_tag.py` | Add tag to field value |
| `remove_tag.py` | Remove tag from field value |
| `list_tags.py` | List all tags |
| `search_by_tag.py` | Search using tag= syntax |

## Examples

```bash
python add_tag.py --field host --value webserver01 --tag production
python list_tags.py
python search_by_tag.py production
```

## SPL Patterns

```spl
tag=web_traffic
tag::src_ip=internal
```
