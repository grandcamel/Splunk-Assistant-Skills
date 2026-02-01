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
| `tag add` | Add tag to field value |
| `tag remove` | Remove tag from field value |
| `tag list` | List all tags |
| `tag search` | Search using tag= syntax |

## Options

| Option | Commands | Description |
|--------|----------|-------------|
| `-a`, `--app` | list, add, remove | App context (defaults to "search") |
| `-o`, `--output` | list, search | Output format (text, json) |
| `-i`, `--index` | search | Filter by index |
| `-e`, `--earliest` | search | Earliest time (defaults to -24h) |

## Examples

```bash
# List all tags (with short flags)
splunk-as tag list
splunk-as tag list -a search -o json

# Add tag to field value (format: field::value tag_name)
splunk-as tag add host::webserver01 production
splunk-as tag add host::webserver01 production -a my_app

# Remove tag from field value
splunk-as tag remove host::webserver01 production
splunk-as tag remove host::webserver01 production -a my_app

# Search by tag (with short flags)
splunk-as tag search production
splunk-as tag search production -e -1h -i main
splunk-as tag search production -e -1h -o json
```

## SPL Patterns

```spl
tag=web_traffic
tag::src_ip=internal
```
