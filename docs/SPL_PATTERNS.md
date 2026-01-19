# SPL Query Patterns

This document covers SPL (Search Processing Language) best practices and the progressive disclosure system.

## Query Best Practices

### Always Include Time Bounds

```spl
# Good - explicit time bounds
index=main earliest=-1h latest=now | head 100

# Bad - scans all time
index=main | head 100
```

### Field Extraction Optimization

```spl
# Good - limit fields early
index=main | fields host, status, uri | head 1000

# Bad - returns all fields
index=main | head 1000
```

## Common Patterns

### Statistics and Aggregation

```spl
index=main | stats count by status | sort -count
```

### Time-Based Analysis

```spl
index=main | timechart span=1h count by sourcetype
```

### Subsearch

```spl
index=main [search index=alerts | fields src_ip | head 1000]
```

### Transaction

```spl
index=main | transaction host maxspan=5m | stats avg(duration)
```

### Metrics (mstats)

```spl
| mstats avg(cpu.percent) WHERE index=metrics BY host span=1h
```

### Metadata Discovery

```spl
| metadata type=sourcetypes index=main | table sourcetype, totalCount
```

### REST API Access

```spl
| rest /services/server/info | table splunk_server, version, build
```

### Lookup Enrichment

```spl
index=main | lookup users.csv username OUTPUT department
```

---

# Progressive Disclosure (3 Levels)

The Splunk Assistant Skills use a three-level progressive disclosure system to provide the right level of detail at the right time.

## Level 1: Essential Connection

Focus on establishing a working connection:

- Verify Search Head connection on port 8089
- Validate authentication (Bearer/Basic)
- Detect deployment type (Cloud vs on-prem)
- Route to appropriate skill

## Level 2: Execution Mode Strategy

Select the right search mode for the task:

| Mode | Use Case |
|------|----------|
| **Oneshot** | Ad-hoc queries (minimal disk I/O) |
| **Export** | ETL/large transfers (streaming) |
| **Normal + Polling** | Long searches with progress |
| **Blocking** | Simple, fast queries |

## Level 3: Advanced Optimization

Apply performance optimizations:

| Technique | Description |
|-----------|-------------|
| **Time Bounds** | Enforce `earliest_time`/`latest_time` |
| **Field Reduction** | Add `fields` command early |
| **Resource Cleanup** | Cancel jobs after use |
| **Error Handling** | Use `strict=true` mode |

---

# Error Handling Strategy

## 4-Layer Approach

1. **Validation Layer**: Input validation before API calls
2. **HTTP Layer**: Retry on transient failures (429, 5xx)
3. **API Layer**: Parse Splunk error responses
4. **Application Layer**: User-friendly error messages

## Exception Hierarchy

```
SplunkError (base)
├── AuthenticationError (401)
├── AuthorizationError (403)
├── ValidationError (400)
├── NotFoundError (404)
├── RateLimitError (429)
├── SearchQuotaError (503)
├── JobFailedError
└── ServerError (5xx)
```

## Using the Error Decorator

```python
from error_handler import handle_errors

@handle_errors
def main():
    client = get_splunk_client()
    # Operations that might fail
    result = client.post('/search/jobs/oneshot', data={'search': spl})
```
