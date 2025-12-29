# splunk-rest-admin

Programmatic access to internal configurations via REST command.

## Purpose

Query and manage Splunk server configurations, users, roles, and system info.

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
python get_server_info.py
python rest_get.py /services/authentication/users
python list_users.py
```

## SPL Patterns

```spl
| rest /services/server/info
| rest /services/authentication/users
| rest /services/admin/conf-times
```
