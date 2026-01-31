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

## CLI Commands

| Command | Description |
|---------|-------------|
| `admin info` | Get server information |
| `admin status` | Get server status |
| `admin health` | Get server health |
| `admin list-users` | List all users |
| `admin list-roles` | List all roles |
| `admin rest-get` | Make GET request to REST endpoint |
| `admin rest-post` | Make POST request to REST endpoint |

## REST Options

| Option | Description |
|--------|-------------|
| `-d`, `--data` | JSON data payload for POST requests |

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

# REST GET request - users
splunk-as admin rest-get /services/authentication/users

# REST GET request - server info
splunk-as admin rest-get /services/server/info

# REST GET request - apps
splunk-as admin rest-get /services/apps/local

# REST POST request
splunk-as admin rest-post /services/saved/searches -d '{"name": "test"}'
```

## SPL Patterns

```spl
| rest /services/server/info
| rest /services/authentication/users
| rest /services/admin/conf-times
```
