# splunk-job

Search job lifecycle orchestration for Splunk.

## Purpose

Manage the complete lifecycle of Splunk search jobs including creation, monitoring, control actions (pause/cancel/finalize), and cleanup.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| Get job status | - | Read-only |
| List jobs | - | Read-only |
| Create job | - | Easily reversible via cancel |
| Pause/unpause job | ⚠️ | Can be undone |
| Finalize job | ⚠️ | Returns partial results |
| Cancel job | ⚠️ | Stops execution |
| Delete job | ⚠️⚠️ | Removes job and results |

## Triggers

- "job", "search job", "SID"
- "status", "progress", "state"
- "cancel", "pause", "unpause", "finalize"
- "list jobs", "delete job"

## Job States (dispatchState)

```
QUEUED → PARSING → RUNNING → FINALIZING → DONE
                                        → FAILED
                 → PAUSED (on pause action)
```

| State | Description |
|-------|-------------|
| QUEUED | Job waiting in queue |
| PARSING | SPL being parsed |
| RUNNING | Search executing |
| FINALIZING | Results being finalized |
| DONE | Completed successfully |
| FAILED | Error occurred |
| PAUSED | Paused by user |

## CLI Commands

| Command | Description |
|---------|-------------|
| `job create` | Create search job, return SID |
| `job status` | Get dispatchState, progress, stats |
| `job poll` | Wait for job completion with timeout |
| `job cancel` | Issue /control/cancel action |
| `job pause` | Issue /control/pause action |
| `job unpause` | Issue /control/unpause action |
| `job finalize` | Issue /control/finalize action |
| `job ttl` | Set job time-to-live |
| `job touch` | Touch a job to extend its TTL |
| `job list` | List all search jobs for user |
| `job delete` | Remove job from dispatch directory |

## Examples

### Create and Monitor Job

```bash
# Create job
splunk-as job create "index=main | stats count by sourcetype" --earliest -1h
# Output: Job created: 1703779200.12345

# Check status
splunk-as job status 1703779200.12345
# Output: State: RUNNING, Progress: 45%, Events: 12345

# Wait for completion
splunk-as job poll 1703779200.12345 --timeout 300
# Output: Job completed: DONE, Results: 42
```

### Job Control

```bash
# Pause running job
splunk-as job pause 1703779200.12345

# Resume paused job
splunk-as job unpause 1703779200.12345

# Cancel job
splunk-as job cancel 1703779200.12345

# Finalize (stop and return current results)
splunk-as job finalize 1703779200.12345
```

### Job Management

```bash
# List all jobs
splunk-as job list
# Output: Table of active jobs with status

# Extend TTL (positional arg: SID TTL_VALUE)
splunk-as job ttl 1703779200.12345 3600

# Delete job
splunk-as job delete 1703779200.12345
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/services/search/v2/jobs` | POST | Create job |
| `/services/search/v2/jobs/{sid}` | GET | Get job status |
| `/services/search/v2/jobs/{sid}/control` | POST | Control actions |
| `/services/search/jobs` | GET | List jobs |
| `/services/search/jobs/{sid}` | DELETE | Delete job |

## Control Actions

```python
# Available actions for /control endpoint
actions = ['cancel', 'pause', 'unpause', 'finalize', 'touch', 'setttl', 'enablepreview', 'disablepreview']

# POST /services/search/v2/jobs/{sid}/control
# data={'action': 'cancel'}
```

## Job Properties

| Property | Description |
|----------|-------------|
| `sid` | Search job ID |
| `dispatchState` | Current state |
| `doneProgress` | Completion 0.0-1.0 |
| `eventCount` | Events scanned |
| `resultCount` | Results produced |
| `scanCount` | Buckets scanned |
| `runDuration` | Execution time |
| `ttl` | Time to live |
| `isFailed` | Failure flag |
| `isPaused` | Pause flag |

## Best Practices

1. **Always set time bounds** in the search query
2. **Use appropriate timeout** for poll_job.py
3. **Cancel jobs** when results are no longer needed
4. **Monitor progress** for long-running searches
5. **Extend TTL** for jobs you need to keep

## Related Skills

- [splunk-search](../splunk-search/SKILL.md) - Query execution
- [splunk-export](../splunk-export/SKILL.md) - Result extraction
