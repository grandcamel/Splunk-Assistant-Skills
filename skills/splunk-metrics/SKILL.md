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

## Options

| Option | Commands | Description |
|--------|----------|-------------|
| `-i`, `--index` | mstats, mcatalog, mpreview, list | Metrics index |
| `-o`, `--output` | mcatalog, mpreview | Output format (text, json) |
| `-m`, `--metric` | mcatalog | Filter by metric name pattern |
| `-f`, `--filter` | mpreview | Filter expression (e.g., host=server1) |
| `-c`, `--count` | mpreview | Number of data points |
| `--agg` | mstats | Aggregation function |
| `--split-by` | mstats | Split by field |
| `--span` | mstats | Time span |

## Examples

```bash
# List metrics
splunk-as metrics list -i metrics

# List metric indexes
splunk-as metrics indexes

# Query with mstats
splunk-as metrics mstats cpu.percent --agg avg --split-by host --span 1h

# Discover metrics with mcatalog (use -m/--metric for filtering)
splunk-as metrics mcatalog -i metrics -m "cpu.*"
splunk-as metrics mcatalog -i metrics -o json

# Preview metrics data (requires metric_name positional arg)
splunk-as metrics mpreview cpu.percent -i metrics
splunk-as metrics mpreview cpu.percent -i metrics -f "host=server1" -c 50
```

## SPL Patterns

```spl
| mstats avg(cpu.percent) WHERE index=metrics BY host span=1h
| mcatalog values(metric_name) WHERE index=metrics
| mpreview index=metrics
```
