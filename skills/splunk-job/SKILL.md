# splunk-job

Search job lifecycle orchestration for Splunk.

## Purpose

Manage the complete lifecycle of Splunk search jobs including creation, monitoring, control actions (pause/cancel/finalize), and cleanup.

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

## Scripts

| Script | Description |
|--------|-------------|
| `create_job.py` | Create search job, return SID |
| `get_job_status.py` | Get dispatchState, progress, stats |
| `poll_job.py` | Wait for job completion with timeout |
| `cancel_job.py` | Issue /control/cancel action |
| `pause_job.py` | Issue /control/pause action |
| `unpause_job.py` | Issue /control/unpause action |
| `finalize_job.py` | Issue /control/finalize action |
| `set_job_ttl.py` | Extend job time-to-live |
| `list_jobs.py` | List all search jobs for user |
| `delete_job.py` | Remove job from dispatch directory |

## Examples

### Create and Monitor Job

```bash
# Create job
python create_job.py "index=main | stats count by sourcetype" --earliest -1h
# Output: Job created: 1703779200.12345

# Check status
python get_job_status.py 1703779200.12345
# Output: State: RUNNING, Progress: 45%, Events: 12345

# Wait for completion
python poll_job.py 1703779200.12345 --timeout 300
# Output: Job completed: DONE, Results: 42
```

### Job Control

```bash
# Pause running job
python pause_job.py 1703779200.12345

# Resume paused job
python unpause_job.py 1703779200.12345

# Cancel job
python cancel_job.py 1703779200.12345

# Finalize (stop and return current results)
python finalize_job.py 1703779200.12345
```

### Job Management

```bash
# List all jobs
python list_jobs.py
# Output: Table of active jobs with status

# Extend TTL
python set_job_ttl.py 1703779200.12345 --ttl 3600

# Delete job
python delete_job.py 1703779200.12345
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
