# CLI Reference

The `splunk-as` command provides a unified CLI for all Splunk Assistant Skills operations.

## Installation

```bash
# Install in development mode
pip install -e .

# Verify installation
splunk-as --version
```

## General Usage

```bash
# Get help
splunk-as --help
splunk-as search --help
```

## Command Groups

| Group | Description |
|-------|-------------|
| `search` | SPL query execution (oneshot/normal/blocking) |
| `job` | Search job lifecycle management |
| `export` | Data export and extraction |
| `metadata` | Index, source, sourcetype discovery |
| `lookup` | CSV and lookup file management |
| `kvstore` | App Key Value Store operations |
| `savedsearch` | Saved search and report management |
| `alert` | Alert management and monitoring |
| `app` | Application management |
| `security` | Token management and RBAC |
| `admin` | Server administration and REST API |
| `tag` | Knowledge object tagging |
| `metrics` | Real-time metrics operations |

## Search Commands

```bash
# Oneshot search (immediate results, no job created)
splunk-as search oneshot "index=main | head 10"

# Normal search (creates job, optional wait)
splunk-as search normal "index=main | stats count" --wait

# Blocking search (waits for completion)
splunk-as search blocking "index=main | head 10" --timeout 60
```

## Job Commands

```bash
# List jobs
splunk-as job list

# Get job status
splunk-as job status 1703779200.12345

# Cancel job
splunk-as job cancel 1703779200.12345
```

## Metadata Commands

```bash
# List indexes
splunk-as metadata indexes

# List sourcetypes for an index
splunk-as metadata sourcetypes --index main
```

## Export Commands

```bash
# Export job results
splunk-as export results 1703779200.12345 --output-file results.csv
```

## Administration Commands

```bash
# Get server info
splunk-as admin info

# Get current user
splunk-as security whoami
```

---

# Search Modes

## Oneshot Mode (Ad-hoc)

Best for: Quick queries, results < 50,000 rows

```python
# Results returned inline, no job created
response = client.post(
    '/services/search/jobs/oneshot',
    data={
        'search': 'index=main | head 100',
        'output_mode': 'json',
        'earliest_time': '-1h',
        'latest_time': 'now',
    },
)
results = response['results']
```

## Normal Mode (Async)

Best for: Long-running searches, monitoring progress

```python
# Create job (returns SID immediately)
response = client.post(
    '/services/search/v2/jobs',
    data={'search': spl, 'exec_mode': 'normal'},
)
sid = response['sid']

# Poll for completion
from job_poller import poll_job_status
job = poll_job_status(client, sid, timeout=300)

# Get results
results = client.get(f'/services/search/v2/jobs/{sid}/results')
```

## Blocking Mode (Sync)

Best for: Simple queries, scripted automation

```python
# Waits for completion
response = client.post(
    '/services/search/v2/jobs',
    data={'search': spl, 'exec_mode': 'blocking'},
    timeout=300,
)
sid = response['entry'][0]['name']
results = client.get(f'/services/search/v2/jobs/{sid}/results')
```

## Export Mode (Streaming)

Best for: Large data extraction, ETL pipelines

```python
# Stream results to file
for chunk in client.stream_results(
    f'/services/search/v2/jobs/{sid}/results',
    params={'output_mode': 'csv', 'count': 0},
):
    output_file.write(chunk)
```

---

# Job Lifecycle

## State Flow

```
QUEUED → PARSING → RUNNING → FINALIZING → DONE
                                        → FAILED
                 → PAUSED (on pause)
```

## Job Control Actions

```python
from job_poller import cancel_job, pause_job, unpause_job, finalize_job, set_job_ttl

# Cancel running job
cancel_job(client, sid)

# Pause/resume
pause_job(client, sid)
unpause_job(client, sid)

# Finalize (return current results)
finalize_job(client, sid)

# Extend TTL
set_job_ttl(client, sid, ttl=3600)
```

## Polling Best Practices

```python
from job_poller import poll_job_status

# With progress callback
def on_progress(progress):
    print(f"Progress: {progress.progress_percent:.0f}%")

job = poll_job_status(
    client, sid,
    timeout=300,
    poll_interval=1.0,
    progress_callback=on_progress,
)
```
