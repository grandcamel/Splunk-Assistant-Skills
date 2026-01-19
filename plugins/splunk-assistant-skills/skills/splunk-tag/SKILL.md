# splunk-tag

Knowledge object tags and field/value associations for Splunk.

## Purpose

Add, remove, and manage tags associated with field values for easier searching.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| List tags | - | Read-only |
| Search by tag | - | Read-only |
| Add tag | ⚠️ | Easily reversible |
| Remove tag | ⚠️ | Easily reversible |

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
# List all tags
splunk-as tag list

# Add tag to field value
splunk-as tag add production host webserver01

# Remove tag from field value
splunk-as tag remove production host webserver01

# Search by tag
splunk-as tag search production --earliest -1h
```

## SPL Patterns

```spl
tag=web_traffic
tag::src_ip=internal
```
