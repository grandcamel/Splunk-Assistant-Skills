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
python list_tokens.py
python get_capabilities.py --user admin
python check_permission.py --object saved/searches/MySearch
```

## API Endpoints

- `GET/POST/DELETE /services/authorization/tokens` - Tokens
- `GET/POST /services/data/transforms/lookups/{name}/acl` - ACL
