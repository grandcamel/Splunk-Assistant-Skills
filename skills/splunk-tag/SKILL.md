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

## CLI Commands

| Command | Description |
|---------|-------------|
| `splunk-as tag add` | Add tag to field value |
| `splunk-as tag remove` | Remove tag from field value |
| `splunk-as tag list` | List all tags |
| `splunk-as tag search` | Search using tag= syntax |

## Examples

```bash
# List all tags
splunk-as tag list
splunk-as tag list --output json

# Add tag to field value (format: "field::value" tag_name)
splunk-as tag add "host::webserver01" production
splunk-as tag add "host::webserver01" production --app my_app

# Remove tag from field value
splunk-as tag remove "host::webserver01" production
splunk-as tag remove "host::webserver01" production --app my_app

# Search by tag
splunk-as tag search production --earliest -1h
splunk-as tag search production --earliest -1h --output json
```

## SPL Patterns

```spl
tag=web_traffic
tag::src_ip=internal
```
