# splunk-export

High-volume streaming data extraction for Splunk.

## Purpose

Export large result sets (>50,000 rows) efficiently using streaming.
Supports checkpoint-based resume for reliability during long exports.

## Triggers

- "export", "download", "extract"
- "stream", "large results", "ETL"
- "backup", "archive"

## Scripts

| Script | Description |
|--------|-------------|
| `export_results.py` | Stream results to file (CSV/JSON/XML) |
| `export_raw.py` | Export raw events |
| `export_with_checkpoint.py` | Resume-capable export |
| `estimate_export_size.py` | Preview result count |

## Examples

### Basic Export

```bash
# Export to CSV
splunk-skill export results 1703779200.12345 --output-file results.csv

# Export to JSON
splunk-skill export results 1703779200.12345 --format json --output-file data.json

# Export raw events
splunk-skill export raw 1703779200.12345 --output-file events.json
```

### Large Export with Checkpoints

```bash
# Start export with checkpoint file
splunk-skill export checkpoint "index=main" --output large_export.csv --checkpoint export.ckpt

# Resume interrupted export
splunk-skill export checkpoint --resume export.ckpt
```

### Estimate Size

```bash
# Preview count before export
splunk-skill export estimate "index=main | stats count by host" --earliest -7d
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
2. **Enable checkpoints** for large exports
3. **Limit fields** to reduce data transfer
4. **Monitor progress** for long-running exports
5. **Compress output** for storage efficiency

## Related Skills

- [splunk-search](../splunk-search/SKILL.md) - Query execution
- [splunk-job](../splunk-job/SKILL.md) - Job management
