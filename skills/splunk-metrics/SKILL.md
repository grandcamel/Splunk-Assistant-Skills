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
python mstats.py "avg(cpu.percent)" --index metrics --by host
python mcatalog.py --index metrics
python list_metrics.py --index metrics
```

## SPL Patterns

```spl
| mstats avg(cpu.percent) WHERE index=metrics BY host span=1h
| mcatalog values(metric_name) WHERE index=metrics
| mpreview index=metrics
```
