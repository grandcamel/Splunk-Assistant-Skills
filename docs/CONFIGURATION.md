# Configuration Guide

This document covers configuration, authentication, and credentials management for Splunk Assistant Skills.

## Configuration Priority

Configuration values are resolved in this order (highest to lowest priority):

1. **Environment variables** (highest)
2. **`.claude/settings.local.json`** (personal, gitignored)
3. **Built-in defaults** (lowest)

## Environment Variables

```bash
# Authentication (choose one method)
export SPLUNK_TOKEN="your-jwt-token"           # Bearer token (preferred)
export SPLUNK_USERNAME="admin"                  # Basic Auth
export SPLUNK_PASSWORD="changeme"               # Basic Auth

# Connection
export SPLUNK_SITE_URL="https://splunk.example.com"
export SPLUNK_MANAGEMENT_PORT="8089"
export SPLUNK_VERIFY_SSL="true"

# Defaults
export SPLUNK_DEFAULT_APP="search"
export SPLUNK_DEFAULT_INDEX="main"
```

## Local Settings File

Create `.claude/settings.local.json` for personal credentials (this file is gitignored):

```json
{
  "splunk": {
    "site_url": "https://splunk.example.com",
    "management_port": 8089,
    "token": "your-jwt-token",
    "verify_ssl": true,
    "default_app": "search",
    "default_index": "main"
  }
}
```

## Assistant Skills Setup

If installed via the Claude Code plugin system, use the universal setup wizard:

```bash
/assistant-skills-setup
```

This configures:
- Shared Python venv at `~/.assistant-skills-venv/`
- Required dependencies from `requirements.txt`
- Environment variables (prompts for Splunk credentials)
- `claude-as` shell function for running Claude with dependencies

After setup, use `claude-as` instead of `claude`:
```bash
claude-as  # Runs Claude with Assistant Skills venv activated
```

---

# Authentication

## JWT Bearer Token (Preferred)

Bearer tokens are the recommended authentication method for production use.

### Creating a Token

1. Open Splunk Web
2. Navigate to **Settings > Tokens**
3. Click **New Token**
4. Configure token settings (audience, expiration)
5. Copy the generated token

### Configuring the Token

```bash
export SPLUNK_TOKEN="eyJraWQiOi..."
```

Or in `.claude/settings.local.json`:

```json
{
  "splunk": {
    "token": "eyJraWQiOi..."
  }
}
```

## Basic Auth (Legacy)

For on-prem environments or development:

```bash
export SPLUNK_USERNAME="admin"
export SPLUNK_PASSWORD="changeme"
```

### Auto-Detection

The client automatically detects which authentication method to use:
- If `SPLUNK_TOKEN` is set → Bearer authentication
- Otherwise → Basic authentication with username/password

---

# Credentials Security

## Best Practices

### DO

- Use environment variables for sensitive data
- Store tokens in `.claude/settings.local.json` (gitignored)
- Rotate tokens regularly
- Use minimal permissions for tokens
- Enable SSL verification in production

### DON'T

- Commit tokens or passwords to git
- Log sensitive values
- Share `settings.local.json`
- Use Basic Auth in production (prefer Bearer)
- Disable SSL verification in production

## Schema Validation

Configuration follows `config.schema.json`. Key sections:

```json
{
  "splunk": {
    "api": {},           // API behavior
    "search_defaults": {} // Search parameters
  }
}
```

## Adding New Settings

1. Update `skills/shared/config/config.schema.json`
2. Update `.claude/settings.example.json`
3. Update `config_manager.py` if needed
4. Document in this file
