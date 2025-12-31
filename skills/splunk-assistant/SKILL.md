# splunk-assistant

Central hub and router for Splunk Assistant Skills. Implements 3-level progressive disclosure for optimal Splunk interaction.

## Purpose

Routes natural language requests to specialized Splunk skills based on intent. Provides connection verification, authentication validation, and execution strategy recommendations.

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

| Intent | Route To |
|--------|----------|
| Execute SPL query | `splunk-search` |
| Job lifecycle management | `splunk-job` |
| Large data export | `splunk-export` |
| Index/source discovery | `splunk-metadata` |
| Lookup management | `splunk-lookup` |
| Tag operations | `splunk-tag` |
| Saved searches/reports | `splunk-savedsearch` |
| Alert management | `splunk-alert` |
| REST configuration | `splunk-rest-admin` |
| Token/RBAC/ACL | `splunk-security` |
| Metrics (mstats) | `splunk-metrics` |
| App management | `splunk-app` |
| KV Store | `splunk-kvstore` |

## Connection Verification

```bash
# Get server information (verify connection)
splunk-skill admin info --profile production

# Get server health status
splunk-skill admin health --profile production
```

## Examples

### Verify Connection

```bash
splunk-skill admin info
# Output:
# ✓ Connected to splunk.example.com:8089
# ✓ Authentication: Bearer token valid
# ✓ Deployment: Splunk Enterprise 9.1.0
# ✓ User: admin (capabilities: search, admin_all_objects)
```

### Get Server Info

```bash
splunk-skill admin info --output json
# Output: Server version, build, OS, cluster status, etc.
```

### Common CLI Commands

```bash
# Search commands
splunk-skill search oneshot "index=main | head 10"
splunk-skill search normal "index=main | stats count" --wait

# Job management
splunk-skill job list
splunk-skill job status 1703779200.12345

# Metadata discovery
splunk-skill metadata indexes
splunk-skill metadata sourcetypes --index main

# Security
splunk-skill security whoami
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
