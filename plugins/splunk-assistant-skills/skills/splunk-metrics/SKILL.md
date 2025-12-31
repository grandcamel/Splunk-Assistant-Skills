# splunk-metrics

Real-time metrics and data point analysis for Splunk.

## Purpose

Query and analyze metrics data using mstats and mcatalog commands.

## Triggers

- "metrics", "mstats", "mcatalog"
- "time series", "data points"

## Scripts

| Script | Description |
|--------|-------------|
| `mstats.py` | Execute mstats command |
| `mcatalog.py` | Query metrics catalog |
| `list_metric_indexes.py` | List metric indexes |
| `list_metrics.py` | List metric names |

## Examples

```bash
# List metrics
splunk-skill metrics list --index metrics

# List metric indexes
splunk-skill metrics indexes

# Query with mstats
splunk-skill metrics mstats cpu.percent --agg avg --by host --span 1h

# Discover metrics with mcatalog
splunk-skill metrics mcatalog --index metrics --filter "cpu.*"
```

## SPL Patterns

```spl
| mstats avg(cpu.percent) WHERE index=metrics BY host span=1h
| mcatalog values(metric_name) WHERE index=metrics
| mpreview index=metrics
```
