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

## CLI Commands

| Command | Description |
|---------|-------------|
| `export estimate` | Estimate export size |
| `export job` | Export from existing job |
| `export results` | Export results to file |
| `export stream` | Stream large exports efficiently |

## Options

| Option | Commands | Description |
|--------|----------|-------------|
| `-o`, `--output-file` | job, results, stream | Output file path (required) |
| `-f`, `--format` | job, results, stream | Export format (csv, json, json_rows, xml) |
| `-e`, `--earliest` | estimate, results, stream | Earliest time |
| `-l`, `--latest` | estimate, results, stream | Latest time |
| `-c`, `--count` | job, stream | Maximum results to export |
| `--fields` | results, stream | Comma-separated fields to export |
| `--progress` | results | Show progress |

## Examples

### Export Results

```bash
# Export to CSV (using short flags)
splunk-as export results "index=main | head 1000" -o results.csv

# Export to JSON with specific fields
splunk-as export results "index=main" -o data.json -f json --fields host,status

# Export with progress indicator
splunk-as export results "index=main | stats count by host" -o report.csv --progress
```

### Export from Existing Job

```bash
# Export results from a completed search job
splunk-as export job 1703779200.12345 -o job_results.csv

# Export with count limit
splunk-as export job 1703779200.12345 -o results.csv -c 10000

# Export as JSON array (json_rows format)
splunk-as export job 1703779200.12345 -o data.json -f json_rows
```

### Stream Export

```bash
# Stream large export efficiently
splunk-as export stream "index=main | head 1000000" -o large_results.csv

# Stream with count limit
splunk-as export stream "index=main" -o results.csv -c 50000

# Stream with specific fields
splunk-as export stream "index=main" -o data.json -f json_rows --fields host,status
```

### Estimate Size

```bash
# Preview count before export
splunk-as export estimate "index=main | stats count by host" -e -7d
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
