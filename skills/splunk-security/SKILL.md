# splunk-security

Token management, RBAC, and ACL verification for Splunk.

## Purpose

Manage JWT tokens, check permissions, and configure ACLs on knowledge objects.

## Triggers

- "token", "permission", "ACL"
- "security", "RBAC", "role"
- "access", "capabilities"

## Scripts

| Script | Description |
|--------|-------------|
| `create_token.py` | Create new JWT token |
| `list_tokens.py` | List tokens for user |
| `delete_token.py` | Revoke token |
| `get_capabilities.py` | Get user capabilities |
| `check_permission.py` | Verify access to resource |
| `get_acl.py` | Get ACL for knowledge object |

## Examples

```bash
# Get current user info
splunk-skill security whoami

# List users
splunk-skill security list-users

# List roles
splunk-skill security list-roles

# List tokens
splunk-skill security list-tokens

# Create token
splunk-skill security create-token --audience "my-app" --expires 30d

# Delete token
splunk-skill security delete-token token_123

# Get capabilities
splunk-skill security capabilities --user admin

# Check permission
splunk-skill security check-permission --object saved/searches/MySearch

# Get ACL
splunk-skill security acl saved/searches/MySearch
```

## API Endpoints

- `GET/POST/DELETE /services/authorization/tokens` - Tokens
- `GET/POST /services/data/transforms/lookups/{name}/acl` - ACL
