# splunk-metrics

Real-time metrics and data point analysis for Splunk.

## Purpose

Query and analyze metrics data using mstats and mcatalog commands.

## Risk Levels

| Operation | Risk | Notes |
|-----------|------|-------|
| List metrics | - | Read-only |
| List metric indexes | - | Read-only |
| Query with mstats | - | Read-only |
| Discover with mcatalog | - | Read-only |

## Triggers

- "metrics", "mstats", "mcatalog"
- "time series", "data points"

## CLI Commands

| Command | Description |
|---------|-------------|
| `metrics mstats` | Execute mstats command |
| `metrics mcatalog` | Query metrics catalog |
| `metrics mpreview` | Preview metrics data |
| `metrics indexes` | List metric indexes |
| `metrics list` | List metric names |

## Examples

```bash
# List metrics
splunk-as metrics list --index metrics

# List metric indexes
splunk-as metrics indexes

# Query with mstats
splunk-as metrics mstats cpu.percent --agg avg --split-by host --span 1h

# Discover metrics with mcatalog
splunk-as metrics mcatalog --index metrics --filter "cpu.*"

# Preview metrics data
splunk-as metrics mpreview --index metrics
```

## SPL Patterns

```spl
| mstats avg(cpu.percent) WHERE index=metrics BY host span=1h
| mcatalog values(metric_name) WHERE index=metrics
| mpreview index=metrics
```
