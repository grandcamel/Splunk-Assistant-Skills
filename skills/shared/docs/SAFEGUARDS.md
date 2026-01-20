# Safeguards and Recovery Procedures

This document defines risk levels, pre-operation checklists, and recovery procedures for Splunk Assistant Skills.

## Risk Level Definitions

| Level | Indicator | Description | User Confirmation |
|-------|-----------|-------------|-------------------|
| Safe | `-` | Read-only operations, no data modification | None required |
| Caution | `Warning` | Modifiable but easily reversible | Optional |
| Warning | `WarningWarning` | Destructive but potentially recoverable | Recommended |
| Danger | `WarningWarningWarning` | **IRREVERSIBLE** data loss | **Required** |

## Pre-Operation Checklists

### Before Any Destructive Operation

- [ ] Confirm the target resource name/ID is correct
- [ ] Verify you're connected to the intended Splunk instance
- [ ] Check if the resource is currently in use
- [ ] Determine if backups exist

### Before Delete Operations

```bash
# List what will be affected
splunk-as <skill> list --app <app>

# Get details of specific resource
splunk-as <skill> get <resource-name>

# Check dependencies (if applicable)
splunk-as search oneshot "| rest /services/<endpoint> | search <resource>"
```

### Before Bulk Operations

- [ ] Test with a single item first
- [ ] Review the full list of affected items
- [ ] Consider time-of-day (avoid production peak hours)
- [ ] Have rollback plan ready

## Recovery Procedures by Resource Type

### Search Jobs (splunk-job)

| Operation | Recovery Method |
|-----------|-----------------|
| Cancel job | Re-run the search |
| Delete job | Results are gone; re-run search if needed |
| Finalize job | Accept partial results or re-run |

**Prevention**: Use `--ttl` to set appropriate time-to-live instead of manual deletion.

### Saved Searches (splunk-savedsearch)

| Operation | Recovery Method |
|-----------|-----------------|
| Update | No version history; restore from backup |
| Delete | Restore from backup or recreate |
| Disable | Re-enable with `splunk-as savedsearch enable` |

**Prevention**: Export before modifying:
```bash
splunk-as savedsearch get "MySearch" --output json > backup_mysearch.json
```

### Lookups (splunk-lookup)

| Operation | Recovery Method |
|-----------|-----------------|
| Upload (overwrite) | Restore from local copy or backup |
| Delete | Restore from backup |

**Prevention**: Always download before upload:
```bash
splunk-as lookup download users.csv --output-file users_backup.csv
splunk-as lookup upload users_new.csv --app search
```

### KV Store (splunk-kvstore)

| Operation | Recovery Method |
|-----------|-----------------|
| Update record | Previous value lost; restore from backup |
| Delete record | Restore from backup |
| Delete collection | **IRREVERSIBLE** - all data lost |

**Prevention**: Export collection before modifications:
```bash
splunk-as search oneshot "| inputlookup my_collection" --output json > backup.json
```

### Apps (splunk-app)

| Operation | Recovery Method |
|-----------|-----------------|
| Disable | Re-enable with `splunk-as app enable` |
| Uninstall | **IRREVERSIBLE** - reinstall from package |

**Prevention**: Keep original package files. Never uninstall without backup.

### Tokens (splunk-security)

| Operation | Recovery Method |
|-----------|-----------------|
| Delete token | Create new token; update all integrations |

**Prevention**: Document all token usages. Use meaningful audience names.

### Alerts (splunk-alert)

| Operation | Recovery Method |
|-----------|-----------------|
| Delete | Recreate from documentation |
| Acknowledge | Alert can re-trigger on next schedule |

**Prevention**: Document alert configurations in version control.

## Confirmation Patterns

### For Warning Operations

```
Warning: This will modify <resource>.
Current value: <current>
New value: <new>
Proceed? [y/N]
```

### For WarningWarning Operations

```
WARNING: This will delete <resource>.
This action may be recoverable from backups only.
Type the resource name to confirm:
```

### For WarningWarningWarning Operations

```
DANGER: This will PERMANENTLY delete <resource>.
This action is IRREVERSIBLE. All data will be lost.
Type "I understand this is irreversible" to confirm:
```

## Dry-Run Guidance

### When to Use Dry-Run

- Bulk operations affecting multiple resources
- First-time execution of automated scripts
- Production environment modifications
- When uncertainty exists about scope

### Dry-Run Patterns

```bash
# Preview what would be affected
splunk-as job list --filter "status=running"  # See before canceling all

# Use search to preview
splunk-as search oneshot "| rest /services/saved/searches | search disabled=0"

# Test SPL syntax first
splunk-as search validate "your complex SPL query"
```

## Emergency Procedures

### Runaway Search Job

```bash
# List all running jobs
splunk-as job list --filter "dispatchState=RUNNING"

# Cancel specific job
splunk-as job cancel <SID>

# Cancel all your jobs (emergency)
splunk-as search oneshot "| rest /services/search/jobs | search dispatchState=RUNNING | fields sid" \
  | xargs -I {} splunk-as job cancel {}
```

### Accidental Token Deletion

1. Immediately create a new token
2. Update all affected integrations
3. Document which integrations were affected
4. Review audit logs for exposure window

### Wrong Lookup Uploaded

```bash
# If you have backup
splunk-as lookup upload backup.csv --app search

# If no backup, check Splunk's backup (if enabled)
# Look in $SPLUNK_HOME/var/lib/splunk/kvstore/backup/
```

### App Causing Issues

```bash
# Disable first, don't uninstall
splunk-as app disable problematic_app

# Restart Splunk if needed (admin only)
# Then investigate before deciding on uninstall
```

## Audit and Logging

### What Gets Logged

| Action | Log Location | Retention |
|--------|--------------|-----------|
| Search execution | `index=_audit action=search` | Per policy |
| Config changes | `index=_internal component=Conf*` | Per policy |
| REST API calls | `index=_internal REST` | Per policy |
| Authentication | `index=_audit action=login` | Per policy |

### Review Before Destructive Actions

```spl
# Who else is using this saved search?
index=_audit action=search savedsearch_name="MySearch"
| stats count by user
| sort -count

# Recent modifications to resource
index=_internal component=ConfReplicationThread
| search name="transforms-lookup/MyLookup"
```

## Best Practices Summary

1. **Always verify the target** - Double-check resource names and environments
2. **Backup before modify** - Export configurations before changes
3. **Start small** - Test with single items before bulk operations
4. **Document changes** - Keep records of what was changed and why
5. **Use dry-run** - Preview operations when available
6. **Off-peak timing** - Schedule destructive operations during low-usage periods
7. **Have rollback plan** - Know how to recover before you execute

---

<!-- PERMISSIONS
permissions:
  cli: splunk-as
  operations:
    # Safe - Read-only operations
    - pattern: "splunk-as search oneshot *"
      risk: safe
    - pattern: "splunk-as search validate *"
      risk: safe
    - pattern: "splunk-as job list *"
      risk: safe
    - pattern: "splunk-as job status *"
      risk: safe
    - pattern: "splunk-as job results *"
      risk: safe
    - pattern: "splunk-as metadata indexes *"
      risk: safe
    - pattern: "splunk-as metadata sources *"
      risk: safe
    - pattern: "splunk-as metadata sourcetypes *"
      risk: safe
    - pattern: "splunk-as savedsearch list *"
      risk: safe
    - pattern: "splunk-as savedsearch get *"
      risk: safe
    - pattern: "splunk-as lookup list *"
      risk: safe
    - pattern: "splunk-as lookup download *"
      risk: safe
    - pattern: "splunk-as app list *"
      risk: safe
    - pattern: "splunk-as app info *"
      risk: safe
    - pattern: "splunk-as security list *"
      risk: safe
    - pattern: "splunk-as metrics *"
      risk: safe
    - pattern: "splunk-as alert list *"
      risk: safe
    - pattern: "splunk-as kvstore list *"
      risk: safe
    - pattern: "splunk-as kvstore get *"
      risk: safe
    - pattern: "splunk-as export *"
      risk: safe

    # Caution - Modifiable but easily reversible
    - pattern: "splunk-as job create *"
      risk: caution
    - pattern: "splunk-as job finalize *"
      risk: caution
    - pattern: "splunk-as job cancel *"
      risk: caution
    - pattern: "splunk-as job touch *"
      risk: caution
    - pattern: "splunk-as savedsearch create *"
      risk: caution
    - pattern: "splunk-as savedsearch update *"
      risk: caution
    - pattern: "splunk-as savedsearch enable *"
      risk: caution
    - pattern: "splunk-as savedsearch disable *"
      risk: caution
    - pattern: "splunk-as lookup upload *"
      risk: caution
    - pattern: "splunk-as tag *"
      risk: caution
    - pattern: "splunk-as app install *"
      risk: caution
    - pattern: "splunk-as app enable *"
      risk: caution
    - pattern: "splunk-as app disable *"
      risk: caution
    - pattern: "splunk-as security create *"
      risk: caution
    - pattern: "splunk-as alert acknowledge *"
      risk: caution
    - pattern: "splunk-as kvstore insert *"
      risk: caution
    - pattern: "splunk-as kvstore update *"
      risk: caution

    # Warning - Destructive but potentially recoverable
    - pattern: "splunk-as job delete *"
      risk: warning
    - pattern: "splunk-as savedsearch delete *"
      risk: warning
    - pattern: "splunk-as lookup delete *"
      risk: warning
    - pattern: "splunk-as security delete *"
      risk: warning
    - pattern: "splunk-as alert delete *"
      risk: warning
    - pattern: "splunk-as kvstore delete *"
      risk: warning

    # Danger - IRREVERSIBLE operations
    - pattern: "splunk-as app uninstall *"
      risk: danger
    - pattern: "splunk-as kvstore drop *"
      risk: danger
-->
