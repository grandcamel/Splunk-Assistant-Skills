# splunk-security

Token management, RBAC, and ACL verification for Splunk.

## Purpose

Manage JWT tokens, check permissions, and configure ACLs on knowledge objects.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| Get current user | - | Read-only |
| List users/roles | - | Read-only |
| List tokens | - | Read-only |
| Get capabilities | - | Read-only |
| Check permission | - | Read-only |
| Get ACL | - | Read-only |
| Create token | ⚠️ | Security credential created |
| Delete token | ⚠️⚠️ | **Breaks dependent integrations** |
| Modify ACL | ⚠️⚠️ | Changes access permissions |

## Triggers

- "token", "permission", "ACL"
- "security", "RBAC", "role"
- "access", "capabilities"

## CLI Commands

| Command | Description |
|---------|-------------|
| `security whoami` | Get current user info |
| `security list-users` | List all users |
| `security list-roles` | List all roles |
| `security list-tokens` | List auth tokens |
| `security create-token` | Create auth token |
| `security delete-token` | Delete auth token |
| `security capabilities` | Get user capabilities |
| `security check` | Check if user has capability |
| `security acl` | Get ACL for resource |

## Options

| Option | Commands | Description |
|--------|----------|-------------|
| `-o`, `--output` | whoami, list-users, list-roles, list-tokens, capabilities, acl | Output format (text, json) |
| `-n`, `--name` | create-token | Token name (required) |
| `--audience` | create-token | Token audience (optional) |
| `--expires` | create-token | Expiration time in seconds (optional) |

## Examples

```bash
# Get current user info (with output format)
splunk-as security whoami
splunk-as security whoami -o json

# List users
splunk-as security list-users
splunk-as security list-users -o json

# List roles
splunk-as security list-roles
splunk-as security list-roles -o json

# List tokens
splunk-as security list-tokens
splunk-as security list-tokens -o json

# Create token (--name required, --audience and --expires optional)
splunk-as security create-token -n "my-app-token"
splunk-as security create-token -n "my-app-token" --audience "my-app" --expires 2592000

# Delete token
splunk-as security delete-token token_123

# Get capabilities (current user)
splunk-as security capabilities
splunk-as security capabilities -o json

# Check if user has a specific capability (positional argument)
splunk-as security check search

# Get ACL (full REST path starting with /)
splunk-as security acl /servicesNS/nobody/search/saved/searches/MySearch
splunk-as security acl /servicesNS/nobody/search/saved/searches/MySearch -o json
```

## API Endpoints

- `GET/POST/DELETE /services/authorization/tokens` - Tokens
- `GET/POST /services/data/transforms/lookups/{name}/acl` - ACL
