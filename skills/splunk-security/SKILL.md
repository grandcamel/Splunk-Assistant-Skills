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

## Examples

```bash
# Get current user info
splunk-as security whoami

# List users
splunk-as security list-users

# List roles
splunk-as security list-roles

# List tokens
splunk-as security list-tokens

# Create token
splunk-as security create-token --audience "my-app" --expires 30d

# Delete token
splunk-as security delete-token token_123

# Get capabilities
splunk-as security capabilities --user admin

# Check permission
splunk-as security check --object saved/searches/MySearch

# Get ACL
splunk-as security acl saved/searches/MySearch
```

## API Endpoints

- `GET/POST/DELETE /services/authorization/tokens` - Tokens
- `GET/POST /services/data/transforms/lookups/{name}/acl` - ACL
