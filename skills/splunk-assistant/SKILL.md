# splunk-assistant

Central hub and router for Splunk Assistant Skills. Routes requests to 13 specialized skills using 3-level progressive disclosure.

## Purpose

Routes natural language requests to specialized Splunk skills based on intent. Provides connection verification, authentication validation, and execution strategy recommendations.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| Get server info | - | Read-only |
| Verify connection | - | Read-only |
| Route to skill | - | Navigation only |

## Triggers

- Any Splunk-related request
- "splunk", "search", "query", "SPL"
- Connection/authentication issues
- General Splunk questions

## Progressive Disclosure

### Level 1: Essential Connection & Identification

- Verify Search Head connection on management port 8089 via HTTPS
- Validate JWT Bearer token or Basic Auth credentials
- Detect deployment type (Cloud vs on-prem)
- Route to appropriate specialized skill

### Level 2: Execution Mode Strategy

| Mode | Use Case | Characteristics |
|------|----------|-----------------|
| Oneshot | Ad-hoc queries | Results inline, no SID, minimal disk I/O |
| Normal | Long searches | Returns SID, poll for results, progress tracking |
| Blocking | Simple queries | Waits for completion, synchronous |
| Export | Large extracts | Streaming, checkpoint support, ETL |

### Level 3: Advanced Optimization & Resource Governance

- **Time Modifiers**: Always enforce `earliest_time` and `latest_time`
- **Field Reduction**: Insert `fields` command to limit data transfer
- **Resource Cleanup**: Issue `/control/cancel` after results consumed
- **Error Handling**: Use `strict=true` for clear errors vs incomplete data

## Skill Routing

| Intent | Skill | CLI Command |
|--------|-------|-------------|
| Execute SPL query | `splunk-search` | `search` |
| Job lifecycle management | `splunk-job` | `job` |
| Large data export | `splunk-export` | `export` |
| Index/source discovery | `splunk-metadata` | `metadata` |
| Lookup management | `splunk-lookup` | `lookup` |
| Tag operations | `splunk-tag` | `tag` |
| Saved searches/reports | `splunk-savedsearch` | `savedsearch` |
| Alert management | `splunk-alert` | `alert` |
| REST/Server administration | `splunk-rest-admin` | `admin` |
| Token/RBAC/ACL | `splunk-security` | `security` |
| Metrics (mstats) | `splunk-metrics` | `metrics` |
| App management | `splunk-app` | `app` |
| KV Store | `splunk-kvstore` | `kvstore` |

## Connection Verification

```bash
# Get server information (verify connection)
splunk-as admin info --profile production

# Get server health status
splunk-as admin health --profile production
```

## Examples

### Verify Connection

```bash
splunk-as admin info
# Output:
# ✓ Connected to splunk.example.com:8089
# ✓ Authentication: Bearer token valid
# ✓ Deployment: Splunk Enterprise 9.1.0
# ✓ User: admin (capabilities: search, admin_all_objects)
```

### Get Server Info

```bash
splunk-as admin info --output json
# Output: Server version, build, OS, cluster status, etc.
```

### Common CLI Commands

```bash
# Search commands
splunk-as search oneshot "index=main | head 10"
splunk-as search normal "index=main | stats count" --wait

# Job management
splunk-as job list
splunk-as job status 1703779200.12345

# Metadata discovery
splunk-as metadata indexes
splunk-as metadata sourcetypes --index main

# Security
splunk-as security whoami
```

## Best Practices

1. **Always include time bounds** - Prevent full index scans
2. **Use field extraction** - Limit data transfer
3. **Choose appropriate mode** - Oneshot for ad-hoc, Export for ETL
4. **Clean up resources** - Cancel jobs when done
5. **Handle errors gracefully** - Use the error hierarchy

## Related Skills

- [splunk-job](../splunk-job/SKILL.md) - Job lifecycle
- [splunk-search](../splunk-search/SKILL.md) - Query execution
- [splunk-security](../splunk-security/SKILL.md) - Authentication
