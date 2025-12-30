# Prompt: Generate Environment Setup Script

Use this prompt with Claude to generate a `setup-env.sh` script for your Assistant Skills project.

---

## Prompt Template

```
Create a bash script called `scripts/setup-env.sh` that interactively prompts users to configure environment variables for my project.

## Project Name
[YOUR_PROJECT_NAME]

## Environment Variables

| Variable | Description | Default | Required | Secret |
|----------|-------------|---------|----------|--------|
| [VAR_NAME] | [Description] | [default or empty] | yes/no | yes/no |

## Validation Rules
- [VAR_NAME]: [validation rule, e.g., "must be valid URL", "must be port 1-65535", "must be non-empty"]

## Connection Test (Optional)
To test the connection, make a request to: [endpoint]
- Success: HTTP [status code]
- Auth header: [how to include auth, e.g., "Bearer token" or "Basic auth"]

## Requirements

1. Interactive prompts with color output
2. Show existing values from ~/.env as defaults (mask secrets)
3. Validate input where specified
4. Write variables to ~/.env in KEY="value" format (no export)
5. Add this loader block to ~/.bashrc or ~/.zshrc (detect shell):

```bash
# ============================================================================
# Load Environment Variables from ~/.env
# ============================================================================
if [ -f ~/.env ]; then
    set -a  # Automatically export all variables
    source ~/.env
    set +a  # Disable automatic export
fi
```

6. Backup existing ~/.env before modifying
7. Set chmod 600 on ~/.env for security
8. Offer to test connection before saving (if applicable)
9. Offer to source the config immediately after saving
10. Show masked summary of configured values at the end
```

---

## Example: Splunk Assistant Skills

```
Create a bash script called `scripts/setup-env.sh` that interactively prompts users to configure environment variables for my project.

## Project Name
Splunk Assistant Skills

## Environment Variables

| Variable | Description | Default | Required | Secret |
|----------|-------------|---------|----------|--------|
| SPLUNK_SITE_URL | Splunk server URL | https://localhost | yes | no |
| SPLUNK_MANAGEMENT_PORT | Management API port | 8089 | yes | no |
| SPLUNK_TOKEN | Bearer authentication token | | no* | yes |
| SPLUNK_USERNAME | Basic auth username | admin | no* | no |
| SPLUNK_PASSWORD | Basic auth password | | no* | yes |
| SPLUNK_VERIFY_SSL | Verify SSL certificates | true | no | no |
| SPLUNK_DEFAULT_APP | Default Splunk app | search | no | no |
| SPLUNK_DEFAULT_INDEX | Default search index | main | no | no |
| SPLUNK_PROFILE | Profile name for multi-instance | default | no | no |

*Either SPLUNK_TOKEN or SPLUNK_USERNAME+SPLUNK_PASSWORD required

## Validation Rules
- SPLUNK_SITE_URL: must start with http:// or https://
- SPLUNK_MANAGEMENT_PORT: must be valid port (1-65535)
- SPLUNK_VERIFY_SSL: must be "true" or "false"

## Connection Test
Endpoint: ${SPLUNK_SITE_URL}:${SPLUNK_MANAGEMENT_PORT}/services/server/info
- Success: HTTP 200
- Auth: Bearer token header OR Basic auth
- Skip SSL verify if SPLUNK_VERIFY_SSL=false
```

---

## Example: GitHub Integration Project

```
Create a bash script called `scripts/setup-env.sh` that interactively prompts users to configure environment variables for my project.

## Project Name
GitHub Assistant Skills

## Environment Variables

| Variable | Description | Default | Required | Secret |
|----------|-------------|---------|----------|--------|
| GITHUB_TOKEN | GitHub Personal Access Token | | yes | yes |
| GITHUB_API_URL | GitHub API base URL | https://api.github.com | no | no |
| GITHUB_DEFAULT_ORG | Default organization | | no | no |
| GITHUB_DEFAULT_REPO | Default repository | | no | no |

## Validation Rules
- GITHUB_TOKEN: must be non-empty, should start with "ghp_" or "github_pat_"
- GITHUB_API_URL: must be valid URL

## Connection Test
Endpoint: ${GITHUB_API_URL}/user
- Success: HTTP 200
- Auth: Bearer ${GITHUB_TOKEN}
```

---

## Example: Database Project

```
Create a bash script called `scripts/setup-env.sh` that interactively prompts users to configure environment variables for my project.

## Project Name
Database Assistant Skills

## Environment Variables

| Variable | Description | Default | Required | Secret |
|----------|-------------|---------|----------|--------|
| DB_HOST | Database hostname | localhost | yes | no |
| DB_PORT | Database port | 5432 | yes | no |
| DB_NAME | Database name | | yes | no |
| DB_USERNAME | Database username | postgres | yes | no |
| DB_PASSWORD | Database password | | yes | yes |
| DB_SSL_MODE | SSL mode (disable/require/verify-full) | require | no | no |
| DB_POOL_SIZE | Connection pool size | 10 | no | no |

## Validation Rules
- DB_HOST: must be non-empty
- DB_PORT: must be valid port (1-65535)
- DB_NAME: must be non-empty
- DB_SSL_MODE: must be one of: disable, require, verify-full
- DB_POOL_SIZE: must be positive integer

## Connection Test
Use: pg_isready -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USERNAME} -d ${DB_NAME}
- Success: exit code 0
```

---

## Tips

1. **Group related variables**: If you have auth options (token vs username/password), prompt user to choose one method

2. **Provide context**: Add helpful tips during prompts (e.g., "To create a token, go to Settings > Tokens")

3. **Mask secrets**: When showing existing values for secrets, display only first/last 4 characters

4. **Validate early**: Validate input immediately after each prompt, not at the end

5. **Test connections**: If your service has a health/info endpoint, offer to test before saving

6. **Handle updates**: The script should work for both initial setup and updating existing config
