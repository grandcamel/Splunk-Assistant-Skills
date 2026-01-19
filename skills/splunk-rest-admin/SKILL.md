# splunk-rest-admin

Programmatic access to internal configurations via REST command.

## Purpose

Query and manage Splunk server configurations, users, roles, and system info.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| REST GET request | - | Read-only |
| Get server info | - | Read-only |
| List users/roles | - | Read-only |
| REST POST request | ⚠️⚠️ | May modify server config |

## Triggers

- "rest", "admin", "config"
- "server", "settings", "info"

## Scripts

| Script | Description |
|--------|-------------|
| `rest_get.py` | GET any REST endpoint |
| `rest_post.py` | POST to REST endpoint |
| `get_server_info.py` | Server version, build, features |
| `list_users.py` | List Splunk users |
| `list_roles.py` | List Splunk roles |

## Examples

```bash
# Get server info
splunk-as admin info

# Get server status
splunk-as admin status

# Get server health
splunk-as admin health

# List users
splunk-as admin list-users

# List roles
splunk-as admin list-roles

# REST GET request
splunk-as admin rest-get /services/authentication/users

# REST POST request
splunk-as admin rest-post /services/saved/searches -d '{"name": "test"}'
```

## SPL Patterns

```spl
| rest /services/server/info
| rest /services/authentication/users
| rest /services/admin/conf-times
```
