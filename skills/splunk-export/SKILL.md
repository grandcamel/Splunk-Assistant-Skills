# splunk-export

High-volume streaming data extraction for Splunk.

## Purpose

Export large result sets (>50,000 rows) efficiently using streaming.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| Export results | - | Read-only |
| Export from job | - | Read-only |
| Estimate size | - | Read-only |

## Triggers

- "export", "download", "extract"
- "stream", "large results", "ETL"
- "backup", "archive"

## Scripts

| Script | CLI Command | Description |
|--------|-------------|-------------|
| `estimate_export_size.py` | `splunk-as export estimate` | Estimate export size |
| `export_from_job.py` | `splunk-as export job` | Export from existing job |
| `export_results.py` | `splunk-as export results` | Export results to file |

## Examples

### Export Results

```bash
# Export to CSV
splunk-as export results 1703779200.12345 --output-file results.csv

# Export to JSON
splunk-as export results 1703779200.12345 --format json --output-file data.json
```

### Export from Existing Job

```bash
# Export results from a completed search job
splunk-as export job 1703779200.12345 --output-file job_results.csv
```

### Estimate Size

```bash
# Preview count before export
splunk-as export estimate "index=main | stats count by host" --earliest -7d
# Output: Estimated 1,234,567 results
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /services/search/v2/jobs/{sid}/results` | Stream results |
| `GET /services/search/v2/jobs/{sid}/events` | Stream raw events |

## Parameters

| Parameter | Description |
|-----------|-------------|
| `count=0` | Return all results (no limit) |
| `output_mode` | csv, json, xml, raw |
| `field_list` | Comma-separated fields |

## Best Practices

1. **Use streaming** for >50K results
2. **Estimate size first** before large exports
3. **Limit fields** to reduce data transfer
4. **Monitor progress** for long-running exports
5. **Compress output** for storage efficiency

## Related Skills

- [splunk-search](../splunk-search/SKILL.md) - Query execution
- [splunk-job](../splunk-job/SKILL.md) - Job management
